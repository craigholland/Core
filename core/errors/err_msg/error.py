"""Error categories and messages specific to the Error Object.
Read doc_string of error_handler.ErrorMsgManager for more information.
"""
from core.errors.err_msg_utils import *


LOCATION = 'core.errors.error_handler'
_local_location = LOCATION + '.Errors'
GENERIC = localkey('GENERIC',
                   'Generic local_key for Error Object.',
                   _local_location,
                   [])

GENERIC.messages = [
    errmsg('GENERICKEY', 'This key not to be used in messaging.'),
    errmsg('UNKNOWN_ERRORKEY', 'Encountered unexpected key: %s'),
    errmsg('DEFAULTKEY', 'Generic Error Message'),
    errmsg('UNEXPECTED_DEFAULT', 'Encountered unexpected default key(s): %s')
]


VALIDATION = localkey('VALIDATION',
                      'Error Object localkey for Validation errors.',
                      _local_location,
                      [])
VALIDATION.messages = [
    errmsg('UNKNOWN', 'An unknown error has caused an exception: %s'),
    errmsg('INVALIDKEY', 'Encountered invalid error key: %s')
]

ADD = localkey('ADD',
               'Error Object localkey for Add method exceptions.',
               _local_location,
               [])
ADD.messages = [
    errmsg('INVALID_MSGFORMAT', 'Incorrect number of message arguments included with '
                                'message.  Original message: %s; Args: %s'),
    errmsg('INVALID_ERRORKEY', 'Invalid ErrorKey included with message.  Original '
                               'message: %s; Args: %s')

]
