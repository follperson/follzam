import assets.db_access_info as credentials
from IO_methods import VALID_FILE_TYPES
import pandas as pd
import sqlalchemy
import SignalProcessing
from exceptions import *
GENRES = ['Indie Rock','Rap','Classical','Jazz']
import numpy
from psycopg2.extensions import register_adapter, AsIs

# https://github.com/openego/ego.io/commit/8e7c64e0e9868b9bbc3156c70f6c368cad427f1f
def adapt_numpy_int64(numpy_int64):
    """ Adapting numpy.int64 type to SQL-conform int type using psycopg extension, see [1]_ for more info.
    References
    ----------
    .. [1] http://initd.org/psycopg/docs/advanced.html#adapting-new-python-types-to-sql-syntax
    """
    return AsIs(numpy_int64)


register_adapter(numpy.int64, adapt_numpy_int64)


def get_access_info():
    return {'user':credentials.username,
            'password':credentials.password,
            'host':credentials.host,
            'dbname':'afollman'}


def get_engine():
    info = get_access_info()
    engine = sqlalchemy.create_engine('postgresql://' + info['user'] + ':' + info['password'] + '@' + info['host'])
    engine.connect()
    return engine

# tests for oridnary ufcntions are separrate from dbquerying tests
# pytests can be expected to fail or have skip logic


class DatabaseInfo: # todo maybe put these into a sql folder and do away with the class.
                    # wondering how i would manage the formating though...
    """ This Class is a persistent variable store for the SQL accessors.
        It does not do anything by itself, but it is used by the other programs when creating the database,
        or updating the tables.
    """

    class TABLE_NAMES:
        GENRE = 'follzam_genre'
        ALBUM = 'follzam_album'
        ARTIST = 'follzam_artist'
        SONG = 'follzam_song'
        SONG_DATA = 'follzam_songdata'
        SIGNATURE = 'follzam_signature'
        SIGNATURE_TYPES = 'follzam_signaturetypes' # in case we want to test out multiple signatures
        FILE_TYPE = 'follzam_filetype' # for binary data storage and spectrogram recreation
        SIGNATURE_MATCH = 'follzam_signature_matches'
        MATCH_ATTEMPT = 'follzam_match_attempts'

        ALL = [GENRE, ALBUM, ARTIST, SONG, SONG_DATA, SIGNATURE, SIGNATURE_TYPES, FILE_TYPE, SIGNATURE_MATCH, MATCH_ATTEMPT]

    create_artist = """CREATE TABLE {} ( 
       id SERIAL PRIMARY KEY, 
       name TEXT UNIQUE
       );
    """.format(TABLE_NAMES.ARTIST)

    create_genre = """CREATE TABLE {} (
        id SERIAL PRIMARY KEY, 
        name text UNIQUE
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
        filesource text,
        artist_id integer REFERENCES {} (id),
        album_id integer REFERENCES {} (id),
        UNIQUE (name, artist_id, album_id)
        );
    """.format(TABLE_NAMES.SONG, TABLE_NAMES.ARTIST, TABLE_NAMES.ALBUM)

    create_songdata = """CREATE TABLE {} (
        id SERIAL PRIMARY KEY,
        song_id integer REFERENCES {} (id) NOT NULL,
        filetype_id integer REFERENCES {} (id) NOT NULL,
        framerate integer NOT NULL,
        channels integer NOT NULL,
        data bytea NOT NULL
        );
    """.format(TABLE_NAMES.SONG_DATA, TABLE_NAMES.SONG, TABLE_NAMES.FILE_TYPE)

    create_file_types = """CREATE TABLE {} ( 
        id SERIAL PRIMARY KEY,
        name text NOT NULL
        );
    """.format(TABLE_NAMES.FILE_TYPE)

    create_signature_types = """CREATE TABLE {} ( 
        id SERIAL PRIMARY KEY,
        name text NOT NULL
        );
    """.format(TABLE_NAMES.SIGNATURE_TYPES)
    #
    # create_signature = """CREATE TABLE {} (
    #             time_index integer NOT NULL,
    #             frequency integer NOT NULL,
    #             signature varchar(32) NOT NULL,
    #             method_id integer REFERENCES {} (id) NOT NULL,
    #             song_id integer REFERENCES {} (id) NOT NULL,
    #             PRIMARY KEY (song_id, method_id, time_index, frequency)
    #             );
    #         """.format(TABLE_NAMES.SIGNATURE, TABLE_NAMES.SIGNATURE_TYPES, TABLE_NAMES.SONG)
    # create_signature_match = """CREATE TABLE {} (
    #             match_id integer REFERENCES {} (id) NOT NULL,
    #             frequency integer NOT NULL,
    #             signature varchar(32) NOT NULL,
    #             PRIMARY KEY (match_id, frequency, signature)
    #             );
    #         """.format(TABLE_NAMES.SIGNATURE_MATCH, TABLE_NAMES.MATCH_ATTEMPT)

    ## should I add and OPTIONS column to specify and arguments which got passed?
    ## maybe i can pass that to the signature types part...?
    # create_signature = """CREATE TABLE {} (
    #     time_index integer NOT NULL,
    #     frequency integer NOT NULL,
    #     signature integer NOT NULL,
    #     method_id integer REFERENCES {} (id) NOT NULL,
    #     song_id integer REFERENCES {} (id) NOT NULL,
    #     PRIMARY KEY (song_id, method_id, time_index, frequency)
    #     );
    # """.format(TABLE_NAMES.SIGNATURE, TABLE_NAMES.SIGNATURE_TYPES, TABLE_NAMES.SONG)

    create_signature = """CREATE TABLE {} (
            time_index integer NOT NULL,
            frequency integer,
            signature integer NOT NULL,
            method_id integer REFERENCES {} (id) NOT NULL,
            song_id integer REFERENCES {} (id) NOT NULL,
            PRIMARY KEY (song_id, method_id, time_index, signature)
            );
        """.format(TABLE_NAMES.SIGNATURE, TABLE_NAMES.SIGNATURE_TYPES, TABLE_NAMES.SONG)


    create_signature_match = """CREATE TABLE {} (
        match_id integer REFERENCES {} (id) NOT NULL,
        frequency integer NOT NULL,
        signature integer NOT NULL,
        PRIMARY KEY (match_id, frequency, signature)
        );
    """.format(TABLE_NAMES.SIGNATURE_MATCH, TABLE_NAMES.MATCH_ATTEMPT)

    create_match = """CREATE TABLE {} (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        predicted_song_id integer REFERENCES {} (id),
        true_song_id integer REFERENCES {} (id),
        method_id integer REFERENCES {} (id) NOT NULL
        );
    """.format(TABLE_NAMES.MATCH_ATTEMPT, TABLE_NAMES.SONG, TABLE_NAMES.SONG, TABLE_NAMES.SIGNATURE_TYPES)

    create_full_schema = '\n '.join(
        [create_file_types, create_signature_types, create_artist, create_genre, create_album, create_song,
         create_songdata, create_signature, create_match, create_signature_match])

    drop_tables = 'DROP TABLE IF EXISTS ' + ' CASCADE;\nDROP TABLE IF EXISTS '.join(TABLE_NAMES.ALL) + ' CASCADE;'


