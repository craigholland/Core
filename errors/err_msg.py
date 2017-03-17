"""Error and Log Messages."""
from utils import constants
LOG_MSG_MISMATCH = ('Log Mismatch: attempted log message contained a greater '
                    'number of placeholders than the number of args provided.'
                    '\nMSG: {} - Placeholders: {} - ARGs: {} - KWARGs: {}')
LOG_START = ('Log Started: {} (local/'
             + format(constants.LOCAL_TIMEZONE_STR)
             + '); {} (UTC)\n\n************************\n\n')
