from matching import SignatureChecking
import SignalProcessing
import database_management as dbm
import IO_methods  as iom
import pandas as pd

def test_matching_db():
    songs = {r"..\assets\files_for_tests\06 no more honey_0-10.mp3":'06  - No More Honey',
             r"..\assets\files_for_tests\06 no more honey_1-11.mp3":'06  - No More Honey',
             r"..\assets\files_for_tests\06 no more honey_10-20.mp3":'06  - No More Honey',
             r"..\assets\files_for_tests\06 no more honey_15-25.mp3":'06  - No More Honey',
             r"..\assets\files_for_tests\06 no more honey_45-55.mp3":'06  - No More Honey',
             r"..\assets\files_for_tests\06 no more honey_65-75.mp3": '06  - No More Honey',
             '../assets/files_for_tests/01 Barragan_20-30.mp3': '01  - Barragán',
             '../assets/files_for_tests/01 Barragan_20 - 30.mp3': '01  - Barragán',
             '../assets/files_for_tests/01 Barragan_65 - 75.mp3': '01  - Barragán',
             '../assets/files_for_tests/01 Speed Trials_0 - 10.mp3': '01 Speed Trials',
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
        method_id = dbh.get_signature_id_by_name(sp.method)
        dbh.cur.execute('INSERT INTO {} (method_id) VALUES (%s)'.format(dbm.DatabaseInfo.TABLE_NAMES.MATCH_ATTEMPT), method_id)
        attempt_id = dbh.cur.execute('select max(id) from {};'.format(dbm.DatabaseInfo.TABLE_NAMES.MATCH_ATTEMPT)).fetchone()[0]

        df = pd.DataFrame(sp.signature, columns=['time_index', 'frequency', 'signature'])
        df['match_id'] = attempt_id
        df[['signature', 'frequency', 'match_id']].drop_duplicates().to_sql(
            dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE_MATCH, con=dbh.cur, if_exists='append', index=False)
        match_query_text = """SELECT {}.time_index, {}.signature, {}.song_id FROM {} 
            INNER JOIN {} ON {}.signature = {}.signature
            WHERE {}.match_id = %s
            ORDER BY {}.signature;
        """.format(dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE, dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE,
                   dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE, dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE_MATCH,
                   dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE, dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE_MATCH,
                   dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE, dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE_MATCH,
                   dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE)
        df = pd.read_sql(match_query_text, dbh.con, params=(attempt_id,))
        dfgb = df.groupby('song_id').agg({'time_index': 'count'})
        for song_id in dfgb.index:
            dfgb.loc[song_id, 'total signatures'] = dbh.get_total_signatures_for_given_song(method_id, song_id)
        dfgb['weighting'] = dfgb['time_index'] / dfgb['total signatures']
        dfgb['P'] = dfgb['weighting'] / dfgb['weighting'].sum()
        song_id, probability = dfgb.reset_index().loc[dfgb['P'] == dfgb['P'].max(),['song_id','P']]
        song_info = dbh.get_formatted_song_info(song_id)
        update_prediction = '''UPDATE {} SET prediction=%s WHERE id=%s;'''.format(dbm.DatabaseInfo.TABLE_NAMES.MATCH_ATTEMPT)
        dbh.cur.execute(update_prediction, (song_id, attempt_id))




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