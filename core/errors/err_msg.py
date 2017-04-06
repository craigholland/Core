from enum import Enum
from core.core_utils import *
from core.errors.err_msg_utils import *



# class BaseKey(Enum):
#   """Enum of top-level base classes that initialize error objects."""
#   SYSTEM = 0  # Default
#   ERRORS = 1  # core.errors
#   MESSAGE = 2 # core.base.core_message.Message
#
# for name in [x.name for x in BaseKey]:
#   globals()[name] = createType(name)
#
#
# # ERROR OBJECT error messages
# ERRORS.VALIDATION = createType(VALIDATION)

ERRORS = BaseKey('Errors',
                 desc='Error Keys associated with the Base Error Object.',
                 location='core.errors'
                 )

ERRORS.local_keys = [
  LocalKey('VALIDATION', '')
]

