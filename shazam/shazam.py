from IO_methods import *
import database_management as dbm
import matching
import logging
from sqlalchemy import create_engine

import SignalProcessing as sp
import os
import pandas as pd


def initialize(SigProc=sp.SignalProcessorExactMatch):
    """
        stick all our songs into the database
    :return:
    """
    sig_db = dbm.DatabaseHandler()
    dbm.initialize_database(dbh=sig_db, delete=True)

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

    # df_artist_info.to_sql(name=dbm.DatabaseInfo.TABLE_NAMES.ARTIST, con=sig_db.con,if_exists='append')
    for i in df_artist_info.index:
        d = {k:df_artist_info.at[i, k] for k in df_artist_info.columns}
        sig_db.add_artist(**d)
    # df_album_info.to_sql(name=dbm.DatabaseInfo.TABLE_NAMES.ALBUM, con=sig_db.con,if_exists='append')
    for i in df_album_info.index:
        d = {k:df_album_info.at[i, k] for k in df_album_info.columns}
        sig_db.add_album(**d)
    # df_song_info.to_sql(name=dbm.DatabaseInfo.TABLE_NAMES.SONG, con=sig_db.con,if_exists='append')
    for i in df_song_info.index:
        d = {k:df_song_info.at[i, k] for k in df_song_info.columns}
        sig_db.add_song(**d)

    for i in df_song_info.index:
        filesource, name, artist, album = df_song_info.loc[i, ['filesource', 'name', 'artist_id','album_id']]
        rad = ReadAudioData(os.path.join(path_to_songs, name))  # transform song to wav
        sigp = SigProc(audio_array=rad.array, sample_freq=rad.audio.frame_rate,songinfo={'artist_id':artist,
                                                                                         'album_id':album,
                                                                                         'filesource':filesource,
                                                                                         'name':name})
        sigp.compute_signature()
        sig_db.load_signal(sigp)

        # stick our signatures into the database, tied to song, albums, and
        # artists ids



def check_new_signature(snippet):
    """
        procedure to compare new snippet to our database
    :param snippet: short audio segment
    :return:
    """
    wav = ReadAudioData(snippet)  # homogenize snippet to wav

    sp = SignalProcessor(wav)  # initialize
    sp.main()  # create all the signatures

    matches = []
    for signature in sp.signatures:
        compare_new_signature(signature, 1)
    return matches  # our list of findings

if __name__ == '__main__':
    initialize()
