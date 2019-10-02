
from exceptions import NotWavData

import wave
class SignalProcessor(object):
    """
        Signal Processor class
        This class houses all of the functions which deal with processing signals
        Each class owns a wav segment
    """
    class SignatureProcesses:
        EXACT_MATCH = 'EXACT_MATCH'
        SMOOTHED_PERIODOGRAM = 'SMOOTHED_PERIODOGRAM'
        FREQ_POWER_PAIRS = 'FREQ_POWER_PAIRS'
        FREQ_PEAKS = 'FREQ_PEAKS'
        MAX_POWER_FREQ_BANDS = 'MAX_POWER_FREQ_BANDS'

        ALL = [EXACT_MATCH, SMOOTHED_PERIODOGRAM, FREQ_POWER_PAIRS, FREQ_PEAKS, MAX_POWER_FREQ_BANDS]

    def __init__(self, wav):
        try:
            assert type(wav) == wave.Wave_read
        except AssertionError:
            raise NotWavData

        self.wav = wav

        self.windows = []
        self.periodograms = []
        self.signatures = []

    def main(self, signature_type=SignatureProcesses.EXACT_MATCH):
        """
            main function used for end to end computation of wav file to signatures
                object still stores the relevant data
            ?? I could implement it via one loop instead of three??

        :param signature_type: signature method
        :return: None
        """
        self.windowing()
        self.compute_periodograms()
        if signature_type == self.SignatureProcesses.EXACT_MATCH:
            self.signatures = self.periodograms
        elif signature_type == self.SignatureProcesses.SMOOTHED_PERIODOGRAM:
            pass
            # etc..
        # elif
        # etc...

    def windowing(self, size=5):
        """
            take full initialized song and cut it up into a bunch of windows of given size
        :param size: window size
        :return:
        """
        assert isinstance(size,(int, float))
        assert size > 0
        for wav_window_index in range(size, len(self.wav)):
            window = self.wav[wav_window_index - size/2: wav_window_index + size/2]
            self.windows.append(self.compute_window(window))

    def compute_window(self, window):
        # implement fancy windowing function
        # return improved window
        pass

    @staticmethod
    def hanning_window(t, h=5):
        """ from notes """
        return

    @staticmethod
    def blackman_window(t, h=5):
        """ implement blackman windowing"""
        pass

    def compute_periodograms(self):
        for window in self.windows:
            self.periodograms.append(self.compute_periodogram(window))

    @staticmethod
    def compute_periodogram(window):
        """ Spectral Analysis """
        # intensity at each frequency
        # from fourier transformation (time domain from frequency domain)
        # intensity and frequency
        # construct image of signature
        periodogram = ''
        return periodogram

    @staticmethod
    def smooth_periodogram(periodogram):
        """
        smooth the periodogram using the
        :param periodogram:
        :return:
        """
        # periodogram is array
        return ''# smoothed_periodorgam

    @staticmethod
    def compute_signature(periodogram, method):
        """
        using method keyword you can implement a signature generation function

        :param periodogram:
        :param method:
        :return:
        """

        return '' #signature

    @staticmethod
    def visualize_periodogram(periodogram):
        """plot it for visual representation"""
        pass
