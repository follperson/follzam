from follzam import VALID_FILE_TYPES, basepath
from follzam.IO_methods import *
from follzam.exceptions import NoResults
import follzam.database_management as dbm
import follzam.SignalProcessing as sp
from follzam import TABLE_NAMES, GENRES, SIGNALTYPES, logging
from follzam.DatabaseInfo import create_full_schema, drop_tables, create_signature
import os
import pandas as pd

logger = logging.getLogger(__name__)

def make_database(dbh=None,delete=False):
    """
        This function will create and optionally delete the entire database schema.
    :param dbh: database handler object - if we have already established a connection, just use that one
    :param delete: boolean, True if you want to delete the database schema, False if not. Default False
    :return: None
    """
    if dbh is None:
        dbh = dbm.DatabaseHandler()

    if delete:
        logger.info('Deleting Previous Database Schema')
        dbh.cur.execute(drop_tables)

    logger.info('Creating New Database Schema')
    dbh.cur.execute(create_full_schema)

    logger.info('Loading {} Database Table'.format(TABLE_NAMES.SIGNATURE_TYPES))
    with open(os.path.join(basepath, 'assets/signature_types.sql'),'r') as sql_f:
        sql = sql_f.read()
    dbh.cur.execute(sql.format(TABLE_NAMES.SIGNATURE_TYPES, ', '.join(['(%s)'] * len(SIGNALTYPES.ALL))),
                    SIGNALTYPES.ALL)

    logger.info('Loading {} Database Table'.format(TABLE_NAMES.FILE_TYPE))
    with open(os.path.join(basepath, 'assets/file_types.sql'),'r') as file_f:
        sql = file_f.read()
    dbh.cur.execute(sql.format(TABLE_NAMES.FILE_TYPE, ', '.join(['(%s)']*len(VALID_FILE_TYPES))), VALID_FILE_TYPES)

    logger.info('Loading {} Database Table'.format(TABLE_NAMES.GENRE))
    with open(os.path.join(basepath, 'assets/genres.sql'),'r') as genres:
        sql = genres.read()
    dbh.cur.execute(sql.format(TABLE_NAMES.GENRE, ', '.join(['(%s)']*len(GENRES))), GENRES)


def initialize(signal_processor=sp.SignalProcessorSpectrogram):
    """
        Initialize the database, the
    :return:
    """
    logger.info('Begin Initialization')

    sig_db = dbm.DatabaseHandler()
    make_database(sig_db, True)

    df_song_info = load_starter_database_data(sig_db)
    logger.info('Begin Signature Loading')
    for i in df_song_info.index:
        filesource, name, artist, album = df_song_info.loc[i, ['filesource', 'name', 'artist_id','album_id']]
        rad = ReadAudioData(filesource)  # transform song to wav
        sigp = signal_processor(audio_array=rad.array,
                       sample_freq=rad.audio.frame_rate,
                       songinfo={'artist_id': artist, 'album_id': album, 'filesource': filesource, 'name': name})
        try:
            sigp.compute_signature()
        except sp.NoSignatures:
            print("No Signature found for this song")
            continue
        sigp.load_signature(sig_db)


def load_starter_database_data(sig_db, load=True):
    df_artist_info = pd.read_csv(os.path.join(basepath, 'assets/metadata/artists.csv'))
    df_album_info = pd.read_csv(os.path.join(basepath, 'assets/metadata/album.csv'))

    logger.info('Loading {} Database Table'.format(TABLE_NAMES.ARTIST))
    if load:
        df_artist_info.to_sql(name=TABLE_NAMES.ARTIST, con=sig_db.cur, if_exists='append', index=False)

    logger.info('Loading {} Database Table'.format(TABLE_NAMES.ALBUM))
    df_album_info['artist_id'] = df_album_info['artist_name'].apply(lambda x: sig_db.get_artist_id(name=x))
    if load:
        df_album_info[['name', 'year', 'artist_id', 'genre_id']].to_sql(name=TABLE_NAMES.ALBUM, con=sig_db.cur,
                                                                        if_exists='append', index=False)

    logger.info('Loading {} Database Table'.format(TABLE_NAMES.SONG))

    path_to_songs = os.path.join(basepath, 'assets/audio')
    songs = [os.path.join(root, f) for root, dirs, files in os.walk(path_to_songs) for f in files]
    df_song_info = pd.DataFrame(data=songs, columns=['filesource'])
    df_song_info = df_song_info[df_song_info['filesource'].str.split('.').str[-1].str.upper().isin(VALID_FILE_TYPES)]
    df_song_info['album_name'] = df_song_info['filesource'].str.split('\\').str[-2]
    df_song_info['artist_name'] = df_song_info['filesource'].str.split('\\').str[-3]
    df_song_info['name'] = df_song_info['filesource'].str.split('\\').str[-1].str.split('.').str[:-1].str.join('.')
    df_song_info['album_id'] = df_song_info['album_name'].apply(lambda x: sig_db.get_album_id(name=x))
    df_song_info['artist_id'] = df_song_info['artist_name'].apply(lambda x: sig_db.get_artist_id(name=x))
    if load:
        df_song_info[['name', 'filesource', 'album_id', 'artist_id']].to_sql(name=TABLE_NAMES.SONG, con=sig_db.cur,
                                                                             if_exists='append', index=False)

    return df_song_info


def continue_loading_signatures(signal_processor=sp.SignalProcessorSpectrogram):
    """
        Initialize the database, the
    :return:
    """
    logger.info('Begin Initialization continuation')
    sig_db = dbm.DatabaseHandler()
    df_song_info = load_starter_database_data(sig_db, False)
    logger.info('Begin Signature Loading')
    for i in df_song_info.index:
        filesource, name, artist, album = df_song_info.loc[i, ['filesource', 'name', 'artist_id', 'album_id']]
        try:
            sig_db.get_one_song(artist_id=artist, album_id=album,name=name)
            continue
        except NoResults as good:
            pass
        rad = ReadAudioData(filesource)  # transform song to wav
        sigp = signal_processor(audio_array=rad.array,
                                sample_freq=rad.audio.frame_rate,
                                songinfo={'artist_id': artist, 'album_id': album, 'filesource': filesource,
                                          'name': name})
        sigp.compute_signature()
        sigp.load_signature(sig_db)


def main():
    initialize(sp.SignalProcessorSpectrogram)
    # load_signatures(sp.SignalProcessorSpectrogram)
    # continue_loading_signatures()
    pass


if __name__ == '__main__':
    main()
