from exceptions import NotWavData
import wave


class SignalProcessor(object):
    """
        Signal Processor class
        This class houses all of the functions which deal with processing signals
        Each class owns a wav segment
    """
    # class SignatureMethods: will implement these as subclasses to this as an abstract class,but no
    EXACT_MATCH = 'EXACT_MATCH'
    SMOOTHED_PERIODOGRAM = 'SMOOTHED_PERIODOGRAM'
    FREQ_POWER_PAIRS = 'FREQ_POWER_PAIRS'
    FREQ_PEAKS = 'FREQ_PEAKS'
    MAX_POWER_FREQ_BANDS = 'MAX_POWER_FREQ_BANDS'

    ALL = [EXACT_MATCH, SMOOTHED_PERIODOGRAM, FREQ_POWER_PAIRS, FREQ_PEAKS, MAX_POWER_FREQ_BANDS]

    def __init__(self, wav, signature_method=EXACT_MATCH):
        try:
            assert type(wav) == wave.Wave_read
        except AssertionError:
            raise NotWavData
        self.wav = wav
        self.windows = []
        self.periodograms = []
        self.signatures = []

    def main(self, signature_type=EXACT_MATCH):
        """
            main function used for end to end computation of wav file to signatures
                object still stores the relevant data
            ?? I could implement it via one loop instead of three??

        :param signature_type: signature method
        :return: None
        """
        self.windowing()
        self.compute_periodograms()
        if signature_type == self.EXACT_MATCH:
            self.signatures = self.periodograms
        elif signature_type == self.SMOOTHED_PERIODOGRAM:
            pass
            # etc..
        # elif
        # etc...

    def windowing(self, num_secs=5):
        """
            take full initialized song and cut it up into a bunch of windows of given size
        :param num_secs: window size
        :return:
        """
        assert isinstance(num_secs, (int, float))
        assert num_secs > 0
        num_ms = num_secs*1000
        for wav_window_index in range(1, len(self.wav) * 1000):
            window = self.wav[wav_window_index - num_ms / 2: wav_window_index + num_ms / 2]
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
