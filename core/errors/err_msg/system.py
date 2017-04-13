"""Error categories and messages specific to the System activities.
Read doc_string of error_handler.ErrorMsgManager for more information.
"""
from core.errors.err_msg_utils import *
LOCATION = 'core'

GENERIC = localkey('GENERIC',
                   'Generic local_key for System Object.',
                   'core.errors',
                   [])

GENERIC.messages = [
    errmsg('DEFAULTMSG', 'Default key for all System errors.'),
    errmsg('UNKNOWN_ERRORKEY', 'Encountered unexpected key: %s'),
    errmsg('TEMPKEY', 'Generic System error message')
]