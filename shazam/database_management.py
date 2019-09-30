


class DatabaseHandler():
    """
        class managing database update procedures
    """

    def __init__(self, access_info):
        """
            use access_info to create connection with db
        :param access_info:
        """
        pass

    def initialize_database(self):
        """ run through """

    def add_song(self, wav, metadata):
        # check if song already there
        # try: self.get_song
        # except cannot find
        #
        #features  = extract_features(wav)
        pass

    def remove_song(self, name):
        # find id
        # remove entry
        pass

    def list_songs(self):
        # df = read sql
        # print(df)
        pass

    def get_song(self, field, value):
        # if field = 'id' return value
        # id = sql where field = value
        #
        pass

    def compute_signature(self):
        # for i in ids:
        #   wav = get_wav
        #   signature = get_signature(wav)
        #
        # read_sql
        pass
