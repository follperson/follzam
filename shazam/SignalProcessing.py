from exceptions import NotWavData
import logging
import wave
import scipy.signal as ss
import numpy as np

NFFT = 2 ** 12
INC = NFFT // 16

class SignalProcessor(object):
    EXACT_MATCH = 'EXACT_MATCH'
    SMOOTHED_PERIODOGRAM = 'SMOOTHED_PERIODOGRAM'
    FREQ_POWER_PAIRS = 'FREQ_POWER_PAIRS'
    FREQ_PEAKS = 'FREQ_PEAKS'
    MAX_POWER_FREQ_BANDS = 'MAX_POWER_FREQ_BANDS'

    ALL = [
        EXACT_MATCH,
        SMOOTHED_PERIODOGRAM,
        FREQ_POWER_PAIRS,
        FREQ_PEAKS,
        MAX_POWER_FREQ_BANDS]


    def __init__(self, audio_array, sample_freq, window_size=5):
        self.audio_array = audio_array
        self.sample_freq = sample_freq
        self.window_size = window_size
        self.periodograms = []
        self.signature = []
        self.windows = []
        self.smoothed_windows = []

    def main(self):
        self.compute_signature()

    def compute_signature(self):
        raise NotImplementedError

    def compute_periodogram(self,**kwargs):
        """ Spectral Analysis """
        for window in self.smoothed_windows:
            f, pxx = ss.periodogram(window, fs=self.sample_freq, nfft=NFFT, **kwargs)
            self.periodograms.append(pxx)

    def compute_spectrogram(self, audio_array=None):
        if audio_array is None:
            audio_array = self.audio_array
        spectrogram = ss.spectrogram(audio_array, fs=self.sample_freq, window=self.window_size)
        return spectrogram

    def compute_windows(self):
        """
            take full initialized song and cut it up into a bunch of windows of given size
        :param size: window size
        :return:
        """
        assert isinstance(self.window_size, (int, float))
        assert self.window_size > 0
        for wav_window_index in range(self.window_size*1000, len(self.audio_array) // 1000):
            window = self.audio_array[wav_window_index - self.window_size*1000 / 2: wav_window_index + self.window_size*1000 / 2]
            self.windows.append(window)


class SignalProcessorExactMatch(SignalProcessor):
    """
        Signal Processor class
        This class houses all of the functions which deal with processing signals
        Each class owns a wav segment
    """

    def __init__(self, wav, window_size):
        super().__init__(wav, window_size)

    def compute_signature(self):
        self.compute_windows()
        self.smoothed_windows = self.windows
        self.compute_periodogram()
        self.signature = self.periodograms


class SignalProcessorSmoothedPeriodogram(SignalProcessor): # should i enable smoothing on the rest? probably
    """
        Signal Processor class
        This class houses all of the functions which deal with processing signals
        Each class owns a wav segment
    """
    HANNING = 'hann'
    BLACKMAN = 'blackman'

    def __init__(self, window_type=HANNING, **kwargs):
        super().__init__(**kwargs)
        self.window_type = window_type

    def compute_signature(self):
        self.compute_windows()
        self.compute_periodogram(window=self.window_type)


class SignalProcessorPeaksOnly(SignalProcessor):
    """
        corresponds with ex 5 of the signature identification portion
    """
    SIXTEEN_EVEN = ([i * INC, (i + 1) * INC] for i in range(15))
    EIGHT_EVEN = ([i * INC*2, (i + 1) * INC*2] for i in range(8))
    EXP = ([2**i, 2**(i+1)] for i in range(int(np.log2(NFFT))))

    def __init__(self, freq_ranges=EIGHT_EVEN, **kwargs):
        super().__init__(**kwargs)
        self.freq_ranges = freq_ranges

    def compute_signature(self):
        self.compute_windows()
        self.compute_periodogram()
        for periodogram in self.periodograms:
            for low, high in self.freq_ranges:
                self.signature.append(np.argmax(periodogram[low:high]))


class SignalProcessorFreqPeaks(SignalProcessor):
    """
        corresponds to example 3
    """
    MAX_POWER_FREQ_BANDS = 'MAX_POWER_FREQ_BANDS'

    def __init__(self, min_distance=NFFT/32, **kwargs):
        super().__init__(**kwargs)
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
        super().__init__(**kwargs)

    def compute_signature(self):
        # using the power bands method
        pass
