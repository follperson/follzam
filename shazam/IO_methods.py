import io
import os
import requests
from pydub import AudioSegment
import numpy as np
VALID_FILE_TYPES = ['WAV','MP3','OGG','FLAC']
# https://stackoverflow.com/a/53633178/9936238
ex = r'assets/music/Blonde Redhead/Barragán/04  - Cat On Tin Roof.mp3'
ex_url = "https://upload.wikimedia.org/wikipedia/en/0/0c/She_Loves_You_%28Beatles_song_-_sample%29.ogg"
ex_test = r'C:\Users\follm\Documents\s750\assignments-follperson\shazam\assets\files_for_tests\01 Speed Trials_4.mp3'
ex_test_2 = r'C:\Users\follm\Documents\s750\assignments-follperson\shazam\assets\files_for_tests\01 Speed Trials_5.mp3'
ex_test_full = r'C:\Users\follm\Documents\s750\assignments-follperson/assets/audio/songs/01 Speed Trials.mp3'


class ReadAudioData(object):
    """
        class housing the audio input processing functions.
        input to this class should be audio data of some sort, and output should be
        WAV structured data
    """

    def __init__(self, filepath=None, stream=None):
        # todo make this cleaner
        assert not (
            filepath is None and stream is None), 'You must specify aa filepath or a stream'
        assert not (
            filepath is not None and stream is not None), 'You mus specify a filepath OR a stream, not both'
        self.audio = None
        self.array = None
        self.darray = None
        if filepath is not None:
            self.read_file(filepath)
        else:
            self.read_url(stream)

        pass

    def read_file(self, filepath):
        assert os.path.isfile(filepath)
        fobj = open(filepath, 'rb')
        return self._from_file_obj(fobj)

    def read_url(self, url):
        resp = requests.get(url)
        self._check_resp(resp)
        file_like = io.BytesIO(resp.content)
        self._from_file_obj(file_like)

    @staticmethod
    def _check_resp(resp):
        if resp.status_code not in (200, 201, 202, 203, 204): # url is bad
            # todo needs more nuance
            raise Exception


    def read_stream(self, url):
        raise NotImplementedError
        # https://medium.com/@anthonypjshaw/python-requests-deep-dive-a0a5c5c1e093
        resp = requests.get(url, stream=True)
        self._check_resp(resp)
        chunksize = 8096
        total_f = []
        for chunk in resp.iter_content(chunksize):
            total_f.append(chunk)
            file_like = io.BytesIO(b''.join(total_f))
            self._from_file_obj(file_like)
            # dispatch the searching. this will require some redesign. just leaving this in for a later todo

    def _from_file_obj(self, fobj):
        """ turns file object into operatable np array"""
        self.audio = AudioSegment.from_file(fobj)
        as_array = np.array(self.audio.get_array_of_samples())
        if self.audio .channels == 2:
            as_array = as_array.reshape((-1,2))
        self.darray = as_array
        self.array = np.mean(as_array, axis=1)
