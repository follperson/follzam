import logging
import scipy.signal as ss
import matplotlib.pyplot as plt
import numpy as np
from math import ceil
from itertools import islice
NFFT = 2 ** 9
INC = NFFT // 16

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
        spectrogram = ss.spectrogram(audio_array, fs=self.sample_freq, nfft=NFFT)
        if audio_array is None:
            self.spectrogram = spectrogram
        return spectrogram

    def plot_spectrogram(self, audio_array=None):
        if audio_array is None:
            audio_array = self.audio_array
        f, t, sxx = self.compute_spectrogram(audio_array)
        plt.pcolormesh(t, f, np.log(sxx))
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

    def __init__(self, **kwargs):
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

    def __init__(self, window_type=HANNING, **kwargs):
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

    def __init__(self, freq_ranges=SIXTEEN_EVEN, **kwargs):
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.method = SignalProcessor.SIGNALTYPES.SPECTROGRAM
        self.signature_info = {}

    def compute_signature(self):
        self.compute_spectrogram()
        f, t, sxx = self.spectrogram
        # first find the time wise and frequency band level peaks, using scipy
        tpeaks = np.array(list(ss.find_peaks(sxx[:, i], width=2)[0] for i in range(sxx.shape[1])))
        fpeaks = np.array(list(ss.find_peaks(sxx[i, :], width=2)[0] for i in range(sxx.shape[0])))

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

        # corresponding with the hashhing portion of the Wang paper, we will compute a signature
        # for each identified peak
        net_time = 2000  # forward propagation of net (look forward window)
        net_freq = 20  # frequency propagation of net (above and below current)
        signature = {}
        for i in range(sxx.shape[1]):
            if i % 1000 == 0: print(i)
            cpeaks = np.where(cons_both[:, i] == 1)[0]
            for freq in cpeaks:
                freq_offset, time_offset = np.where(cons_both[(freq - net_freq):(freq + net_freq), i:i + net_time])
                coord_pairs = list(zip(*(freq_offset + freq - net_freq, i + time_offset)))
                ranked_coords = sorted(coord_pairs, key=lambda x: sxx[x], reverse=True)
                ranked_freqs = [f[freq_index] for freq_index, time_index in ranked_coords
                                if 20 < f[freq_index] < 20000]
                # ranked_freqs = [freq_index for freq_index, time_index in ranked_coords] # is this better or worse?
                ranked_freqs = ranked_freqs[:5]
                signature[(i, freq)] = sum((i + 1) * 10 * j for i, j in enumerate(reversed(ranked_freqs)))

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
