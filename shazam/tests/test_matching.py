from matching import SignatureChecking
from SignalProcessing import *
from database_management import DatabaseHandler
from IO_methods import ReadAudioData


def test_matching():
    filesource = '../assets/audio/songs/01 Speed Trials.mp3'
    rad = ReadAudioData(filesource)
    dbh = database_management.DatabaseHandler()
    sp = SignalProcessorSpectrogram(audio_array=rad.array, sample_freq=rad.audio.frame_rate)
    sp.compute_signature()
    method_id = dbh.get_signature_id_by_name(sp.method)
    dbh.cur.execute(
        'INSERT INTO {} (method_id) VALUES (%s)'.format(database_management.DatabaseInfo.TABLE_NAMES.MATCH_ATTEMPT),
        method_id)
    attempt_id = dbh.cur.execute(
        'select max(id) from {};'.format(database_management.DatabaseInfo.TABLE_NAMES.MATCH_ATTEMPT)).fetchall()[0]

    """        match_id integer REFERENCES {} (id) NOT NULL,
        frequency integer NOT NULL,
        signature integer NOT NULL,
        PRIMARY KEY (match_id, frequency, signature) 
        );
    """.format(TABLE_NAMES.SIGNATURE_MATCH, TABLE_NAMES.MATCH_ATTEMPT)

    create_match = """CREATE TABLE {} (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        method_id integer REFERENCES {} (id) NOT NULL
"""

    df = pd.DataFrame.from_dict(sp.signature, 'index', columns=['signature'])
    df['time_index'] = df.index.str[0]
    df['frequency'] = df.index.str[1]
    df['match_id'] = attempt_id
    df.to_sql(database_management.DatabaseInfo.TABLE_NAMES.SIGNATURE_MATCH, con=dbh.cur)

    dbh.cur.execute('SELECT * FROM {} '
                    'WHERE {}.frequency == {}.frequency AND '
                    '{}.signature > {}.signature + 1000 AND {}.signature > {}.signature'.format(
        database_management.DatabaseInfo.TABLE_NAMES.SIGNATURE,
        database_management.DatabaseInfo.TABLE_NAMES.SIGNATURE,
        database_management.DatabaseInfo.TABLE_NAMES.SIGNATURE_MATCH,
        database_management.DatabaseInfo.TABLE_NAMES.SIGNATURE_MATCH,
        database_management.DatabaseInfo.TABLE_NAMES.SIGNATURE,
        database_management.DatabaseInfo.TABLE_NAMES.SIGNATURE_MATCH,
        database_management.DatabaseInfo.TABLE_NAMES.SIGNATURE
    ))

if __name__ == '__main__':
    test_matching()
