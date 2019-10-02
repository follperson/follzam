
from signal_processing import SignalProcessor

def get_access_info():
    pass

class DatabaseHandler(object):
    """
        class managing database update procedures

    """

    def __init__(self):
        """
            initialize a database connection
        """
        access_info = get_access_info()
        # connect to db using access info
        self.db = access_info

        pass

    def add_song(self, wav, name, artist=None, album=None):
        # check if song already there
        # try: self.get_song
        # except cannot find
        # song table
        # add
        #
        pass

    def add_spectrogram(self, song_id, spectrograms, windowsize):
        for i, spectrogram in enumerate(spectrograms):
            center = (i / len(spectrograms)) + windowsize / 2
            # spectrogram to add to database with center and song_id and windowsize

    def remove_song(self, name):
        """
        :param name: name of song to be removed
        :return: nothing
        """
        # what if multiple songs with name??

        # find id
        # remove entry
        # for each periodogra stuff associated with it then delete that too
        pass

    def list_songs(self):
        # df = read sql
        # print(df)
        pass

    def get_song(self, field, value): # searching
        # if field = 'id' return value
        # id = sql where field = value
        # return id
        pass

    def get_song_by_title(self, title):
        self.get_song(field='title',value=title)

    def get_song_by_artist(self, artist):
        self.get_song(field='artist',value=artist)

    def get_song_by_periodogram(self, periodogram):
        self.get_song(field='periodogram',value=periodogram)

    def view_library(self):
        # select some fun stuff out the lib
        pass

    def get_all_signatures(self, signature_type):
        """
            grab all the signatures of a given kind i.e.
        :return:
        """

    def view_spectrogram(self, song_id, period=(0,-1)):
        """
            select all the periodograms associated with song_id, and then
        :param song_id:
        :param period:
        :return:
        """


class CannotAddDuplicateRecords(Exception):
    """ Field is already populted, cannot add new record """


class MultipleRecordsFound(Exception):
    """ error if we are looking for 1 record but found multiple """

class NoRecordsFound(Exception):
    """ No records found but we were lookig for something.... """

