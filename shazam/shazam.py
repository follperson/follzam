from IO_methods import *
from signal_processing import *



def main():
    fp = '/path/to/snippet'
    audio = ReadAudioData()
    audio.initialize(fp)
    signal = SignalProcessor(audio.wav)
    signal.transform_wav_to_matrices()

