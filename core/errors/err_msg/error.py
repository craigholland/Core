"""Error categories and messages specific to the Error Object."""
from core.errors.err_msg_utils import *


LOCATION = 'core.errors.error_handler'

GENERIC = localkey('GENERIC',
                   'Generic local_key for Error Object.',
                   'core.errors',
                   [])

GENERIC.messages = [
    errmsg('UNKNOWN_ERRORKEY', 'Encountered unexpected key: %s'),
    errmsg('TEMPKEY', 'Generic Error Message')
]