def initialize_database(dbh=None,delete=False):  # maybe I should put this somewhere else
    """
        This function will create and optionally delete the entire database schema.
    :param dbh: database handler object - if we have already established a connection, just use that one
    :param delete: boolean, True if you want to delete the database schema, False if not. Default False
    :return: None
    """
    if dbh is None:
        dbh = DatabaseHandler()

    if delete:
        dbh.cur.execute(DatabaseInfo.drop_tables)
    dbh.cur.execute(DatabaseInfo.create_full_schema)

    with open('assets/signature_types.sql','r') as sql_f:
        sql = sql_f.read()
    dbh.cur.execute(sql.format(DatabaseInfo.TABLE_NAMES.SIGNATURE_TYPES,
                               ', '.join(['(%s)']*len(SignalProcessing.SignalProcessor.SIGNALTYPES.ALL))),
                    SignalProcessing.SignalProcessor.SIGNALTYPES.ALL)

    with open('assets/file_types.sql','r') as file_f:
        sql = file_f.read()
    dbh.cur.execute(sql.format(DatabaseInfo.TABLE_NAMES.FILE_TYPE,
                               ', '.join(['(%s)']*len(VALID_FILE_TYPES))),
                    VALID_FILE_TYPES)

    with open('assets/genres.sql','r') as genres:
        sql = genres.read()
    dbh.cur.execute(sql.format(DatabaseInfo.TABLE_NAMES.GENRE,
                               ', '.join(['(%s)']*len(GENRES))),
                    GENRES)


