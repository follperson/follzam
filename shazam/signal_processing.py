import math
import numpy


class SignalProcessor(object):
    """ Signal Processor class.

    This class houses all of the functions which deal with processing signals
    and extracting features from audio samples

    Each class owns a wav segment

    """
    def __init__(self, wav):
        self.wav = wav
        self.wav_as_time_series= None

    def transform_wav_to_matrices(self):
        self.wav_as_time_series = self.wav

        pass

    def compute_signal_window(self, window):

        pass

    def compute_signal(self, wav, window_size=5):
        signal = []
        for wav_window_index in range(len(wav) // window_size):
            window = wav[wav_window_index: wav_window_index + window_size]
            signal.append(self.compute_signal_window(window))
        pass

    @staticmethod
    def hanning_window(t, h=5):
        if abs(t) <= h/2:
            return 1 + math.cos(2*math.pi*t/h)
        return 0

    @staticmethod
    def blackman_window(t, h=5):
        """ as found in notes"""
        pass

    @staticmethod
    def compute_periodogram(signal):
        """ from notes """

        # describes frequency structure of signal within window
        pass

    @staticmethod
    def visualize_periodogram(self, periodogram):
        """plot it for visual representation"""
        pass


