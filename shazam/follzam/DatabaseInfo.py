from follzam import TABLE_NAMES
""" This is a persistent variable store for the SQL accessors.
    It does not do anything by itself, but it is used by the other programs when creating the database,
    or updating the tables.
"""

create_artist = """CREATE TABLE {} ( 
   id SERIAL PRIMARY KEY, 
   name TEXT UNIQUE
   );
    """.format(TABLE_NAMES.ARTIST)

create_genre = """CREATE TABLE {} (
    id SERIAL PRIMARY KEY, 
    name text UNIQUE
    );
""".format(TABLE_NAMES.GENRE)

create_album = """CREATE TABLE {} ( 
    id SERIAL PRIMARY KEY, 
    name text UNIQUE,
    year integer,
    artist_id integer REFERENCES {} (id),
    genre_id integer REFERENCES {} (id)
    );
    """.format(TABLE_NAMES.ALBUM, TABLE_NAMES.ARTIST, TABLE_NAMES.GENRE)

create_song = """CREATE TABLE {} ( 
    id SERIAL PRIMARY KEY, 
    name text NOT NULL,
    filesource text,
    artist_id integer REFERENCES {} (id),
    album_id integer REFERENCES {} (id),
    UNIQUE (name, artist_id, album_id)
    );
    """.format(TABLE_NAMES.SONG, TABLE_NAMES.ARTIST, TABLE_NAMES.ALBUM)

create_songdata = """CREATE TABLE {} (
    id SERIAL PRIMARY KEY,
    song_id integer REFERENCES {} (id) NOT NULL,
    filetype_id integer REFERENCES {} (id) NOT NULL,
    framerate integer NOT NULL,
    channels integer NOT NULL,
    data bytea NOT NULL
    );
    """.format(TABLE_NAMES.SONG_DATA, TABLE_NAMES.SONG, TABLE_NAMES.FILE_TYPE)

create_file_types = """CREATE TABLE {} ( 
    id SERIAL PRIMARY KEY,
    name text NOT NULL
    );
    """.format(TABLE_NAMES.FILE_TYPE)

create_signature_types = """CREATE TABLE {} ( 
    id SERIAL PRIMARY KEY,
    name text NOT NULL
    );
    """.format(TABLE_NAMES.SIGNATURE_TYPES)

create_signature = """CREATE TABLE {} (
        time_index integer NOT NULL,
        frequency integer,
        signature integer NOT NULL,
        method_id integer REFERENCES {} (id) NOT NULL,
        song_id integer REFERENCES {} (id) NOT NULL,
        PRIMARY KEY (song_id, method_id, time_index, signature)
        );
    """.format(TABLE_NAMES.SIGNATURE, TABLE_NAMES.SIGNATURE_TYPES, TABLE_NAMES.SONG)

create_signature_match = """CREATE TABLE {} (
    match_id integer REFERENCES {} (id) NOT NULL,
    frequency integer NOT NULL,
    signature integer NOT NULL,
    PRIMARY KEY (match_id, frequency, signature)
    );
    """.format(TABLE_NAMES.SIGNATURE_MATCH, TABLE_NAMES.MATCH_ATTEMPT)

create_match = """CREATE TABLE {} (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    predicted_song_id integer REFERENCES {} (id),
    true_song_id integer REFERENCES {} (id),
    method_id integer REFERENCES {} (id) NOT NULL
    );
    """.format(TABLE_NAMES.MATCH_ATTEMPT, TABLE_NAMES.SONG, TABLE_NAMES.SONG, TABLE_NAMES.SIGNATURE_TYPES)


create_full_schema = '\n '.join(
    [create_file_types, create_signature_types, create_artist, create_genre, create_album, create_song,
     create_songdata, create_signature, create_match, create_signature_match])

drop_tables = 'DROP TABLE IF EXISTS ' + ' CASCADE;\nDROP TABLE IF EXISTS '.join(TABLE_NAMES.ALL) + ' CASCADE;'

