
import os
import wave


class ReadAudioData(object):
    """
        functions to read in purported audio data dn output wav data
    """

    def read_file(self, filepath):
        assert os.path.isfile(filepath)
        return self._from_file(filepath)

    def read_stream(self, socket):
        pass

    def read_url(self, url):
        pass

    def _from_url(self, url):
        pass
    def _from_file(self, filepath):
        pass

    def _from_stream(self, socket):
        """
        """
        pass

    def _read_mp3(self):
        # method to read in mp3
        pass

    def _read_flac(self):
        pass

    def _read_mp4(self):
        pass


    def read(self, obj):
        # if obj is file
        # self._from_file(obj)
        # if obj is socket
        # self.from_stream
        pass

