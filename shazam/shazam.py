from IO_methods import *
import database_management as dbm
from sqlalchemy import create_engine
import SignalProcessing as sp
import os
import pandas as pd
import logging
import sys



fh = logging.FileHandler('logs/Shazam.log')
fh.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(Levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger = logging.getLogger('Shazam')
logger.addHandler(fh)
# logger.addFilter(ch)


def initialize(SigProc=sp.SignalProcessorSpectrogram):
    """
        stick all our songs into the database
    :return:
    """
    logger.info('Starting')
    sig_db = dbm.DatabaseHandler()
    logger.info('Established Database Connection')
    dbm.initialize_database(dbh=sig_db, delete=True)
    logger.info('Initialized New Database')
    path_to_songs = 'assets/audio/songs'
    # df_song_info = pd.read_csv('assets/audio/metadata/songs.csv')
    df_artist_info = pd.read_csv('assets/audio/metadata/artists.csv')
    df_album_info = pd.read_csv('assets/audio/metadata/album.csv')
    songs = os.listdir(path_to_songs)
    df_song_info = pd.DataFrame(data=songs, columns=['name'])
    # todo make these using 'get id'
    df_song_info['album_id'] = 1
    df_song_info['artist_id'] = 1
    df_song_info['filesource'] = df_song_info['name'].apply(lambda x: os.path.join(path_to_songs, x))
    logger.info('Loading Initial Artists Begin')

    df_artist_info.to_sql(name=dbm.DatabaseInfo.TABLE_NAMES.ARTIST, con=sig_db.cur, if_exists='append', index=False)
    # for i in df_artist_info.index:
    #     d = {k:df_artist_info.at[i, k] for k in df_artist_info.columns}
    #     sig_db.add_artist(**d)
    logger.info('...Loaded Initial Artists Complete')
    df_album_info.to_sql(name=dbm.DatabaseInfo.TABLE_NAMES.ALBUM, con=sig_db.cur, if_exists='append', index=False)
    logger.info('Loading Initial Albums Begin')
    logger.info('...Loaded Initial Albums Complete')
    df_song_info.to_sql(name=dbm.DatabaseInfo.TABLE_NAMES.SONG, con=sig_db.cur, if_exists='append', index=False)
    logger.info('Loading Initial Songs Begin')
    logger.info('...Loaded Initial Songs Complete')
    for i in df_song_info.index:
        filesource, name, artist, album = df_song_info.loc[i, ['filesource', 'name', 'artist_id','album_id']]
        rad = ReadAudioData(os.path.join(path_to_songs, name))  # transform song to wav
        sigp = SigProc(audio_array=rad.array,
                       sample_freq=rad.audio.frame_rate,
                       songinfo={'artist_id': artist, 'album_id': album, 'filesource': filesource, 'name': name})
        sigp.compute_signature()
        sigp.load_signature(sig_db)

        # stick our signatures into the database, tied to song, albums, and
        # artists ids


def load_signatures(SigProc=sp.SignalProcessorExactMatch):
    sig_db = dbm.DatabaseHandler()
    path_to_songs = 'assets/audio/songs'
    songs = os.listdir(path_to_songs)
    df_song_info = pd.DataFrame(data=songs, columns=['name'])
    # todo make these using 'get id'
    df_song_info['album_id'] = 1
    df_song_info['artist_id'] = 1
    df_song_info['filesource'] = df_song_info['name'].apply(lambda x: os.path.join(path_to_songs, x))
    sig_db.cur.execute('DROP TABLE IF EXISTS ' + dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE + ' CASCADE;')
    sig_db.cur.execute(dbm.DatabaseInfo.create_signature)
    for i in df_song_info.index:
        filesource, name, artist, album = df_song_info.loc[i, ['filesource', 'name', 'artist_id','album_id']]
        rad = ReadAudioData(os.path.join(path_to_songs, name))  # transform song to wav
        sigp = SigProc(audio_array=rad.array, sample_freq=rad.audio.frame_rate,songinfo={'artist_id':artist,
                                                                                         'album_id':album,
                                                                                         'filesource':filesource,
                                                                                         'name':name})
        sigp.compute_signature()
        sigp.load_signature(sig_db)




def main():
    initialize(sp.SignalProcessorSpectrogram)
    # load_signatures(sp.SignalProcessorSpectrogram)
    pass


if __name__ == '__main__':
    main()
