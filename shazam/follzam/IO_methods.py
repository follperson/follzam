import io
import os
import requests
from pydub import AudioSegment
import numpy as np
import logging
from follzam.exceptions import UnsupportedFileType
from re import match
logger = logging.getLogger(__name__)
# https://stackoverflow.com/a/53633178/9936238


class ReadAudioData(object):
    """
        class housing the audio input processing functions.
        input to this class should be audio data of some sort, and output should be
        WAV structured data
    """

    def __init__(self, filepath_or_url):
        """
            read in audio file or audio url path using pydub, and transform it to an numpy array for processing
        :param filepath: filepath to read. You must specify filepath OR url, not both
        :param url: url path to read. You must specify filepath OR url, not both
        """
        self.audio = None
        self.array = None
        self.darray = None
        if match('^https?://', filepath_or_url):
            logger.info('Loading from url - {}'.format(filepath_or_url))
            self.read_url(filepath_or_url)
        else:
            logger.info('Loading from file path - {}'.format(filepath_or_url))
            self.read_file(filepath_or_url)

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
            self._from_file_obj(io.BytesIO(b''.join(total_f)))
            # dispatch the searching. this will require some redesign and threading. just leaving this in for a later

    def _from_file_obj(self, fobj):
        """ turns file object into operatable np array"""
        try:
            self.audio = AudioSegment.from_file(fobj)
        except Exception:
            raise UnsupportedFileType
        as_array = np.array(self.audio.get_array_of_samples())
        if self.audio .channels == 2:
            as_array = as_array.reshape((-1, 2))
        self.darray = as_array
        self.array = np.mean(as_array, axis=1)
        logger.info('Initialized audio')
