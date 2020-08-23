# Follzam README

## Purpose

Follzam is a audio fingerprinting tool, in the model of Shazam. 

Pass audio via the command line interface and Python. 

eg:

```
$ python freezam.py -h
Command line call to Follzam
usage: Follzam [-h] [--version] {add,update,remove,identify,list} ...

Freezam is a python based audio feature identifier. It tries to identify the
song which an audio snippet came from

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

actions:
  {add,update,remove,identify,list}
    init                Initialize the database. Must do this first. 
                        Provide --reset if you wish to teardown old database. 
                        Database lives at location specified by db_file variable 
                        in follzam/DatabaseInfo.py 
    add                 Add a new song to the database final position
                        parameter is file, or directory If you provide --title
                        you must provide --album and --artist if you provide
                        --dir you cannot provide --title if you provide --dir
                        you cannot provide only --album, you must also pass
                        --artist
    update              Update the given table. the name of the row, and then
                        additional where specification
    remove              Remove by id. Need to pass the table which you care to
                        remove, the name of the row, and then additional where
                        specification
    identify            Pass a filepath or a URL of an audio file and we will
                        identify the audio file if it is in our audio database
    list                List the current songs, artists, and albums from the
                        database

``` 

## initialize database

To initialize the database you need to run the command 

`python freezam.py init`

Next you should populate the database with the `add` commands

Depending on the structure, run the freezam add command with appropriate specifications

eg. if structured like <artists> / <albums> / <songs>

run like: `python freezam.py add --dir <directory_to_add>`

if structured like <albums> / <songs>

run like: `python freezam.py add --dir --artist=<artist_name> <directory_to_add>`

if structured like / <songs> 

run like: `python freezam.py add --dir --artist=<artist_name> --album=<album_name> <directory_to_add>`

## Test Audio

Once your database is initialized, you can test snippets via the `identify` subcommand

eg: `python freezam.py identify <path_to_audio>`

### Metrics

We find that it takes approximately 1 second to fingerprint a song, and we have about an 75% True Positive rate, and a 1% False Positive rate. Our True negative rate is 99%, and False Negative rate is about 25%.  
 
## Questions?

Please contact author [Andrew Follmann](follperson.github.io) with any questions or concerns.

### Notes

The test scripts are all developed to run with hard-coded (relative) directories that I were created for this project.
You ought to change those paths for your project.  