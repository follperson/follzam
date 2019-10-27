from exceptions import NotWavData
import logging
import wave
import scipy.signal as ss
import numpy as np

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
    NFFT = 2**12
    FREQ_RANGES = [[i*2**8,(i+1)*2**8] for i in range(NFFT//2**8)]

    def __init__(self, audio_array, sample_freq, window_size=5):
        self.audio_array = audio_array
        self.sample_freq = sample_freq
        self.window_size = window_size
        self.spectrogram = None
        self.periodograms = []
        self.signature = []
        self.windows = []
        self.smoothed_windows = []

    def main(self):
        self.compute_spectrogram(self.audio_array)
        # self.compute_signature()

    def compute_signature(self):
        raise NotImplementedError

    def get_audio_signature(self):
        for window_index in range(len(self.audio_array) - (self.window_size*1000)):
            self.windows.append(self.audio_array[window_index:window_index + self.window_size*1000])
        for window in self.windows:
            self.smooth_window(window)
        for window in self.smoothed_windows:
            self.compute_periodogram(window)


    def compute_avg_periodogram(self, window):
        """ Spectral Analysis """
        pd = ss.welch(window, fs=self.sample_freq, nperseg=self.sample_freq, nfft=512)
        self.periodograms.append(pd)

    def compute_periodogram(self, window):
        """ Spectral Analysis """
        f, pxx = ss.periodogram(window,
                                fs=self.sample_freq,
                                nfft=512)
        self.periodograms.append(pxx)

    def compute_signature(self, periodogram):
        for low, high in self.FREQ_RANGES:
            self.signature.append(np.argmax(periodogram[low:high]))
        # intensity at each frequency
        # from fourier transformation (time domain from frequency domain)
        # intensity and frequency
        # construct image of signature
        pass

    def compute_spectrogram(self, audio_array):
        spectrogram = ss.spectrogram(audio_array, fs=self.sample_freq, window=self.window_size)
        return spectrogram


    def smooth_window(self, window):
        # window
        # implement fancy windowing function
        # return improved window
        pass


    def windowing(self):
        """
            take full initialized song and cut it up into a bunch of windows of given size
        :param size: window size
        :return:
        """
        assert isinstance(self.window_size, (int, float))
        assert self.window_size > 0
        for wav_window_index in range(self.window_size,
                                      len(self.audio_array)):
            window = self.audio_array[wav_window_index - self.window_size / 2: wav_window_index + self.window_size / 2]
            # self.windows.append(self.compute_window(window))


class SignalProcessorExactMatch(SignalProcessor):
    """
        Signal Processor class
        This class houses all of the functions which deal with processing signals
        Each class owns a wav segment
    """

    def __init__(self, wav, window_size):
        super().__init__(wav, window_size)

    def compute_signature(self):
        # using the unsmoothed periodogram
        pass


class SignalProcessorSmoothedPeriodogram(SignalProcessor):
    """
        Signal Processor class
        This class houses all of the functions which deal with processing signals
        Each class owns a wav segment
    """

    def __init__(self, wav, window_size):
        super().__init__(wav, window_size)

    def compute_signature(self):
        # using the smoothed periodogram
        pass


class SignalProcessorFreqPowerPairs(SignalProcessor):
    """
        Signal Processor class
        This class houses all of the functions which deal with processing signals
        Each class owns a wav segment
    """

    def __init__(self, wav, window_size):
        super().__init__(wav, window_size)

    def compute_signature(self):
        # using the freq power pairs
        pass


class SignalProcessorFreqPeaks(SignalProcessor):
    """
        Signal Processor class
        This class houses all of the functions which deal with processing signals
        Each class owns a wav segment
    """
    MAX_POWER_FREQ_BANDS = 'MAX_POWER_FREQ_BANDS'

    def __init__(self, wav, window_size):
        super().__init__(wav, window_size)

    def compute_signature(self):
        # using the FreqPeaks method
        pass


class SignalProcessorPowerBands(SignalProcessor):
    """
        Power band signature processor
    """

    def __init__(self, wav, window_size):
        super().__init__(wav, window_size)

    def compute_signature(self):
        # using the power bands method
        pass
