import time
import pandas as pd
import logging
import scipy.signal as ss
import matplotlib.pyplot as plt
import numpy as np
from .exceptions import NoSignatures
from math import ceil
from scipy.ndimage.filters import maximum_filter
from follzam import TABLE_NAMES
from follzam import SIGNALTYPES
NFFT = 2 ** 12
INC = NFFT // 16
logger = logging.getLogger(__name__)

# https://stackoverflow.com/questions/51042870/wrong-spectrogram-when-using-scipy-signal-spectrogram?noredirect=1&lq=1


class SignalProcessor(object):
    """
        Extensible class for signature generation. The base class houses the common functions, like normalizing,
            windowing, spectrogram or periodogram generation, which are used by the subsequent classes.
            The two primary functions which are to be consistently overwritten are the 'Match' and 'compute signature'.
    """

    def __init__(self, audio_array, sample_freq, window_size=5, songinfo={}):
        """
            start up the base class, setting the base attributes
        :param audio_array: numpy array of audio. can be of entire song or just a snippet
        :param sample_freq: the sampling rate. Usually 44100 but possible others
        :param window_size: size of window for periodograms
        :param songinfo: song level information for database loading
        """
        self.songinfo = songinfo
        self.audio_array = audio_array
        self.sample_freq = sample_freq
        self.window_size = window_size
        self.periodograms = []
        self.signature = []
        self.signature = None
        self.spectrogram = None
        self.windows = []
        self.method = ''
        assert isinstance(self.window_size, (int, float))
        assert self.window_size > 0
        self.window_centers = list(range(
            self.window_size // 2, ceil(len(self.audio_array) // self.sample_freq) - self.window_size // 2))
        self.signature_info = {'time_index': self.window_centers}

    def compute_periodogram(self, **kwargs):
        for window in self.windows:
            f, pxx = ss.periodogram(window, fs=self.sample_freq, nfft=NFFT, **kwargs)
            self.periodograms.append((f, pxx))

    def compute_spectrogram(self):
        """
            sompute the spectrogram using scipy.signal.spectrogram
        :param audio_array:
        :return:
        """
        f, t, sxx = ss.spectrogram(self.audio_array, fs=self.sample_freq, window='hann', nfft=NFFT, nperseg=NFFT,
                                   noverlap=NFFT * .5)
        sxx = 10*np.log10(sxx)  # decibels
        sxx[np.where(np.isnan(sxx) | np.isinf(sxx))] = 0  # if somehow the sxx was negative, we put the value to 0
        self.spectrogram = f, t, sxx
        return self.spectrogram

    def plot_spectrogram(self):
        """
            Plot out the spectrogram for the audio
        :return:
        """
        f, t, sxx = self.compute_spectrogram()
        plt.pcolormesh(t, f, sxx)
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time (sec)')
        plt.show()

    def compute_windows(self):
        """
            take full initialized song and cut it up into a bunch of windows of given size
        :return:
        """
        for window_index in self.window_centers:
            window = self.audio_array[(window_index - self.window_size // 2) * self.sample_freq:
                                      (window_index + self.window_size // 2) * self.sample_freq]
            self.windows.append(window)

    def compute_signature(self):
        raise NotImplementedError

    def load_signature(self, dbh):
        """
            load the current signature
        :param dbh: database connector object
        :return:
        """
        song_id = dbh.get_song_id(**self.songinfo)
        sig_type_id = dbh.get_signature_id_by_name(self.method)

        logger.info("Begin Signature loading for %s" % self.songinfo)
        df = pd.DataFrame(self.signature,columns=['time_index','frequency','signature'])
        df['method_id'] = sig_type_id
        df['song_id'] = song_id

        df.to_sql(TABLE_NAMES.SIGNATURE,
                  con=dbh.cur,
                  if_exists='append',
                  index=False,
                  method='multi')

    def match(self, dbh):
        raise NotImplementedError

    def load_match_attempt(self, dbh):
        method_id = dbh.get_signature_id_by_name(self.method)
        dbh.cur.execute('INSERT INTO {} (method_id) VALUES (%s)'.format(TABLE_NAMES.MATCH_ATTEMPT), method_id)
        attempt_id = dbh.cur.execute('SELECT max(id) FROM {};'.format(TABLE_NAMES.MATCH_ATTEMPT)).fetchone()[0]
        logger.info('Loading Match Attempt to Database {}'.format(attempt_id))
        df = pd.DataFrame(self.signature, columns=['time_index', 'frequency', 'signature'])
        df['match_id'] = attempt_id
        df[['signature', 'frequency', 'match_id']].drop_duplicates().to_sql(
            TABLE_NAMES.SIGNATURE_MATCH, con=dbh.cur, if_exists='append', index=False, method='multi')
        return attempt_id


class SignalProcessorSpectrogram(SignalProcessor):
    """
        Spectrogram implementation of signature, based on Wang et al. (2003)

        From spectrogram, we find the peaks in the data using a 2dimensional maximum filter.
        From Peaks, we find near neighbors

    """

    N_STEPS_IN_SECOND = 21  # approximate number of time steps per second in the spectrogram
    EXP = tuple([2**i, 2**(i+1)] for i in range(int(np.log2(NFFT))))
    TIME_NET_WINDOW = N_STEPS_IN_SECOND*5  # time propagation of net
    FREQ_NET_WINDOW = 30  # frequency propagation of net
    MIN_POWER = 10 # minimum power for a peak in decibels
    LOOK_FORWARD_WINDOW_START = N_STEPS_IN_SECOND  # how far ahead of the current time do we want to begin our peak net
    MIN_PROBABILITY_FOR_MATCH = .1  # minimum certainty threshold

    def __init__(self, audio_array, sample_freq, **kwargs):
        super().__init__(audio_array=audio_array,
                         sample_freq=sample_freq,
                         **kwargs)
        self.method = SIGNALTYPES.SPECTROGRAM
        self.signature_info = {}

    def compute_signature(self):
        """
            compute signature by identifying the peaks in 2 dimensions, propagate a window forward in time of
                nearby frequencies, and for each adjacent peak in this window, create a hash based on the two
                frequencies and time distance
        :return:
        """
        logger.info("Begin compute signature")
        f, t, sxx = self.compute_spectrogram()  # spectrogram from scipy.signal
        logger.info("Begin compute peaks")
        constellation = self.get_peaks(sxx, False)  # sparse matrix of 0s and 1s
        logger.info("Iterating through peaks and computing signature for following peaks")

        # corresponding with the hashing portion of the Wang paper, we will compute a signature
        # for each identified peak
        signature = []

        for i in range(sxx.shape[1] - self.LOOK_FORWARD_WINDOW_START):  # iterate over time dimension
            cpeaks = np.where(constellation[:, i])[0]  # subset to get the current peaks

            # for all the peaks that were found at the current time
            for freq in cpeaks:
                # get all the peaks in the forward window
                freq_offset, time_offset = np.where(
                    constellation[(freq - self.FREQ_NET_WINDOW):
                                  (freq + self.FREQ_NET_WINDOW),
                                  i + self.LOOK_FORWARD_WINDOW_START:
                                  i + self.LOOK_FORWARD_WINDOW_START + self.TIME_NET_WINDOW]
                )
                # iterate through all the following peaks and compute a hash
                for peak_freq, peak_time_offset in zip(
                        *(freq - self.FREQ_NET_WINDOW + freq_offset, time_offset + self.LOOK_FORWARD_WINDOW_START)):
                    c_sig = freq * 1000000 + peak_freq * 1000 + peak_time_offset  # integer hash
                    if c_sig == 0:
                        continue
                    signature.append((i, freq, c_sig))

        if len(signature) == 0:
            logger.error("No signatures found for {}".format(str(self.songinfo)))
            raise NoSignatures
        self.signature = signature

    def _get_peaks_deprecated(self, sxx, plot=False):
        """ DEPRECATED (for reference) """
        tpeaks = np.array(list(ss.find_peaks(sxx[:, i], height=self.MIN_POWER, width=10)[0] for i in range(sxx.shape[1])))
        fpeaks = np.array(list(ss.find_peaks(sxx[i, :], height=self.MIN_POWER, width=10)[0] for i in range(sxx.shape[0])))

        # create a big zero matrix which we will fill in with the peaks, as it is easier to work with
        # Wang calls them 'constellations', which we adopt
        cons_freq = np.zeros(sxx.shape)
        for i, peaks in enumerate(fpeaks):
            for j in peaks:
                cons_freq[i, j] = 1
        cons_time = np.zeros(sxx.shape)
        for i, peaks in enumerate(tpeaks):
            for j in peaks:
                cons_time[j, i] = 1

        # we will multiply the constellation matrices element-wise. As they consist of {0,1}
        # we know that we will get the intersection of time-band and element-band peaks only
        cons_both = np.multiply(cons_freq, cons_time)
        if plot:
            t_peaks, f_peaks = np.where(cons_both)
            plt.pcolormesh(sxx)
            plt.scatter(t_peaks, f_peaks, s=.5, c='red')
            plt.savefig('Testing time peaks constellation_overlay_{}.png'.format(str(time.time()).split('.')[0]))
        return cons_both

    def get_peaks(self, sxx, plot=False):
        """
            get the maximum power peaks in both the time and frequency dimesnions. using scipy 2 dimensional filtering
            we can identify the maximum power within a time-frequency area range.
        :param sxx: time x frequency spectrogram
        :param plot: boolean if we want to save the plot of the peak overlaid on the spectrogram
        :return: constellation of {0,1} if identified a peak. same size/shape as input sxx
        """
        fuzzy_sxx = maximum_filter(sxx, size=50) # two dimension filter (the maximum value of a square of size size)

        # find where the peak is located within the peak, and
        #   the peak is of greater power than the minimum power we are considering as a peak
        constellation = (sxx == fuzzy_sxx) & (sxx > self.MIN_POWER)
        if plot:
            time_peaks, freq_peaks = np.where(constellation)
            plt.pcolormesh(sxx)
            plt.scatter(freq_peaks, time_peaks, s=.5, c='red')
            plt.savefig('Testing time peaks constellation_new method_{}.png'.format(str(time.time()).split('.')[0]))
        return constellation

    def match(self, dbh, accurate=False):
        """
            attempt to match the computed signature to the database.
        :param dbh: initialized DatabaseHandler class
        :param accurate: quicker vs more accurate?
        :return: song name, artist name, album name, certainty of match, attempt _d
        """
        attempt_id = self.load_match_attempt(dbh)
        match_query_text = """SELECT {}.time_index, {}.signature, {}.song_id, totals.total_signatures FROM {} 
                    INNER JOIN {} ON {}.signature = {}.signature
                    INNER JOIN (SELECT count(time_index) as total_signatures, song_id FROM {} 
                                GROUP BY song_id) totals
                                ON totals.song_id={}.song_id 
                    WHERE {}.match_id = %s
                    ORDER BY {}.signature;
                """.format(
            TABLE_NAMES.SIGNATURE, TABLE_NAMES.SIGNATURE,
                           TABLE_NAMES.SIGNATURE, TABLE_NAMES.SIGNATURE_MATCH,
                           TABLE_NAMES.SIGNATURE, TABLE_NAMES.SIGNATURE_MATCH,
                           TABLE_NAMES.SIGNATURE, TABLE_NAMES.SIGNATURE,
                           TABLE_NAMES.SIGNATURE, TABLE_NAMES.SIGNATURE_MATCH,
                           TABLE_NAMES.SIGNATURE)
        # something about signatures
        f,t,sxx= self.spectrogram
        df_matches = pd.read_sql(match_query_text, dbh.con, params=(attempt_id,))
        if accurate:  # approx .2 seconds slower per snippet (~10%)
            df_matches['neighbors'] = df_matches.apply(lambda x: df_matches.loc[(df_matches['time_index'] < x['time_index'] + len(t)) &
                                                                            (df_matches['time_index'] > x['time_index']) &
                                                                            (df_matches['song_id'] == x['song_id'])].shape[0], axis=1)
            df_song_matches = df_matches.groupby('song_id').agg({'neighbors': 'sum', 'total_signatures': 'first'})
            df_song_matches['weighting'] = df_song_matches['neighbors'] / df_song_matches['total_signatures']
            df_song_matches['P'] = df_song_matches['weighting'] / df_song_matches['weighting'].sum()
            # df_matches.to_csv('matches_%s.csv' % attempt_id)
        else:  # approx 2 % more accurate
            df_song_matches = df_matches.groupby('song_id').agg({'time_index': 'count', 'total_signatures': 'first'})
            df_song_matches['weighting'] = df_song_matches['time_index'] / df_song_matches['total_signatures']
            df_song_matches['P'] = df_song_matches['weighting'] / df_song_matches['weighting'].sum()
        probability = df_song_matches['P'].max()

        if probability < self.MIN_PROBABILITY_FOR_MATCH or pd.isnull(probability):
            logger.info('No adequate matches found')
            return -1, probability, attempt_id
        logger.info('Match selected')
        song_id = df_song_matches['P'].idxmax()
        song_info = dbh.get_formatted_song_info(song_id)
        update_prediction = '''UPDATE {} SET predicted_song_id=%s WHERE id=%s;'''.format(TABLE_NAMES.MATCH_ATTEMPT)
        dbh.cur.execute(update_prediction, (song_id, attempt_id))
        return song_info, probability, attempt_id




##################################################################################################################
#                    THE SIGNATURES BELOW ARE NON-FUNCTIONING
##################################################################################################################


class SignalProcessorExactMatch(SignalProcessor):
    """
        Signal Processor class
        This class houses all of the functions which deal with processing signals
        Each class owns a wav segment
    """

    def __init__(self, audio_array, sample_freq, **kwargs):
        super().__init__(**kwargs)
        self.method = SIGNALTYPES.EXACT_MATCH

    def compute_signature(self):
        self.compute_windows()
        self.compute_periodogram()
        self.signature = self.periodograms
        f, pxx = zip(*self.signature)
        self.signature_info.update({'frequency': f,
                                    'signature': pxx})

    def match(self, dbh):
        raise NotImplementedError

class SignalProcessorSmoothedPeriodogram(SignalProcessor):
    """
        Signal Processor class
        This class houses all of the functions which deal with processing signals
        Each class owns a wav segment
    """
    epsilon = 10
    HANNING = 'hann'
    BLACKMAN = 'blackman'

    def __init__(self, audio_array, sample_freq, window_type=HANNING, **kwargs):
        super().__init__(**kwargs)
        self.window_type = window_type
        self.method = SIGNALTYPES.SMOOTHED_PERIODOGRAM

    def compute_signature(self):
        self.compute_windows()
        self.compute_periodogram(window=self.window_type)
        self.signature = self.periodograms
        f, pxx = zip(*self.signature)
        self.signature_info.update({'frequency': f,
                                    'signature': pxx})

    def match(self, dbh):
        raise NotImplementedError


class SignalProcessorPeaksOnly(SignalProcessor):
    """
        corresponds with ex 5 of the signature identification portion
    """
    SIXTEEN_EVEN = tuple([i * INC, (i + 1) * INC] for i in range(16))
    EIGHT_EVEN = tuple([i * INC*2, (i + 1) * INC*2] for i in range(8))
    EXP = tuple([2**i, 2**(i+1)] for i in range(int(np.log2(NFFT))))

    def __init__(self, audio_array, sample_freq, freq_ranges=SIXTEEN_EVEN, **kwargs):
        super().__init__(**kwargs)
        self.freq_ranges = freq_ranges
        self.method = SIGNALTYPES.MAX_POWER_FREQ_BANDS

    def compute_signature(self):
        self.compute_windows()
        self.compute_periodogram()
        orig_peaks = [0]*len(self.periodograms[0][1])
        for f, pxx in self.periodograms:
            peaks = orig_peaks.copy()
            for low, high in self.freq_ranges:
                peaks[low + np.argmax(pxx[low:high])] = 1
            self.signature.append((f, peaks))
        freq, all_peaks = zip(*self.signature)
        self.signature_info.update({'frequency': freq,
                                    'signature': all_peaks})

    def match(self, dbh):
        df = pd.read_sql('SELECT * FROM {}'.format(TABLE_NAMES.SIGNATURE),con=dbh.cur)
        matches = []
        for i in df.index:
            reference = df.loc[i,'signature']
            for sig in self.signature:
                if sig == reference:
                    matches.append(i)
        return matches



class SignalProcessorFreqPeaks(SignalProcessor):
    """
        corresponds to example 3
    """

    def __init__(self, min_distance=NFFT/32, **kwargs):
        raise NotImplementedError
        super().__init__(**kwargs)
        self.method = SIGNALTYPES.FREQ_PEAKS
        self.min_distance = min_distance  # could use distance between notes on the scale as default?

    def compute_signature(self):
        self.compute_windows()
        self.compute_periodogram()
        for f, pxx in self.periodograms:
            self.signature.append(ss.find_peaks(pxx, distance=self.min_distance))


class SignalProcessorPowerBands(SignalProcessor):
    """
        Power band signature processor, corresponds with example 3
    """

    def __init__(self, **kwargs):
        raise NotImplementedError
        super().__init__(**kwargs)

    def compute_signature(self):
        # using the power bands method
        pass

    def match(self, dbh):
        raise NotImplementedError
