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
    if user and user.lower() == 'system':
      self.user, self.client_ip, self._logname, self._system = 'SYSTEM', '0.0.0.0', 'SYSLOG', True
    else:
      self.user, self.client_ip = user_util.getUserIP()
    self.extra = {'user': self.user, 'clientip': self.client_ip}
    self.logger = logging.getLogger(self._logname)
    self.log_file = self._initDataConnection()

  def _initDataConnection(self):

    data_path = 'data/logs'
    data_path += '/system' if self._system else '/users'

    date_dict = datetime_util.asDict(datetime_util.now(True))
    log_path = '/{0}/{1}/{2}'.format(date_dict['yr'], date_dict['mo'], date_dict['dy'])

    log_file = '{0}_log.txt'.format(date_dict['hr'])
    file_obj = file_util.File(data_path+log_path, log_file)
    file_obj.enableAllPermissions()
    if not file_obj.path_exists:
      file_obj.createPath()
    return file_obj