class DatabaseHandler(object):
    """
        This class managages the access and updates to SQL
    """

    def __init__(self):
        """
            initialize a database connection
        """
        self.cur = get_engine()
        self.con = self.cur.connect()

    def execute_query(self, query, params=None):
        # try:
        return self.cur.execute(query, params)
        # except psql.errors.InFailedSQLTransaction:
        #     self.cur.execute('rollback')
        #     self.cur.execute(query, vars=params)

    def _generic_insert(self, table, insert_kv):
        assert table in DatabaseInfo.TABLE_NAMES.ALL
        ks, vs = self.get_key_val_list(insert_kv)
        sql = 'INSERT INTO {} ({}) VALUES ({})'.format(table, ', '.join(ks), ', '.join(['%s']*len(vs)))
        self.cur.execute(sql, vs)

    def _song_where_check(self, **kwargs):
        if 'album' in kwargs:
            if not isinstance(kwargs['album'], int):
                album = kwargs.pop('album')
                album_id = self.get_album_id(**{'name': album})
                kwargs.update({'album_id':album_id})
        if 'artist' in kwargs:
            if not isinstance(kwargs['artist'], int):
                artist = kwargs.pop('artist')
                artist_id = self.get_artist_id(**{'name':artist})
                kwargs.update({'artist_id': artist_id})
        return kwargs

    def add_song(self, **kwargs):
        kwargs = self._song_where_check(**kwargs)
        try:
            self.get_song(**kwargs)

            raise CannotAddDuplicateRecords
        except NoResults as good:
            pass
        self._generic_insert(DatabaseInfo.TABLE_NAMES.SONG, kwargs)

    def remove_artist(self, **kwargs):
        artist_id = self.get_artist_id(**kwargs)
        try:
            self.get_song(artist_id=artist_id)
            raise CannotDeleteLinkedData
        except NoResults as ok:
            pass
        try:
            self.get_album(artist_id=artist_id)
            raise CannotDeleteLinkedData
        except NoResults as ok:
            pass
        self._remove_generic_by_id(DatabaseInfo.TABLE_NAMES.ARTIST, artist_id)

    def add_artist(self, **kwargs):
        try:
            self.get_artist(**kwargs)
            raise CannotAddDuplicateRecords
        except NoResults as good:
            pass
        self._generic_insert(DatabaseInfo.TABLE_NAMES.ARTIST, insert_kv=kwargs)

    def add_album(self, **kwargs):
        if 'artist' in kwargs:
            artist = kwargs.pop('artist')
            artist_id = self.get_artist_id(name=artist)
            kwargs.update({'artist_id': artist_id})
        try:
            self.get_album(**kwargs)
            raise CannotAddDuplicateRecords
        except NoResults as good:
            pass
        self._generic_insert(DatabaseInfo.TABLE_NAMES.ALBUM, insert_kv=kwargs)

    def get_album_id(self, **where):  # searching
        albums = self.get_album(**where)
        if len(albums) > 1:
            raise TooManyResults
        return albums[0]['id']

    def get_total_signatures_for_given_song(self, method_id, song_id):
        query = 'SELECT count(time_index) FROM {} WHERE method_id=%s AND song_id=%s;'.format(
            DatabaseInfo.TABLE_NAMES.SIGNATURE)
        return self.con.execute(query, (method_id, song_id)).fetchone()[0]

    def remove_album(self, **kwargs):
        album_id = self.get_album_id(**kwargs)
        try:
            self.get_song(album_id=album_id)
            raise CannotDeleteLinkedData
        except NoResults:
            pass
        self._remove_generic_by_id(DatabaseInfo.TABLE_NAMES.ALBUM, album_id)

    def remove_song(self, **kwargs):
        """
        :param name: name of song to be removed
        :return: nothing
        """
        song = self.get_one_song(**kwargs)
        self._remove_generic_by_id(DatabaseInfo.TABLE_NAMES.SONG, song)

    def _remove_generic_by_id(self, table, id):
        assert table in DatabaseInfo.TABLE_NAMES.ALL
        sql = 'DELETE FROM {} WHERE id=%s'.format(table)
        self.execute_query(sql, (id,))

    def list_songs(self):
        self.get_song('*')
        pass

    def get_formatted_song_info(self, song_id):
        query = """SELECT {}.name, {}.name, {}.name FROM {} 
                    INNER JOIN {} on {}.artist_id = {}.id 
                    INNER JOIN {} on {}.album_id={}.id 
                    WHERE {}.id=%s""".format(
            DatabaseInfo.TABLE_NAMES.SONG, DatabaseInfo.TABLE_NAMES.ARTIST, DatabaseInfo.TABLE_NAMES.ALBUM, DatabaseInfo.TABLE_NAMES.SONG,
            DatabaseInfo.TABLE_NAMES.ARTIST, DatabaseInfo.TABLE_NAMES.SONG, DatabaseInfo.TABLE_NAMES.ARTIST,
            DatabaseInfo.TABLE_NAMES.ALBUM, DatabaseInfo.TABLE_NAMES.SONG, DatabaseInfo.TABLE_NAMES.ALBUM
            , DatabaseInfo.TABLE_NAMES.SONG
        )
        return self.cur.execute(query, (song_id,)).fetchone()

    def get_one_song(self,*cols, **where):
        songs = self.get_song(*cols, **where)
        if len(songs) > 1:
            raise TooManyResults
        return songs[0]

    def get_song_id(self, **where):
        return self.get_one_song('id', **where)['id']

    @staticmethod
    def get_key_val_list(dict_to_unpack):
        dict_as_list = [(k, v) for k, v in dict_to_unpack.items()]
        return zip(*dict_as_list)

    def _generic_select(self, table, *cols_to_select, **where):
        assert table in DatabaseInfo.TABLE_NAMES.ALL
        if len(cols_to_select) == 0:
            cols_to_select = ('id',)
        if len(where) == 0:
            where = {'1': 1}  # select everything
        ks, vs = self.get_key_val_list(where)
        sql = 'SELECT {} FROM {} WHERE {}=%s'.format(', '.join(cols_to_select), table, '=%s and '.join(ks))
        resp = self.execute_query(sql, vs)
        vals = resp.fetchall()
        if len(vals) == 0:
            raise NoResults
        return vals

    def get_song(self, *cols, **where):  # searching
        where = self._song_where_check(**where)
        songs = self._generic_select(DatabaseInfo.TABLE_NAMES.SONG, *cols, **where)
        return songs

    def _album_where_check(self, **kwargs):
        if 'artist' in kwargs:
            artist_name = kwargs.pop('artist')
            artist_id = self.get_artist_id(name=artist_name)
            kwargs.update({'artist_id':artist_id})
        return kwargs

    def get_album(self, *cols, **where):  # searching
        where = self._album_where_check(**where)
        albums = self._generic_select(DatabaseInfo.TABLE_NAMES.ALBUM, *cols, **where)
        return albums

    def get_artist(self, *cols, **where):  # searching
        artists = self._generic_select(DatabaseInfo.TABLE_NAMES.ARTIST, *cols, **where)
        return artists

    def get_artist_by_id(self, artist_id, *cols):  # searching
        artists = self.get_artist(DatabaseInfo.TABLE_NAMES.ARTIST, *cols, id=artist_id)
        if len(artists) > 1:
            raise TooManyResults
        return artists[0]

    def get_artist_id(self, **where):  # searching
        artists = self.get_artist(**where)
        if len(artists) > 1:
            raise TooManyResults
        return artists[0]['id']

    def get_signature_type_by_id(self, id):
        sig_type = self._generic_select(DatabaseInfo.TABLE_NAMES.SIGNATURE_TYPES, 'name', id=id)
        return sig_type[0]['name']

    def get_signature_id_by_name(self, name):
        sig_type = self._generic_select(DatabaseInfo.TABLE_NAMES.SIGNATURE_TYPES, 'id', name=name)
        return sig_type[0]['id']

    def get_song_by_name(self, name, *cols_to_select):
        return self.get_song(*cols_to_select, name=name)

    def get_song_by_artist(self, artist, cols_to_select=('id',)):
        return self.get_song(cols_to_select, artist=artist)

    def summary(self):
        sql_songs = """SELECT count(id), artist.name 
                        from {}
                        inner join 
                        songs.artist_id=artist.id 
                        group by artist_id;""".format(DatabaseInfo.TABLE_NAMES.SONG)
        sql_signatures = """select count(unique song_id) from {}""".format(DatabaseInfo.TABLE_NAMES.SIGNATURE)
        print(self.execute_query(sql_songs))
        print(self.execute_query(sql_signatures))

    def get_signatures_by_type_name(self, name):
        """
            grab all the signatures of a given kind i.e.
        :return:
        """
        sig_id = self.get_signature_id_by_name(name)
        return self._generic_select(DatabaseInfo.TABLE_NAMES.SIGNATURE, '*', method_id=sig_id)

    def view_spectrogram(self, song_id, period=(0, -1)):
        """
            select all the periodograms associated with song_id, and then
        :param song_id:
        :param period:
        :return:
        """

    def load_signal(self, sigp):
        """
            take signal processer object and
        :param sigp:
        :return:
        """
        # n = len(sigp.windows)
        keys = list(sigp.signature_info.keys()) + ['song_id','method_id']
        song_id = self.get_song_id(**sigp.songinfo)
        sig_type_id = self.get_signature_id_by_name(sigp.method)
        # update = []

        # todo put this into a tsql
        print("begin loading of signature for ",sigp.songinfo)
        for i, time_index in enumerate(sigp.signature_info['time_index']):
            df = pd.DataFrame(zip(sigp.signature_info['frequency'][i], sigp.signature_info['signature'][i]),
                              columns=['frequency', 'signature'])
            df['time_index'] = time_index
            df['song_id'] = song_id
            df['method_id'] = sig_type_id
            update = tuple(tuple(i) for i in df[keys].values)
            sql_base = 'INSERT INTO {} ({}) VALUES {};'.format(DatabaseInfo.TABLE_NAMES.SIGNATURE, ', '.join(keys), ', '.join(['(%s, %s, %s, %s, %s)']*len(update)))
            self.execute_query(sql_base, tuple(i for l in update for i in l))
