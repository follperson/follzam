from exceptions import NotWavData
import wave
import scipy.signal as ss


# signature is at the song level
# spectrogram is frequency vs time matrix!! not just image
#   smooth frequency time representation of signal
# spectrograms are already fourier transformed!!
# spectrogram noise filteration using low pass filter to get constellation matrix
#  constellation matrix then gets hashed frequency dictionary
# fingerprint of spectrogram using

# locally sensitive

# spectrogram is and windowed periodgramed already

# hash borrows information of neighboring peaks before generating structure

# into figerpreing dict,
#    from hz and time, you get a hash

class SignalProcessor(object):
    EXACT_MATCH = 'EXACT_MATCH'
    SMOOTHED_PERIODOGRAM = 'SMOOTHED_PERIODOGRAM'
    FREQ_POWER_PAIRS = 'FREQ_POWER_PAIRS'
    FREQ_PEAKS = 'FREQ_PEAKS'
    MAX_POWER_FREQ_BANDS = 'MAX_POWER_FREQ_BANDS'

    ALL = [EXACT_MATCH, SMOOTHED_PERIODOGRAM, FREQ_POWER_PAIRS, FREQ_PEAKS, MAX_POWER_FREQ_BANDS]

    def __init__(self, wav, window_size=5):
        self.wav = wav
        self.window_size = window_size
        self.spectrogram = None

    def main(self):
        self.compute_spectrogram()
        self.compute_signature()

    def compute_signature(self):
        raise NotImplementedError

    def compute_spectrogram(self):
        self.spectrogram = ss.spectrogram(self.wav, fs=1, window=self.window_size)
        return self.spectrogram

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
        pass
        # for window in self.windows:
        #     self.periodograms.append(self.compute_periodogram(window))


    def compute_periodogram(self,window):
        """ Spectral Analysis """
        # ss.periodogram(self.wav,window=self.window_size)

        # intensity at each frequency
        # from fourier transformation (time domain from frequency domain)
        # intensity and frequency
        # construct image of signature
        # periodogram = ''
        # return periodogram
        pass

    @staticmethod
    def smooth_periodogram(periodogram):
        """
        smooth the periodogram using the
        :param periodogram:
        :return:
        """
        # periodogram is array
        return ''  # smoothed_periodorgam

    @staticmethod
    def visualize_spectrogram(spectrogram):
        """plot it for visual representation"""
        pass


    def windowing(self, size=5):
        """
            take full initialized song and cut it up into a bunch of windows of given size
        :param size: window size
        :return:
        """
        assert isinstance(size, (int, float))
        assert size > 0
        for wav_window_index in range(size, len(self.wav)):
            window = self.wav[wav_window_index - size / 2: wav_window_index + size / 2]
            # self.windows.append(self.compute_window(window))


class SignalProcessorExactMatch(SignalProcessor):
    """
        Signal Processor class
        This class houses all of the functions which deal with processing signals
        Each class owns a wav segment
    """

    def __init__(self,wav, window_size):
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

    def __init__(self,wav, window_size):
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

    def __init__(self,wav, window_size):
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

    def __init__(self,wav, window_size):
        super().__init__(wav, window_size)


    def compute_signature(self):
        # using the FreqPeaks method
        pass


class SignalProcessorPowerBands(SignalProcessor):
    """
        Power band signature processor
    """

    def __init__(self,wav, window_size):
        super().__init__(wav, window_size)


    def compute_signature(self):
        # using the power bands method
        pass

