import os
import requests
from pydub import AudioSegment

class ReadAudioData(object):
    """
        class housing the audio input processing functions.
        input to this class should be audio data of some sort, and output should be
        WAV structured data
    """

    FLAC = 'FLAC'
    MP3 = 'MP3'
    MP4 = 'MP4'
    WAV = 'WAV'

    ACCEPTED = [FLAC, MP3, MP4, WAV]

    def __init__(self, filepath=None, stream=None):
        assert not (
            filepath is None and stream is None), 'You must specify aa filepath or a stream'
        assert not (
            filepath is not None and stream is not None), 'You mus specify a filepath OR a stream, not both'

        self.wav = None
        self.ext = None

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

    def read_url(self, url):
        try:
            resp = requests.get(url)
        except BaseException:
            pass  # idk
        download = resp  # download
        audio=AudioSegment.from_file(download)
        # check the download ftype type
        # handle read_url

    def read_stream(self, socket):
        # do some checks
        self._from_stream(socket)


    def _from_file(self, filepath):
        """ deduces file type (just by the extension now, maybe some other way later """
        fobj = open(filepath,'rb')
        audio = AudioSegment.from_file(fobj)
        self.wav = audio

    def _from_stream(self, socket):
        """
            stream the data
        """
        pass

