from . import AudioFiles, AudioStreams
from .exceptions import *
import os
import wave


# should I make this into a bunch of files and estensible classes??
# like an IO_Methods folder ->  a read audio base class then stream/file variants?
# ...probably




class ReadAudioData(object):
    """
        class housing the audio input processing functions.
        input to this class should be audio data of some sort, and output should be
        WAV structured data
    """

    class AcceptedAudioTypes:
        class FILES:
            FLAC = 'FLAC'
            MP3 = 'MP3'
            MP4 = 'MP4'
            WAV = 'WAV'

            ALL = [FLAC, MP3, MP4, WAV]

        class STREAMS:
            STREAM = 'STREAM'
            OTHERSTREAMS = 'OTHERSTREAMS'

    def __init__(self):
        self.wav = None
        self.ext = None

    def initialize(self, filepath=None, stream=None):
        assert not (filepath is None and stream is None), 'You must specify aa filepath or a stream'
        assert not (filepath is not None and stream is not None),'You mus specify a filepath OR a stream, not both'
        if filepath is not None:
            self.read_file(filepath)
        else:
            self.read_stream(stream)
        # if obj is file
        # self._from_file(obj)
        # if obj is socket
        # self.from_stream
        pass

    def read_file(self, filepath):
        assert os.path.isfile(filepath)
        return self._from_file(filepath)

    def read_stream(self, socket):
        pass

    def _from_file(self, filepath):
        """ deduces file type (just by the extension now, maybe some other way later """
        ext = filepath.split('.')[-1].upper()
        fileobj = open(filepath, 'rb')
        if ext == self.AcceptedAudioTypes.FILES.FLAC:
            self._read_flac(fileobj)
        elif ext == self.AcceptedAudioTypes.FILES.MP3:
            self._read_mp3(fileobj)
        elif ext == self.AcceptedAudioTypes.FILES.MP4:
            self._read_mp4(fileobj)
        elif ext == self.AcceptedAudioTypes.FILES.WAV:
            self._read_wav(fileobj)
        else:
            raise UnsupportedFileType

    def _from_stream(self, socket):
        """
            stream the data
        """
        pass

    def _read_mp3(self, fileobj):
        # method to read in mp3
        # turn it into wav
        pass

    def _read_wav(self,fileobj):
        # method to read in mp3
        pass

    def _read_flac(self,fileobj):
        pass

    def _read_mp4(self, fileobj):
        pass

