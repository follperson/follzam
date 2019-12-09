import argparse
import os
from follzam.database_management import DatabaseHandler, CannotAddDuplicateRecords
from follzam.IO_methods import ReadAudioData, UnsupportedFileType
from follzam.SignalProcessing import SignalProcessorSpectrogram, NoSignatures
import logging
logger = logging.getLogger(__name__)


def identify(path):
    logger.info("Attempting to Identify a new song: {}".format(path))
    dbh = DatabaseHandler()
    rad = ReadAudioData(path)
    sp = SignalProcessorSpectrogram(audio_array=rad.array,
                                    sample_freq=rad.audio.frame_rate)
    try:
        sp.compute_signature()
    except NoSignatures:
        return
    prediction, p, attempt_id = sp.match(dbh)
    title, artist, album = prediction
    logger.info(
        "Match attempt #{}. \n\t Predicted {} by {} on {} with {}% confidence. ".format(attempt_id, title, artist,
                                                                                        album, round(p * 100, 1)))


def add(target, title=None, artist=None, album=None, from_dir=False, genre=None, year=None):
    logger.info('Adding songs to database')
    dbh = DatabaseHandler()
    assert ((title is None) or not from_dir), 'Cannot specify both a title and a directory filled with songs'
    assert ((title is not None) or from_dir), 'Must specify a title or a directory'
    if title is not None:
        assert artist is not None, 'Cannot specify a title without an artist'
        assert album is not None, 'Cannot specify a title without an album'
        logger.info('Adding one song to database: {} by {} on {}'.format(title, artist, album))
        add_song(filepath=target, dbh=dbh, artist=artist, album=album, name=title, genre=genre, year=year)
        return

    if from_dir:
        root = target
        logger.info('Adding directory of songs to database: {}'.format(root))
        if (artist is None) and (album is None):
            for artist in os.listdir(root):
                artist_folder = os.path.join(root, artist)
                if not os.path.isdir(artist_folder):
                    continue
                add_from_artist_level_folder(artist_folder, dbh, artist, genre, year)
        elif album is None:
            add_from_artist_level_folder(root, dbh, artist, genre, year)
        elif (artist is not None) and (album is not None):
            add_from_album_level_folder(root, dbh, artist, album, genre, year)
        else:
            raise NotImplementedError
    raise NotImplementedError


def add_from_artist_level_folder(root, dbh, artist, genre, year):
    for album in os.listdir(root):
        album_folder = os.path.join(root, album)
        if not os.path.isdir(album_folder): continue
        add_from_album_level_folder(root, dbh, artist, album, genre, year)


def add_from_album_level_folder(root, dbh, artist, album, genre, year):
    for filename in os.listdir(root):
        add_song(os.path.join(root, filename), dbh, artist=artist, album=album, genre=genre, year=year)


def add_song(filepath, dbh, artist, album, genre, year, name=None):
    """
        Add a new song to the database, designed for use with the command line driver
    :param filepath: filepath of new song
    :param dbh: database handler object
    :param artist: name of artist
    :param album: name of album
    :param genre: name of genre (for the album!)
    :param year: year genre was published
    :param name: name of song (optional, if not provided then we use the filepath filename without extension)
    :return:
    """
    # Before we do any database updating lets make sure that the file we are working with is a valid file
    assert os.path.isfile(filepath), 'not a file, cannot do anything with this'
    try:
        rad = ReadAudioData(filepath)
    except UnsupportedFileType:
        return

    # Make sure the artist and album is in the database. If they are not then we will add them
    try:
        dbh.add_artist(name=artist)
    except CannotAddDuplicateRecords:
        pass
    artist_id = dbh.get_artist_id(name=artist)

    try:
        dbh.add_album(artist_id=artist_id, name=album, genre=genre, year=year)
    except CannotAddDuplicateRecords:
        pass
    album_id = dbh.get_album_id(artist_id=artist_id, name=album, genre=genre, year=year)

    if name is None:
        name = '.'.join(os.path.basename(filepath).split('.')[:-1])

    sp = SignalProcessorSpectrogram(audio_array=rad.array,
                                    sample_freq=rad.audio.frame_rate,
                                    songinfo={'artist_id': artist_id, 'album_id': album_id, 'filesource': filepath,
                                              'name': name})
    try:
        dbh.add_song(name=name, filesource=filepath, artist_id=artist_id, album_id=album_id)
    except CannotAddDuplicateRecords:
        logger.error('Song already exists in database, cannot re add. Skipping.')
        return
    print(sp.songinfo)
    try:
        sp.compute_signature()
    except NoSignatures:
        return
    sp.load_signature(dbh)


def list_database():
    dbh = DatabaseHandler()
    dbh.list_songs()


if __name__ == '__main__':
    logger.info("Command line call to Freezam")
    parser = argparse.ArgumentParser(
        description='Freezam is a python based audio feature identifier. It tries to identify the song which '
                    'an audio snippet came from'
        )

    subparsers = parser.add_subparsers(title='actions', dest='subparser_name')
    ADD = 'add'
    IDENTIFY = 'identify'
    LIST = 'list'
    parser_add = subparsers.add_parser(ADD,
                                       help='''Add a new song to the database
                                       final position parameter is file, or directory 
                                       If you provide --title you must provide --album and --artist
                                       if you provide --dir you cannot provide --title
                                       if you provide --dir you cannot provide only --album, you must also pass --artist
                                       ''')
    parser_add.add_argument('--title', type=str, default=None,help='Title of song. Cannot be added in conjunction with --dir')
    parser_add.add_argument('--artist', type=str, default=None, help='Artist Name')
    parser_add.add_argument('--album', type=str, default=None, help='Album name')
    parser_add.add_argument('--genre', type=str, default=None, help='Genre of album ')
    parser_add.add_argument('--year', type=int, default=None, help='Year album was released')
    parser_add.add_argument('--dir', action='store_true', default=False,
                            help="""
                            Optional, if you provide a directory, we recursively walk through the directory.

                            If only --artist is provided, directory structure is assumed as: --dir/Album-Name>songs
                            If --artist and --album are provided, directory structure is assumed as: --dir/filenames
                            If neither --artist, nor --album is provided, the directory structure is assumed as:
                                --dir/Artist-name/album-name/songs
                            
                                """)
    parser_add.add_argument('target')

    parser_identify = subparsers.add_parser(IDENTIFY,
                                            help="""Pass a filepath or a URL of an audio file and we will
                                            identify the audio file if it is in our audio database""")

    parser_identify.add_argument('song', action='store', help='song or snippt you want to identify')

    parser_list = subparsers.add_parser(LIST, help='''List the current songs, artists, and albums from the database''')

    args = parser.parse_args()

    # print(args.identify)
    print(args)
    if args.subparser_name == IDENTIFY:
        identify(args.song)
    elif args.subparser_name == ADD:
        add(args.target, args.title, args.artist, args.album, args.dir, args.genre, args.year)
    elif args.subparser_name == LIST:
        list_database()
