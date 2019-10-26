import psycopg2 as psql
import assets.db_access_info as credentials
from SignalProcessing import *
from exceptions import *

def get_access_info():
    return {'user':credentials.username,
            'password':credentials.password,
            'host':credentials.host,
            'dbname':'afollman'}
    pass

class DatabaseInfo:
    """ basically a dictionary to access some static database table names and such """

    class TABLE_NAMES:
        GENRE = 'FOLLZAM_GENRE'
        ALBUM = 'FOLLZAM_ALBUM'
        ARTIST = 'FOLLZAM_ARTIST'
        SONG = 'FOLLZAM_SONG'
        SONG_DATA = 'FOLLZAM_SONGDATA'
        SIGNATURE = 'FOLLZAM_SIGNATURE'
        SIGNATURE_TYPES = 'FOLLZAM_SIGNATURETYPES' # in case we want to test out multiple signatures
        FILE_TYPE = 'FOLLZAM_FILETYPE' # for binary data storage and spectrogram recreation

        ALL = [GENRE, ALBUM, ARTIST, SONG, SONG_DATA, SIGNATURE, SIGNATURE_TYPES, FILE_TYPE]

    create_artist = """CREATE TABLE {} ( 
       id SERIAL PRIMARY KEY, 
       name TEXT UNIQUE
       );
    """.format(TABLE_NAMES.ARTIST)

    create_genre = """CREATE TABLE {} (
        id SERIAL PRIMARY KEY, 
        GENRE text UNIQUE
        );
    """.format(TABLE_NAMES.GENRE)

    create_album = """CREATE TABLE {} ( 
        id SERIAL PRIMARY KEY, 
        name text,
        year integer,
        artist_id integer REFERENCES {} (id),
        genre_id integer REFERENCES {} (id)
        );
    """.format(TABLE_NAMES.ALBUM, TABLE_NAMES.ARTIST, TABLE_NAMES.GENRE)

    create_song = """CREATE TABLE {} ( 
        id SERIAL PRIMARY KEY, 
        name text NOT NULL,
        year integer,
        filesource text,
        artist_id integer REFERENCES {} (id),
        album_id integer REFERENCES {} (id),
        UNIQUE (name, artist_id, album_id)
        );
    """.format(TABLE_NAMES.SONG, TABLE_NAMES.ARTIST, TABLE_NAMES.ALBUM)

    create_songdata = """CREATE TABLE {} (
        id SERIAL PRIMARY KEY,
        song_id REFERENCES {} (id) NOT NULL,
        filetype_id REFERENCES {} (id) NOT NULL,
        framerate INTEGER NOT NULL,
        channels INTEGER NOT NULL,
        data bytea NOT NULL
        );
    """.format(TABLE_NAMES.SONG_DATA, TABLE_NAMES.SONG,TABLE_NAMES.FILE_TYPE)

    create_file_types = """CREATE TABLE {} ( 
        id SERIAL PRIMARY KEY,
        name text NOT NULL
        );
    """.format(TABLE_NAMES.SIGNATURE_TYPES)

    create_signature_types = """CREATE TABLE {} ( 
        id SERIAL PRIMARY KEY,
        name text NOT NULL
        );
    """.format(TABLE_NAMES.SIGNATURE_TYPES)

    create_signature = """CREATE TABLE {} (
        time_index integer NOT NULL,
        frequency integer NOT NULL,
        signature integer NOT NULL,
        method_id integer REFERENCES {} (id) NOT NULL,
        song_id integer REFERENCES {} (id) NOT NULL,
        PRIMARY KEY (song_id, method_id, time_index, frequency)
        );
    """.format(TABLE_NAMES.SIGNATURE, TABLE_NAMES.ARTIST, TABLE_NAMES.ALBUM)

    create_full_schema = '\n '.join(
        [create_file_types, create_signature_types, create_artist, create_genre, create_album, create_song,
         create_songdata, create_signature])



