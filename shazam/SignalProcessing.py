import logging
import scipy.signal as ss
import matplotlib.pyplot as plt
import numpy as np
from math import ceil
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
    # might require some database adjustment because its time independent
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.method = SignalProcessor.SIGNALTYPES.SPECTROGRAM
        self.signature_info = {}

    def compute_signature(self):
        self.compute_spectrogram()
        f, t, sxx = self.spectrogram  # sxx = nfft/2 + 1
        sxxt = np.transpose(sxx)
        peaks = [ss.find_peaks(x) for x in sxxt]

        # make it two dimensional, or like, cluster groups?
        peaks_fb = [] # or break it up by frequency bands
        # this is a mtrix of zeros and ones for peak / not, at each time
        # net portion - for each peak, cast out a net forward in time
        # then order the number of the forward net of frequencies based on the power
        #

        # locality sensitivity hash


        #
        # cant use the time window part
        #self.signature_info.update({'frequency': f, 'signature':''})

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
