
### IO exceptions ###


class UnsupportedFileType(Exception):
    """ cant process specified file type """
    pass


class CorruptedFile(Exception):
    """ cannot process file, it is corrupted """


### Database Exceptions ###


class CannotAddDuplicateRecords(Exception):
    """ Field is already populted, cannot add new record """


class TooManyResults(Exception):
    """ error if we are looking for 1 record but found multiple """


class NoResults(Exception):
    """ No records found but we were lookig for something.... """


class CannotDeleteLinkedData(Exception):
    """ We cannot delete the entry because it is linked in other tables. """

class DatabaseExists(Exception):
    """Database already present, cannot overwrite"""

# Signal Processing Exceptions

class NotWavData(Exception):
    """ Expected WAV file format, but recevied other """


class WindowTooBig(Exception):
    """ The window size parraemeter is larger than the entire file!!"""

class NoSignatures(Exception):
    """ No Signatures found """