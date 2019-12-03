from follzam.database_management import *
from follzam.exceptions import CannotAddDuplicateRecords, NoResults


def test_insert_remove():
    dbh = DatabaseHandler()
    artist_name = 'Testing Artist Fakey'
    album_name = 'An Album, by a fake artist'
    album_year = 2000
    song_name = 'An Oldie But a Goodie'
    artist_where = {'name': artist_name}
    album_where = {'artist': artist_name, 'name': album_name, 'year': album_year}
    song_where = {'artist': artist_name, 'name': song_name, 'album': album_name}

    ## clear out test stuff
    try:
        dbh.remove_song(**song_where)
    except NoResults:
        pass
    try:
        dbh.remove_album(**album_where)
    except NoResults:
        pass
    try:
        dbh.remove_artist(**artist_where)
    except NoResults:
        pass

    #  Test add / removal of artists
    dbh.add_artist(**artist_where)
    artist_id1 = dbh.get_artist_id(**artist_where)
    dbh.remove_artist(**artist_where)
    try:
        dbh.get_artist(**artist_where)
    except NoResults:
        pass
    dbh.add_artist(**artist_where)
    artist_id = dbh.get_artist_id(**artist_where)
    assert artist_id1 + 1 == artist_id, 'SERIAL Function not working as expected'

    #  Test add / removal of album

    try:
        dbh.remove_album(**album_where)
    except NoResults:
        pass
    dbh.add_album(**album_where)
    album_id = dbh.get_album_id(**album_where)
    album_info = dbh.get_album('*', id=album_id)[0]
    assert (album_info['name'] == album_where['name']) & \
           (album_info['year'] == album_where['year']) & \
           (album_info['artist_id'] == artist_id)

    dbh.remove_album(**album_where)
    try:
        dbh.get_album(**album_where)
    except NoResults:
        pass
    dbh.add_album(**album_where)
    album_id = dbh.get_album_id(**album_where)
    album_info = dbh.get_album('*', id=album_id)[0]
    assert (album_info['name'] == album_where['name']) & \
           (album_info['year'] == album_where['year']) & \
           (album_info['artist_id'] == artist_id)

    try:
        dbh.remove_song(**song_where)
    except NoResults:
        pass
    dbh.add_song(**song_where)
    song_id = dbh.get_song_id(**song_where)
    song_info = dbh.get_one_song('*', id=song_id)
    assert (song_info['name'] == song_name) & \
           (song_info['artist_id'] == artist_id) & \
           (song_info['album_id'] == album_id)
    dbh.remove_song(**song_where)
    try:
        dbh.get_song(**song_where)
    except NoResults:
        pass
    try:
        dbh.add_song(**song_where)
    except CannotAddDuplicateRecords:
        pass




