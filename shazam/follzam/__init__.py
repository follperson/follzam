__version__ = 1.0
import logging.config
VALID_FILE_TYPES = ['WAV', 'MP3', 'OGG', 'FLAC']
GENRES = ['Indie Rock','Rap','Classical','Jazz']

logging.config.dictConfig({
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": 'INFO',
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "level":'DEBUG',
            'class':'logging.FileHandler',
            'formatter':'default',
            'filename':'logs/Follzam.log'
        }
    },
    'root': {
        'level':'DEBUG',
        'handlers':['console', 'file']

    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["console", 'file']
        }
    }
})



class TABLE_NAMES:
    GENRE = 'follzam_genre'
    ALBUM = 'follzam_album'
    ARTIST = 'follzam_artist'
    SONG = 'follzam_song'
    SONG_DATA = 'follzam_songdata'
    SIGNATURE = 'follzam_signature'
    SIGNATURE_TYPES = 'follzam_signaturetypes'  # in case we want to test out multiple signatures
    FILE_TYPE = 'follzam_filetype'  # for binary data storage and spectrogram recreation
    SIGNATURE_MATCH = 'follzam_signature_matches'
    MATCH_ATTEMPT = 'follzam_match_attempts'

    ALL = [GENRE, ALBUM, ARTIST, SONG, SONG_DATA, SIGNATURE, SIGNATURE_TYPES, FILE_TYPE, SIGNATURE_MATCH, MATCH_ATTEMPT]


class SIGNALTYPES:
    """ persistent variable store for signature type generation"""
    EXACT_MATCH = 'EXACT_MATCH'
    SMOOTHED_PERIODOGRAM = 'SMOOTHED_PERIODOGRAM'
    FREQ_POWER_PAIRS = 'FREQ_POWER_PAIRS'
    FREQ_PEAKS = 'FREQ_PEAKS'
    MAX_POWER_FREQ_BANDS = 'MAX_POWER_FREQ_BANDS'
    SPECTROGRAM = 'SPECTROGRAM'
    ALL = [EXACT_MATCH, SMOOTHED_PERIODOGRAM, FREQ_POWER_PAIRS, FREQ_PEAKS, MAX_POWER_FREQ_BANDS, SPECTROGRAM]
