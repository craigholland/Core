"""Error categories and messages specific to the System activities.
Read doc_string of error_handler.ErrorMsgManager for more information.
"""
from core.errors_old.err_msg_utils import *
LOCATION = 'core'

GENERIC = localkey('GENERIC',
                   'Generic local_key for System Object.',
                   'core.errors_old',
                   [])

GENERIC.messages = [
    errmsg('DEFAULTMSG', 'Default key for all System errors_old.'),
    errmsg('UNKNOWN_ERRORKEY', 'Encountered unexpected key: %s'),
    errmsg('TEMPKEY', 'Generic System error message')
]