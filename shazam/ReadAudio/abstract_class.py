

class AudioProcessorBaseClass(object):
    def __init__(self, stream_or_filepath):
        self.read(stream_or_filepath)
        self.wav = None

    def read(self, stream_or_filepath):
        AU