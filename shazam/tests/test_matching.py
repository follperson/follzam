from follzam import database_management as dbm, IO_methods as iom, SignalProcessing


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
        song_info, p, attempt_id = sp.match(dbh)
        print("ACTUAL:",song, 'PREDICTIED:', song_info, 'CERTAINTY:', p)
        dbh.execute_query()
