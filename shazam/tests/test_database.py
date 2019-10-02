from database_management import *

with open('dbconn.info','r') as info:
    access_info = info.readlines()



def test_connection():
    dbh = DatabaseHandler(access_info)


def test_add_song():
    dbh = DatabaseHandler(access_info)

    wav = ''
    dbh.add_song(wav, 'Sam Stone', artist='John Prine')
    song_id = dbh.get_song('title','Sam Stone')
    assert wav == dbh.db.execute('SELECT wav from song where id = {}'.format(song_id))

    try:
        dbh.add_song(wav, 'Sam Stone',artist='John Prine')
    except CannotAddDuplicateRecords:
        pass

    dbh.remove_song('Sam Stone')
    try:
        dbh.get_song('title','San Stone')
    except NoRecordsFound:
        pass


def test_add_spectrogram():
    pass

