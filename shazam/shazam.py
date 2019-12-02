from IO_methods import *
import database_management as dbm
from sqlalchemy import create_engine
import SignalProcessing as sp
import os
import pandas as pd
import logging
import sys

logger = logging.getLogger('Shazam')
logger.setLevel(logging.INFO)

fh = logging.FileHandler('logs/Shazam.log')
fh.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


def initialize_database():
    sig_db = dbm.DatabaseHandler()
    logger.info('Established Database Connection')
    dbm.initialize_database(dbh=sig_db, delete=True)
    logger.info('Initialized New Database')
    return sig_db

def load_starter_database_data(sig_db):
    df_artist_info = pd.read_csv('assets/metadata/artists.csv')
    df_album_info = pd.read_csv('assets/metadata/album.csv')
    logger.info('Loading Initial Artists Begin')
    df_artist_info.to_sql(name=dbm.DatabaseInfo.TABLE_NAMES.ARTIST, con=sig_db.cur, if_exists='append', index=False)
    logger.info('...Loaded Initial Artists Complete')
    logger.info('Loading Initial Albums Begin')
    df_album_info['artist_id'] = df_album_info['artist_name'].apply(lambda x: sig_db.get_artist_id(name=x))
    df_album_info[['name', 'year', 'artist_id', 'genre_id']].to_sql(name=dbm.DatabaseInfo.TABLE_NAMES.ALBUM,
                                                                    con=sig_db.cur, if_exists='append', index=False)
    logger.info('...Loaded Initial Albums Complete')

    logger.info('Loading Initial Songs Begin')
    path_to_songs = 'assets/audio'
    songs = [os.path.join(root, f) for root, dirs, files in os.walk(path_to_songs) for f in files]
    df_song_info = pd.DataFrame(data=songs, columns=['filesource'])
    df_song_info = df_song_info[df_song_info['filesource'].str.split('.').str[-1].str.upper().isin(VALID_FILE_TYPES)]
    df_song_info['album_name'] = df_song_info['filesource'].str.split('\\').str[-2]
    df_song_info['artist_name'] = df_song_info['filesource'].str.split('\\').str[-3]
    df_song_info['name'] = df_song_info['filesource'].str.split('\\').str[-1].str.split('.').str[:-1].str.join('.')
    df_song_info['album_id'] = df_song_info['album_name'].apply(lambda x: sig_db.get_album_id(name=x))
    df_song_info['artist_id'] = df_song_info['artist_name'].apply(lambda x: sig_db.get_artist_id(name=x))
    df_song_info[['name', 'filesource', 'album_id', 'artist_id']].to_sql(name=dbm.DatabaseInfo.TABLE_NAMES.SONG,
                                                                         con=sig_db.cur, if_exists='append',
                                                                         index=False)
    logger.info('...Loaded Initial Songs Complete')
    return df_song_info

def initialize(SigProc=sp.SignalProcessorSpectrogram):
    """

    :return:
    """
    logger.info('Starting')
    sig_db = initialize_database()
    df_song_info = load_starter_database_data(sig_db)

    logger.info('Signature Loading Begin')
    for i in df_song_info.index:
        filesource, name, artist, album = df_song_info.loc[i, ['filesource', 'name', 'artist_id','album_id']]
        logger.info('Loading Signature for %s' % filesource)
        rad = ReadAudioData(filesource)  # transform song to wav
        sigp = SigProc(audio_array=rad.array,
                       sample_freq=rad.audio.frame_rate,
                       songinfo={'artist_id': artist, 'album_id': album, 'filesource': filesource, 'name': name})
        sigp.compute_signature()
        sigp.load_signature(sig_db)
        logger.info('Loading Signature for %s Completed' % filesource)
        # stick our signatures into the database, tied to song, albums, and
        # artists ids


def load_signatures(SigProc=sp.SignalProcessorExactMatch):
    sig_db = dbm.DatabaseHandler()
    path_to_songs = 'assets/audio/songs'
    songs = os.listdir(path_to_songs)
    df_song_info = pd.DataFrame(data=songs, columns=['name'])
    df_song_info['album_id'] = 1
    df_song_info['artist_id'] = 1
    df_song_info['filesource'] = df_song_info['name'].apply(lambda x: os.path.join(path_to_songs, x))
    sig_db.cur.execute('DROP TABLE IF EXISTS ' + dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE + ' CASCADE;')
    sig_db.cur.execute(dbm.DatabaseInfo.create_signature)
    for i in df_song_info.index:
        filesource, name, artist, album = df_song_info.loc[i, ['filesource', 'name', 'artist_id','album_id']]
        rad = ReadAudioData(os.path.join(path_to_songs, name))  # transform song to wav
        sigp = SigProc(audio_array=rad.array, sample_freq=rad.audio.frame_rate, songinfo={'artist_id': artist,
                                                                                          'album_id': album,
                                                                                          'filesource': filesource,
                                                                                          'name': name})
        sigp.compute_signature()
        sigp.load_signature(sig_db)




def main():
    initialize(sp.SignalProcessorSpectrogram)
    # load_signatures(sp.SignalProcessorSpectrogram)
    pass


if __name__ == '__main__':
    main()
