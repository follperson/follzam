import numpy.random as nr
from follzam import database_management as dbm, IO_methods as iom, SignalProcessing
import time
import os
from follzam import basepath
from follzam.exceptions import NoSignatures
import pandas as pd

def test_snippet_matching():
    """
    test to evaluate the
    :return:
    """
    n = 50
    file_dir = os.path.join(basepath,'assets/files_for_tests/generated')
    all_songs = os.listdir(file_dir)
    filenames = nr.choice(all_songs, n)
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
        if song_info == -1:
            continue
        title, artist, album = song_info
        print(title == song, "\t\tACTUAL:",song, 'PREDICTIED:', song_info, 'CERTAINTY:', p)
        results.append([filepath, song, title, p])
        dbh.update_signature_match_with_true_value(attempt_id,name=title, artist=artist, album=album)
    df = pd.DataFrame(results, columns=['filepath', 'actual', 'prediction', 'certainty'])
    df['correct'] = df['actual'] == df['prediction']
    df.to_csv(os.path.join(basepath, 'tests/results/match results_%s.csv' % ''.join(str(time.time()).split('.')[:-1])))
