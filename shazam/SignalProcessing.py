import time
import pandas as pd
import logging
import scipy.signal as ss
import matplotlib.pyplot as plt
import numpy as np
from math import ceil
import database_management
from scipy.ndimage.filters import maximum_filter

NFFT = 2 ** 12
INC = NFFT // 16
#https://stackoverflow.com/questions/51042870/wrong-spectrogram-when-using-scipy-signal-spectrogram?noredirect=1&lq=1


logger = logging.getLogger('Shazam.SignalProcessing')


class SignalProcessor(object):
    """
        Base class for signal processor
    """
    class SIGNALTYPES:
        EXACT_MATCH = 'EXACT_MATCH'
        SMOOTHED_PERIODOGRAM = 'SMOOTHED_PERIODOGRAM'
        FREQ_POWER_PAIRS = 'FREQ_POWER_PAIRS'
        FREQ_PEAKS = 'FREQ_PEAKS'
        MAX_POWER_FREQ_BANDS = 'MAX_POWER_FREQ_BANDS'
        SPECTROGRAM = 'SPECTROGRAM'
        ALL = [
            EXACT_MATCH,
            SMOOTHED_PERIODOGRAM,
            FREQ_POWER_PAIRS,
            FREQ_PEAKS,
            MAX_POWER_FREQ_BANDS,
            SPECTROGRAM]

    def __init__(self, audio_array, sample_freq, window_size=5, songinfo={}):
        self.songinfo = songinfo
        self.audio_array = audio_array
        self.sample_freq = sample_freq
        self.window_size = window_size
        self.periodograms = []
        self.signature = []
        self.spectrogram = None
        self.windows = []
        self.smoothed_windows = [] # do i need this??/ looks like periodogram implements a smoothing
        assert isinstance(self.window_size, (int, float))
        assert self.window_size > 0
        self.window_centers = list(range(
            self.window_size // 2, ceil(len(self.audio_array) // self.sample_freq) - self.window_size // 2))
        self.signature_info = {'time_index': self.window_centers}

    def compute_signature(self):
        raise NotImplementedError

    def compute_periodogram(self, **kwargs):
        for window in self.smoothed_windows:
            f, pxx = ss.periodogram(window, fs=self.sample_freq, nfft=NFFT, **kwargs)
            self.periodograms.append((f, pxx))

    def compute_spectrogram(self, audio_array=None):
        if audio_array is None:
            audio_array = self.audio_array
        spectrogram = ss.spectrogram(audio_array, fs=self.sample_freq, window='hamm', nfft=NFFT, nperseg=NFFT,
                                     noverlap=NFFT * .5)
        return spectrogram

    def plot_spectrogram(self, audio_array=None):
        if audio_array is None:
            audio_array = self.audio_array
        f, t, sxx = self.compute_spectrogram(audio_array)
        plt.pcolormesh(t, f, np.log10(sxx))
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time (sec)')
        plt.show()

    def compute_windows(self):
        """
            take full initialized song and cut it up into a bunch of windows of given size
        :param size: window size
        :return:
        """
        for window_index in self.window_centers:
            window = self.audio_array[(window_index - self.window_size // 2) * self.sample_freq:
                                      (window_index + self.window_size // 2) * self.sample_freq]
            self.windows.append(window)

    @staticmethod
    def match(sig1, sig2):
        raise NotImplementedError


class SignalProcessorExactMatch(SignalProcessor):
    """
        Signal Processor class
        This class houses all of the functions which deal with processing signals
        Each class owns a wav segment
    """

    def __init__(self, audio_array, sample_freq, **kwargs):
        super().__init__(**kwargs)
        self.method = SignalProcessor.SIGNALTYPES.EXACT_MATCH

    def compute_signature(self):
        self.compute_windows()
        self.smoothed_windows = self.windows
        self.compute_periodogram()
        self.signature = self.periodograms
        f, pxx = zip(*self.signature)
        self.signature_info.update({'frequency': f,
                                    'signature': pxx})


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
        self.method = self.SIGNALTYPES.SMOOTHED_PERIODOGRAM

    def compute_signature(self):
        self.compute_windows()
        self.smoothed_windows = self.windows
        self.compute_periodogram(window=self.window_type)
        self.signature = self.periodograms
        f, pxx = zip(*self.signature)
        self.signature_info.update({'frequency': f,
                                    'signature': pxx})


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
        self.method = self.SIGNALTYPES.MAX_POWER_FREQ_BANDS

    def compute_signature(self):
        self.compute_windows()
        self.smoothed_windows = self.windows
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

    @staticmethod
    def match(signature_to_match, reference_signatures):
        for signature in reference_signatures:
            if signature_to_match == signature:
                return True


class SignalProcessorSpectrogram(SignalProcessor):
    """
        Implementation of spectrogram method for signature finding.
    """
    EXP = tuple([2**i, 2**(i+1)] for i in range(int(np.log2(NFFT))))
    TIME_NET_WINDOW = 2000  # forward propagation of net (look forward window)
    FREQ_NET_WINDOW = 20  # frequency propagation of net (above and below current)
    MIN_POWER = 10
    def __init__(self, audio_array, sample_freq, **kwargs):
        super().__init__(audio_array=audio_array,
                         sample_freq=sample_freq,
                         **kwargs)
        self.method = SignalProcessor.SIGNALTYPES.SPECTROGRAM
        self.signature_info = {}

    def compute_signature(self):
        f, t, sxx = self.compute_spectrogram()
        sxx = 10*np.log10(sxx)
        # first find the time wise and frequency band level peaks, using scipy
        constellation = self.get_peaks(sxx, True)
        constellation = self.get_peaks_alt(sxx, True)
        # corresponding with the hashhing portion of the Wang paper, we will compute a signature
        # for each identified peak
        signature = {}
        for i in range(sxx.shape[1]):  # iterate over time dimension
            cpeaks = np.where(constellation[:, i] == 1)[0]  # subset to get the current peaks
            for freq in cpeaks:
                freq_offset, time_offset = np.where(
                    constellation[(freq - self.FREQ_NET_WINDOW):(freq + self.FREQ_NET_WINDOW), i:i + self.TIME_NET_WINDOW])

                coord_pairs = list(zip(*(freq_offset + freq - self.FREQ_NET_WINDOW, i + time_offset)))

                ranked_coords = sorted(coord_pairs, key=lambda x: sxx[x], reverse=True)
                ranked_freqs = [f[freq_index] for freq_index, time_index in ranked_coords
                                if 20 < f[freq_index] < 20000]
                if len(ranked_freqs) == 0:
                    continue
                ranked_freqs = ranked_freqs[:3]
                # str freqs
                #signature[(i, freq)] = ','.join([str(int(i)) for i in ranked_freqs[:3]])
                # number sig
                signature[(i, freq)] = sum((i + 1) * 10 * int(j) for i, j in enumerate(reversed(ranked_freqs)))
        self.signature = signature

    # n_homog = 10

    #        tpeaks = list(
    #           [mini + np.argmax(sxx[mini:maxi, i * 5:(i + 1) * 5].sum(axis=1)) for mini, maxi in FREQ_BANDS] for i in
    #          range(sxx.shape[1] // 5))

    def get_peaks(self, sxx, plot=False):
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
        t_peaks, f_peaks = np.where(cons_both)
        if plot:
            fig, ax = plt.subplots()
            ax.imshow(sxx)
            ax.scatter(f_peaks,t_peaks, s=.5, c='red')
            ax.set_xlabel('Time')
            ax.set_ylabel('Frequency')
            ax.set_title("Spectrogram")
            plt.gca().invert_yaxis()
            plt.savefig('Testing time peaks constellation_overlay_{}.png'.format(str(time.time()).split('.')[0]))
        return cons_both

    def get_peaks_alt(self, sxx, plot=False):
        fuzzy_sxx = maximum_filter(sxx, size=50)
        constellation = (sxx == fuzzy_sxx) & (sxx > self.MIN_POWER)
        if plot:
            time_peaks, freq_peaks = np.where(constellation)
            plt.pcolormesh(sxx)
            plt.scatter(freq_peaks, time_peaks, s=.5, c='red')
            plt.savefig('Testing time peaks constellation_new method_{}.png'.format(str(time.time()).split('.')[0]))

        return constellation

    def load_signature(self, dbc):
        """
            load the current signature
        :param dbc: database connector object
        :return:
        """
        song_id = dbc.get_song_id(**self.songinfo)
        sig_type_id = dbc.get_signature_id_by_name(self.method)

        logger.info("begin loading of signature for %s" % self.songinfo)
        df = pd.DataFrame.from_dict(self.signature, 'index',columns=['signature'])
        df['method_id'] = sig_type_id
        df['song_id'] = song_id
        df['time_index'] = df.index.str[0]
        df['frequency'] = df.index.str[1]
        df = df.loc[df['signature'] > 0]
        df.to_sql(database_management.DatabaseInfo.TABLE_NAMES.SIGNATURE,
                  con=dbc.cur,
                  if_exists='append',
                  index=False)

    @staticmethod
    def match(sig1, sig2):

        pass

class SignalProcessorFreqPeaks(SignalProcessor):
    """
        corresponds to example 3
    """

    def __init__(self, min_distance=NFFT/32, **kwargs):
        raise NotImplementedError
        super().__init__(**kwargs)
        self.method = SignalProcessor.SIGNALTYPES.FREQ_PEAKS
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
