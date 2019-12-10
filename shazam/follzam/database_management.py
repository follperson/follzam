import assets.db_access_info as credentials
from follzam import basepath
import sqlalchemy
from follzam.exceptions import *
from follzam import TABLE_NAMES
import numpy
from psycopg2.extensions import register_adapter, AsIs
import logging
logger = logging.getLogger(__name__)

# todo: update, remove

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
        return self.cur.execute(query, params)

    def _generic_insert(self, table, insert_kv):
        """
            generic insert, useful to manage errors and logging
        :param table: table we are inserting to
        :param insert_kv: kew-value dictionary of insert column and values
        :return:
        """
        assert table in TABLE_NAMES.ALL, 'Table name {} is not in our database schema'.format(table)
        logger.info('Inserting into {} {} values'.format(table, len(insert_kv)))
        ks, vs = self._get_key_val_list(insert_kv)
        sql = 'INSERT INTO {} ({}) VALUES ({})'.format(table, ', '.join(ks), ', '.join(['%s']*len(vs)))
        self.cur.execute(sql, vs)

    def _song_where_check(self, **kwargs):
        """
            check if we passed name arguments for album and artist, in which case we try to associate these with
            the database id for that name
        :param kwargs:
        :return:
        """
        if 'album' in kwargs:
            if not isinstance(kwargs['album'], int):
                logger.info('Substituting album ID for provided album name')
                album = kwargs.pop('album')
                album_id = self.get_album_id(**{'name': album})
                kwargs.update({'album_id':album_id})
        if 'artist' in kwargs:
            if not isinstance(kwargs['artist'], int):
                logger.info('Substituting artist ID for provided artist name')
                artist = kwargs.pop('artist')
                artist_id = self.get_artist_id(**{'name':artist})
                kwargs.update({'artist_id': artist_id})
        return kwargs

    def add_song(self, **kwargs):
        kwargs = self._song_where_check(**kwargs)
        try:
            self.get_song(**kwargs)
            raise CannotAddDuplicateRecords('You are trying to add a song which already exists in our database')
        except NoResults as good:
            pass
        self._generic_insert(TABLE_NAMES.SONG, kwargs)

    def remove_artist(self, **kwargs):
        """
            remove artist from database. Checks if there is linked data which would break upon deletion,
                throws errors if so
        :param kwargs: where clause
        :return:
        """
        artist_id = self.get_artist_id(**kwargs)
        try:
            self.get_song(artist_id=artist_id)
            raise CannotDeleteLinkedData('We cannot remove an artist which has associated songs!')
        except NoResults:
            pass

        try:
            self.get_album(artist_id=artist_id)
            raise CannotDeleteLinkedData('We cannot remove an artist which has associated albums!')
        except NoResults:
            pass

        self._remove_generic_by_id(TABLE_NAMES.ARTIST, artist_id)

    def add_artist(self, **kwargs):
        try:
            self.get_artist(**kwargs)
            raise CannotAddDuplicateRecords('You are trying to add an artist which already exists in our database')
        except NoResults as good:
            pass
        self._generic_insert(TABLE_NAMES.ARTIST, insert_kv=kwargs)

    def add_album(self, **kwargs):
        kwargs = self._album_where_check(**kwargs)
        try:
            self.get_album(**kwargs)
            raise CannotAddDuplicateRecords('You are trying to add an album which already exists in our database')
        except NoResults as good:
            pass
        self._generic_insert(TABLE_NAMES.ALBUM, insert_kv=kwargs)

    def get_album_id(self, **where):
        albums = self.get_album(**where)
        if len(albums) > 1:
            raise TooManyResults('We have too many albums with the associated where clause')
        return albums[0]['id']

    def get_total_signatures_for_given_song(self, method_id, song_id):
        query = 'SELECT count(time_index) FROM {} WHERE method_id=%s AND song_id=%s;'.format(TABLE_NAMES.SIGNATURE)
        return self.con.execute(query, (method_id, song_id)).fetchone()[0]

    def remove_album(self, **kwargs):
        album_id = self.get_album_id(**kwargs)
        try:
            self.get_song(album_id=album_id)
            raise CannotDeleteLinkedData('We cannot remove an album which has associated songs!')
        except NoResults:
            pass
        self._remove_generic_by_id(TABLE_NAMES.ALBUM, album_id)

    def remove_song(self, **kwargs):
        """
        :param kwargs: keyword identified where clause
        :return: nothing
        """
        song = self.get_one_song(**kwargs)
        self._remove_generic_by_id(TABLE_NAMES.SONG, song)

    def _remove_generic_by_id(self, table, id):
        """
            root delete call - passed an ID and a table name, we delete the id
        :param table: database table
        :param id: id to delete
        :return: None
        """
        assert table in TABLE_NAMES.ALL
        logger.info('Deleting id {} from table {}'.format(id, table))
        sql = 'DELETE FROM {} WHERE id=%s'.format(table)
        self.execute_query(sql, (id,))

    def list_songs(self):
        self.get_song('*')

    def get_formatted_song_info(self, song_id):
        """
            get the artist, album, and song name from a provided song_id
        :param song_id: song_id
        :return: artist_name, album_name, song_name
        """
        query = """SELECT {}.name, {}.name, {}.name FROM {} 
                    INNER JOIN {} on {}.artist_id = {}.id 
                    INNER JOIN {} on {}.album_id={}.id 
                    WHERE {}.id=%s""".format(
            TABLE_NAMES.SONG, TABLE_NAMES.ARTIST, TABLE_NAMES.ALBUM, TABLE_NAMES.SONG,
            TABLE_NAMES.ARTIST, TABLE_NAMES.SONG, TABLE_NAMES.ARTIST,
            TABLE_NAMES.ALBUM, TABLE_NAMES.SONG, TABLE_NAMES.ALBUM, TABLE_NAMES.SONG
        )
        return self.cur.execute(query, (song_id,)).fetchone()

    def get_one_song(self,*cols, **where):
        """
            wrapper for self.get_song, but throws an error if there are more than one results returned
        :param cols: cols to get
        :param where: filtering
        :return: cols for song
        """
        songs = self.get_song(*cols, **where)
        if len(songs) > 1:
            raise TooManyResults
        return songs[0]

    def get_song_by_id(self, song_id, *cols):
        return self.get_one_song(*cols, id=song_id)

    def get_album_by_id(self, album_id, *cols):
        return self.get_album(*cols, id=album_id)

    def get_song_id(self, **where):
        """
            simple method to get the song id given a generic where clause
        :param where:
        :return: song_id
        """
        return self.get_one_song('id', **where)['id']

    def _generic_update(self, table, id, **update):
        """
            base update function. unpacks **update into keys and values
        :param table: table to access
        :param id: the id to be updated (table dcependent)
        :param update: keyword arguments of the  columns and values to be updated
        :return: None
        """
        assert table in TABLE_NAMES.ALL, 'Table name {} is not valid'.format(table)
        assert len(update) > 0, 'No update keywords specified'

        logger.info("Updating id={} for table={}".format(id, table))
        ks, vs = self._get_key_val_list(update)
        sql = 'UPDATE {} SET {}=%s WHERE id=%s'.format(table, '=%s, '.join(ks))
        self.execute_query(sql, vs + (id,))

    def update_song(self, song_id, **update):
        """
            update a song given update keyword arguments
        :param song_id: song_id to be updated
        :param update: update keyword arguments
        :return: None
        """
        update = self._song_where_check(**update)  # make sure that the update clause is valid
        self.get_song_by_id(song_id=song_id)  # make sure our song is in the database
        self._generic_update(TABLE_NAMES.SONG, song_id, **update)

    def update_artist(self, artist_id, **update):
        """
            update an artist given update keyword arguments
        :param artist_id: id of artist to be updated
        :param update: update keyword arguments
        :return: None
        """
        self.get_artist_by_id(artist_id)  # make sure artist in table
        self._generic_update(TABLE_NAMES.ARTIST, artist_id, **update)

    def update_album(self, album_id, **update):
        """
            update an album given update keyword arguments
        :param album_id: song_id to be updated
        :param update: update keyword arguments
        :return: None
        """
        update = self._album_where_check(**update)  # make sure album update is valid
        self.get_album_by_id(album_id)  # make sure album is in database
        self._generic_update(TABLE_NAMES.ALBUM, album_id, **update)

    def update_signature_match_with_true_value(self, attempt_id,  **where):
        """
            for use when we know the true value (helpful for diagnostics and comparing methods)
        :param attempt_id: match_attempt id
        :param where: where clause for true song value
        :return: None
        """
        song_id = self.get_song_id(**where)
        self._generic_update(TABLE_NAMES.MATCH_ATTEMPT, attempt_id, true_song_id=song_id)

    @staticmethod
    def _get_key_val_list(dict_to_unpack):
        """
            unpacks a dictionary so it is two lists of equal length with values assoicated by index.
            needed to load to sql
        :param dict_to_unpack: key-val dictionary
        :return: unzipped dictionary
        """
        dict_as_list = [(k, v) for k, v in dict_to_unpack.items()]
        return zip(*dict_as_list)

    def _generic_select(self, table, *cols_to_select, **where):
        """
            base select accessor function. some checks on cols and where clause
        :param table: table to access
        :param cols_to_select:
        :param where:
        :return:
        """
        assert table in TABLE_NAMES.ALL
        if len(cols_to_select) == 0:  # if no columns are specified, we just select the id column
            cols_to_select = ('id',)
        if len(where) == 0:  # if no where clause specified then we assume we want to grab everything
            where = {'1': 1}
        ks, vs = self._get_key_val_list(where)
        sql = 'SELECT {} FROM {} WHERE {}=%s'.format(', '.join(cols_to_select), table, '=%s and '.join(ks))
        resp = self.execute_query(sql, vs)
        vals = resp.fetchall()
        if len(vals) == 0:
            raise NoResults
        return vals

    def get_song(self, *cols, **where):
        """
            generic get columns from song table where the where clause is met
        :param cols: cols to select
        :param where: key word arguments
        :return: songs
        """

        where = self._song_where_check(**where)
        songs = self._generic_select(TABLE_NAMES.SONG, *cols, **where)
        return songs

    def _album_where_check(self, **kwargs):
        """
            make sure that the keyword arguments in the album_where clause are valid. clean up common errors
        :param kwargs:
        :return:
        """
        if 'artist' in kwargs:
            artist_name = kwargs.pop('artist')
            artist_id = self.get_artist_id(name=artist_name)
            kwargs.update({'artist_id':artist_id})
        if 'genre' in kwargs:
            genre = kwargs.pop('genre')
            if genre is not None:
                genre_id = self.get_genre_id(name=genre, add=True)
                kwargs.update({'genre_id': genre_id})
        if 'year' in kwargs:
            if kwargs['year'] is None:
                kwargs.pop('year')
        return kwargs

    def get_album(self, *cols, **where):
        where = self._album_where_check(**where)
        albums = self._generic_select(TABLE_NAMES.ALBUM, *cols, **where)
        return albums

    def get_artist(self, *cols, **where):  # searching
        artists = self._generic_select(TABLE_NAMES.ARTIST, *cols, **where)
        return artists

    def get_artist_by_id(self, artist_id, *cols):  # searching
        artists = self.get_artist(TABLE_NAMES.ARTIST, *cols, id=artist_id)
        if len(artists) > 1:
            raise TooManyResults
        return artists[0]

    def get_artist_id(self, **where):
        artists = self.get_artist(**where)
        if len(artists) > 1:
            raise TooManyResults
        return artists[0]['id']

    def add_genre(self, name):
        try:
            self._generic_select(TABLE_NAMES.GENRE, 'id', name=name)
        except NoResults:
            self._generic_insert(TABLE_NAMES.GENRE, {'name': name})

    def get_genre_id(self, name, add=False):
        """
            get the genre id from the name of the genre. If add is true then we add it to the database
        :param name: genre name
        :param add: bool - if True then we put ensure the genre is in the database
        :return: genre id
        """
        if add:
            # add the genre to the database
            self.add_genre(name)
        try:
            genre_id = self._generic_select(TABLE_NAMES.GENRE, 'id', name=name)
        except NoResults:
            logger.error("Genre not found: {}".format(name))
            return 1
        return genre_id[0]['id']

    def get_signature_type_by_id(self, id):
        sig_type = self._generic_select(TABLE_NAMES.SIGNATURE_TYPES, 'name', id=id)
        return sig_type[0]['name']

    def get_signature_id_by_name(self, name):
        sig_type = self._generic_select(TABLE_NAMES.SIGNATURE_TYPES, 'id', name=name)
        return sig_type[0]['id']

    def get_song_by_name(self, name, *cols_to_select):
        return self.get_song(*cols_to_select, name=name)

    def get_song_by_artist(self, artist, cols_to_select=('id',)):
        return self.get_song(cols_to_select, artist=artist)

    def summary(self):
        """
            print our some basic information about our tables
        :return:
        """
        sql_songs = """SELECT count(id), artist.name 
                        from {}
                        inner join 
                        songs.artist_id=artist.id 
                        group by artist_id;""".format(TABLE_NAMES.SONG)
        sql_signatures = """select count(unique song_id) from {}""".format(TABLE_NAMES.SIGNATURE)
        print(self.execute_query(sql_songs))
        print(self.execute_query(sql_signatures))

    def get_signatures_by_type_name(self, name):
        """
            grab all the signatures of a given kind method name
        :return:
        """
        sig_id = self.get_signature_id_by_name(name)
        return self._generic_select(TABLE_NAMES.SIGNATURE, '*', method_id=sig_id)
