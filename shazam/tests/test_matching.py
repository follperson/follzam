from matching import SignatureChecking
import SignalProcessing
import database_management as dbm
import IO_methods  as iom
import pandas as pd

def test_matching_db():
    filesource = '../assets/audio/songs/01 Speed Trials.mp3'
    rad = iom.ReadAudioData(filesource)
    dbh = dbm.DatabaseHandler()
    sp = SignalProcessing.SignalProcessorSpectrogram(audio_array=rad.array, sample_freq=rad.audio.frame_rate)
    sp.compute_signature()
    method_id = dbh.get_signature_id_by_name(sp.method)
    dbh.cur.execute(
        'INSERT INTO {} (method_id) VALUES (%s)'.format(dbm.DatabaseInfo.TABLE_NAMES.MATCH_ATTEMPT),
        method_id)
    attempt_id = dbh.cur.execute(
        'select max(id) from {};'.format(dbm.DatabaseInfo.TABLE_NAMES.MATCH_ATTEMPT)).fetchall()[0]

    """        match_id integer REFERENCES {} (id) NOT NULL,
        frequency integer NOT NULL,
        signature integer NOT NULL,
        PRIMARY KEY (match_id, frequency, signature) 
        );
    """.format(dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE_MATCH, dbm.DatabaseInfo.TABLE_NAMES.MATCH_ATTEMPT)

    create_match = """CREATE TABLE {} (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        method_id integer REFERENCES {} (id) NOT NULL
    """

    df = pd.DataFrame.from_dict(sp.signature, 'index', columns=['signature'])
    df['time_index'] = df.index.str[0]
    df['frequency'] = df.index.str[1]
    df['match_id'] = attempt_id
    df.to_sql(dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE_MATCH, con=dbh.cur)

    dbh.cur.execute('SELECT * FROM {} '
                    'WHERE {}.frequency == {}.frequency AND '
                    '{}.signature > {}.signature + 1000 AND {}.signature > {}.signature - 1000'.format(
        dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE,
        dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE,
        dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE_MATCH,
        dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE_MATCH,
        dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE,
        dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE_MATCH,
        dbm.DatabaseInfo.TABLE_NAMES.SIGNATURE
    ))


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