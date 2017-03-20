"""Log Messages and Error Keys/Messages."""
import collections
import enum
from utils import constants

"""
Log Messages
"""
LOG_MSG_MISMATCH = ('Log Mismatch: attempted log message contained a greater '
                    'number of placeholders than the number of args provided.'
                    '\nMSG: {} - Placeholders: {} - ARGs: {} - KWARGs: {}')
LOG_START = ('Log Started: {} (local/'
             + format(constants.LOCAL_TIMEZONE_STR)
             + '); {} (UTC)\n\n************************\n\n')


"""
Error Keys and Messages.

In effort to keep Error messages well-organized, it is imperative to have a well-defined list of keys,
  which can be considered as specific sub-categories relative to the app.  Similar to the
  heirarchy of the Exception module, with the various categories/types of specific exceptions within it,
  Errors can be categorized by the specific area of the app that it pertains to.  This will
  enable the ability to be as broad or as specific as necessary in pinpointing the type of exception
  as well as it's origin.

This file will serve as a (continue to describe technical structure and application of ErrorKeys
and ErrorMessage structures.)

NB: Might be good idea to leave as generic as possible to make
it easier to adopt a defined Messages() class format later.
"""
class ErrorKeyType(enum.Enum):
  GENERIC = 0   # Catch-all ErrorKey type. Try to not use this as much as possible.
  TEST = 1      # General Error related to Testing mechanisms.
  CORE = 2      # General Error related to Core mechanisms.
  SYSTEM = 3    # General Error related to System mechanisms.
  BUILDER = 4   # General Error related to Builder mechanisms.
  DATA = 5      # General Error related to Data/Data-handling mechanisms.


class ErrorKey():
  pass
