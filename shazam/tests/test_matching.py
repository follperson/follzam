from matching import SignatureChecking
import SignalProcessing
import database_management as dbm
import IO_methods  as iom
import pandas as pd

def test_matching_db():
    songs = {
         r"..\assets\files_for_tests\06 no more honey_0-10.mp3":'06  - No More Honey',
         r"..\assets\files_for_tests\06 no more honey_1-11.mp3":'06  - No More Honey',
         r"..\assets\files_for_tests\06 no more honey_10-20.mp3":'06  - No More Honey',
         r"..\assets\files_for_tests\06 no more honey_15-25.mp3":'06  - No More Honey',
         r"..\assets\files_for_tests\06 no more honey_45-55.mp3":'06  - No More Honey',
         r"..\assets\files_for_tests\06 no more honey_65-75.mp3": '06  - No More Honey',
         '../assets/files_for_tests/01 Barragan_20-30.mp3': '01  - Barragán',
         '../assets/files_for_tests/01 Barragan_65-75.mp3': '01  - Barragán',
         '../assets/files_for_tests/01 Speed Trials_0-10.mp3': '01 Speed Trials',
         '../assets/files_for_tests/01 Speed Trials_1.mp3': '01 Speed Trials',
         '../assets/files_for_tests/01 Speed Trials_2.mp3': '01 Speed Trials',
         '../assets/files_for_tests/01 Speed Trials_3.mp3': '01 Speed Trials',
         '../assets/files_for_tests/01 Speed Trials_4.mp3': '01 Speed Trials',
         '../assets/files_for_tests/01 Speed Trials_5.mp3': '01 Speed Trials',
         '../assets/files_for_tests/01 Speed Trials_6.mp3': '01 Speed Trials'}
    dbh = dbm.DatabaseHandler()
    for filepath, song in songs.items():
        rad = iom.ReadAudioData(filepath)
        sp = SignalProcessing.SignalProcessorSpectrogram(audio_array=rad.array, sample_freq=rad.audio.frame_rate)
        sp.compute_signature()
        song_info, p = sp.match(dbh)
        print("ACTUAL:",song, 'PREDICTIED:', song_info, 'CERTAINTY:', p)

def test_matching_local():
    aud_1 = iom.ReadAudioData(iom.ex_test)
    aud_2 = iom.ReadAudioData(iom.ex_test_2)

    dbh = dbm.DatabaseHandler()

    spex = SignalProcessing.SignalProcessorSpectrogram(aud_1.array, aud_1.audio.frame_rate)
    spex2 = SignalProcessing.SignalProcessorSpectrogram(aud_2.array, aud_2.audio.frame_rate)
    spex.compute_signature()
    spex2.compute_signature()
    df1 = pd.DataFrame.from_dict(spex.signature, 'index', columns=['signature'])
    df2 = pd.DataFrame.from_dict(spex2.signature, 'index', columns=['signature'])

    df1['time_index'] = df1.index.str[0]
    df1['frequency'] = df1.index.str[1]

    df2['time_index'] = df2.index.str[0]
    df2['frequency'] = df2.index.str[1]

    df_db = pd.read_sql('SELECT * FROM FOLLZAM_SIGNATURE', con=dbh.con)
    pd.merge(df1, df2, how='inner', on=['frequency', 'signature'])
    # df1.loc[(df1.frequency > 45) & (df1.frequency < 55)]
    # df2.loc[(df2.frequency > 45) & (df2.frequency < 55)]