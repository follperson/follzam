import numpy.random as nr
from follzam import database_management as dbm, IO_methods as iom, SignalProcessing
import os
from follzam.exceptions import NoSignatures

def test_matching_db():
    file_dir = r'../assets/files_for_tests/generated'
    all_songs = os.listdir(file_dir)
    filenames = nr.choice(all_songs, 10)
    songs = {os.path.join(file_dir, fn): '.'.join(fn.split('.')[:-2]) for fn in filenames}
    dbh = dbm.DatabaseHandler()
    results=[]
    for filepath, song in songs.items():
        rad = iom.ReadAudioData(filepath)
        sp = SignalProcessing.SignalProcessorSpectrogram(audio_array=rad.array, sample_freq=rad.audio.frame_rate)
        try:
            sp.compute_signature()
        except NoSignatures:
            print('Could not find a signature', filepath)
            continue
        song_info, p, attempt_id = sp.match(dbh)

        title, artist, album = song_info
        print("\t\tACTUAL:",song, 'PREDICTIED:', song_info, 'CERTAINTY:', p)
        results.append([song, title])
        dbh.update_signature_match_with_true_value(attempt_id,name=title, artist=artist, album=album)
    print(results)