import os
import requests


# should I make this into a bunch of files and estensible classes??
# like an IO_Methods folder ->  a read audio base class then stream/file variants?
# ...probably. put those in ReadAudio subfolder


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

    def __init__(self, filepath=None, stream=None):
        assert not (filepath is None and stream is None), 'You must specify aa filepath or a stream'
        assert not (filepath is not None and stream is not None), 'You mus specify a filepath OR a stream, not both'

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
        except:
            pass #idk
        download = resp # download
        self.interpret_filetype(download)
        # check the download ftype type
        # handle read_url


    def read_stream(self, socket):
        # do some checks
        self._from_stream(socket)

    def _from_file(self, filepath):
        """ deduces file type (just by the extension now, maybe some other way later """
        fobj = open(filepath,'rb')
        self.interpret_filetype(fobj)
        # ext = filepath.split('.')[-1].upper()
        # fileobj = open(filepath, 'rb')
        # if ext == self.AcceptedAudioTypes.FILES.FLAC:
        #     self._from_flac(fileobj)
        # elif ext == self.AcceptedAudioTypes.FILES.MP3:
        #     self._from_mp3(fileobj)
        # elif ext == self.AcceptedAudioTypes.FILES.MP4:
        #     self._from_mp4(fileobj)
        # elif ext == self.AcceptedAudioTypes.FILES.WAV:
        #     self._from_wav(fileobj)
        # else:
        #     raise UnsupportedFileType


    @staticmethod
    def interpret_filetype(fobj):
        # if it looks like a mp3, then do the mp3 one
        # if it looks like a flac, do a flac
        # etc...
        pass

    def _from_stream(self, socket):
        """
            stream the data
        """
        pass

    def _from_mp3(self, fileobj):
        # method to read in mp3
        # turn it into wav
        pass

    def _from_wav(self,fileobj):
        # method to read in mp3
        pass

    def _from_flac(self,fileobj):
        pass

    def _from_mp4(self, fileobj):
        pass

