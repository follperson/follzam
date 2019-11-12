from matching import SignatureChecking
from SignalProcessing import *
from database_management import DatabaseHandler
from IO_methods import ReadAudioData


def test_matching():
    filesource= '../assets/audio/songs/01 Speed Trials.mp3'
    rad = ReadAudioData(filesource)
    sp = SignalProcessorPeaksOnly(audio_array=rad.array, sample_freq=rad.audio.frame_rate)
    sp.compute_signature()

    dbh = DatabaseHandler()
    signatures = dbh.get_signatures_by_type_name(sp.method)
    sp.match(sp.signature[0], signatures)



if __name__ == '__main__':
    test_matching()
