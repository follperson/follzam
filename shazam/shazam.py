from IO_methods import *
from signal_processing import *
from database_management import *
from matching import *
import os
import pandas as pd


def initialize():
    """
        stick all our songs into the database
    :return:
    """

    path_to_songs = 'assets/audio/songs'
    df_song_info = pd.read_csv('assets/audio/metadata/songs.csv')
    df_artist_info = pd.read_csv('assets/audio/metadata/artists.csv')
    df_album_info = pd.read_csv('assets/audio/metadata/artists.csv')
    songs = os.listdir(path_to_songs)

    df_artist_info.to_sql()  # stick our artist info into db (also give IDs to album_info, song_info df )
    df_album_info.to_sql()  # stick our album info into db (also give IDs to song_info df )
    df_song_info.to_sql()  # stick song info into db (also get ids from albums and artists)
    for song in songs:
        wav = ReadAudioData(os.path.join(path_to_songs, song))  # transform song to wav
        sp = SignalProcessor(wav)
        sp.main() # compute signatures
        df_signatures = pd.DataFrame(sp.signatures)

        df_signatures.to_sql()  # stick our signatures into the database, tied to song, albums, and artists ids



def check_new_signature(snippet):
    """
        procedure to compare new snippet to our database
    :param snippet: short audio segment
    :return:
    """
    wav = ReadAudioData(snippet)  # homogenize snippet to wav

    sp = SignalProcessor(wav) # initialize
    sp.main()  # create all the signatures

    matches = []
    for signature in sp.signatures:
        compare_new_signature(signature,1)
    return matches # our list of findings