class DatabaseHandler(object):
    """
        class managing database update / retrieval procedure
    """

    def __init__(self):
        """
            initialize a database connection
        """
        access_info = get_access_info()
        conn = psql.connect(**access_info)
        self.con = conn
        self.cur = conn.cursor()

    def execute_query(self, query, params=None):
        try:
            self.cur.execute(query, vars=params)
        except psql.errors.InFailedSQLTransaction:
            self.cur.execute('rollback')
            self.cur.execute(query, vars=params)

    def _generic_insert(self, table, insert_kv):
        assert table in DatabaseInfo.TABLE_NAMES.ALL
        ks, vs = self.get_key_val_list(insert_kv)
        sql = 'INSERT INTO {} ({}) VALUES ({})'.format(table, ', '.join(ks), ', '.join(['%s']*len(vs)))
        self.cur.execute(sql, vs)

    def add_song(self, **kwargs):
        try:
            self.get_song(where=kwargs)
            raise TooManyResults
        except NoResults as good:
            pass
        self._generic_insert(DatabaseInfo.TABLE_NAMES.SONG, kwargs)

    def add_artist(self, **kwargs):
        try:
            self.get_artist(where=kwargs)
            raise TooManyResults
        except NoResults as good:
            pass
        self._generic_insert(DatabaseInfo.TABLE_NAMES.ARTIST, insert_kv=kwargs)

    def add_album(self, **kwargs):
        try:
            self.get_album(where=kwargs)
            raise TooManyResults
        except NoResults as good:
            pass
        self._generic_insert(DatabaseInfo.TABLE_NAMES.ALBUM, insert_kv=kwargs)

    def remove_song(self, **kwargs):
        """
        :param name: name of song to be removed
        :return: nothing
        """
        song = self.get_one_song(where=kwargs)
        self._remove_generic_by_id(DatabaseInfo.TABLE_NAMES.SONG, song)

    def _remove_generic_by_id(self, table, id):
        assert table in DatabaseInfo.TABLE_NAMES.ALL
        sql = 'DELETE FROM {} WHERE id=%s'.format(table)
        self.cur.execute(sql, (id,))

    def list_songs(self):
        # df = read sql
        # print(df)
        pass

    def get_one_song(self, cols_to_select=('id',), where=None):
        songs = self.get_song(cols_to_select, where)
        if len(songs) > 1:
            raise TooManyResults
        return songs[0]

    @staticmethod
    def get_key_val_list(dict_to_unpack):
        dict_as_list = [(k, v) for k, v in dict_to_unpack.items()]
        return zip(*dict_as_list)

    def _generic_select(self, table, cols_to_select, where=None):
        assert table in DatabaseInfo.TABLE_NAMES.ALL
        if where is None:
            ks, vs = (1,), (1,)
        else:
            ks, vs = self.get_key_val_list(where)
        sql = 'SELECT {} FROM {} WHERE {}=%s'.format(', '.join(cols_to_select), table, '=%s and '.join(ks))
        self.cur.execute(sql, vs)
        vals = self.cur.fetchall()
        if len(vals) == 0:
            raise NoResults
        return vals

    def get_song(self, cols_to_select=('id',), where=None):  # searching
        songs = self._generic_select(DatabaseInfo.TABLE_NAMES.SONG, cols_to_select, where)
        return songs

    def get_album(self, cols_to_select=('id',), where=None):  # searching
        albums = self._generic_select(DatabaseInfo.TABLE_NAMES.ALBUM, cols_to_select, where)
        return albums

    def get_artist(self, cols_to_select=('id',), where=None):  # searching
        artists = self._generic_select(DatabaseInfo.TABLE_NAMES.ARTIST, cols_to_select, where)
        return artists

    def get_song_by_title(self, title, cols_to_select=('id',)):
        return self.get_song(cols_to_select, where={'title':title})

    def get_song_by_artist(self, artist, cols_to_select=('id',)):
        return self.get_song(cols_to_select, {'artist': artist})

    def summary(self):
        sql_songs = """SELECT count(id), artist.name 
                        from {}
                        inner join 
                        songs.artist_id=artist.id 
                        group by artist_id;""".format(DatabaseInfo.TABLE_NAMES.SONG)
        sql_signatures = """select count(unique song_id) from {}""".format(DatabaseInfo.TABLE_NAMES.SIGNATURE)
        print(self.execute_query(sql_songs))
        print(self.execute_query(sql_signatures))

    def get_all_signatures(self, signature_type):
        """
            grab all the signatures of a given kind i.e.
        :return:
        """
        pass

    def view_spectrogram(self, song_id, period=(0, -1)):
        """
            select all the periodograms associated with song_id, and then
        :param song_id:
        :param period:
        :return:
        """
