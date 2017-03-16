"""Basic Logging class and utilities."""

import enum
import logging

from utils import constants
from utils import datetime_util
from utils import file_util
from utils import user_util


class LogTypes(enum.Enum):
  NOTSET=0
  DEBUG=1
  INFO=2
  WARNING=3
  ERROR=4
  CRITICAL=5

class Log(object):
  _format = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
  logging.basicConfig(format=_format)
  _system = False
  _logname = 'USERLOG'
  _data_path = constants.DATA_PATH + '/logs'

  def __init__(self, user=None):
    if user.lower() == 'system':
      self.user, self.client_ip, self._logname = 'SYSTEM', '0.0.0.0', 'SYSLOG'
    else:
      self.user, self.client_ip = user_util.getUserIP()
    self.extra = {'user': self.user, 'clientip': self.client_ip}
    self.logger = logging.getLogger(self._logname)
    self._initDataConnection()

  def _initDataConnection(self):
    date_dict = datetime_util.asDict(datetime_util.now(True))


