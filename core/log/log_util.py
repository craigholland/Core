"""Basic Logging class and utilities."""

import logging


from core.base.core_enum import Enum
from errors import err_msg
from core_utils import constants
from core.utils import datetime_util
from core.utils import file_util
from core.utils import user_util


class LogTypes(Enum):
  NOTSET=0
  DEBUG=1
  INFO=2
  WARNING=3
  ERROR=4
  CRITICAL=5

_DEFAULT_LOG_LEVEL = LogTypes.INFO

class Log(logging.getLoggerClass()):

  _FORMAT = '%(asctime)s - %(name)s - %(user)s - %(clientip)s - %(levelname)s - %(message)s'
  _DATA_PATH = constants.LOG_PATH

  def __init__(self, user=None):
    self._ready = False
    self._initLogs(user)
    self._initDataConnection()
    self._initLogHandlers()

  def _initLogs(self, user):
    # Initialize User and Log names.
    if user and user.lower() == 'system':
      self.user, self.client_ip = 'SYSTEM', '0.0.0.0'
      self._issystem, self._logname = True, 'SYSLOG'
    else:
      self.user, self.client_ip = user_util.getUserIP()
      self._issystem, self._logname = False, 'USERLOG'
    self.extra = {'user': self.user, 'clientip': self.client_ip}

    # Establish Logging Repo (self.log_file : core_utils.file_utils.File object).
    self.log_file = self._initDataConnection()
    if self.log_file.path_exists and not self.log_file.file_exists:
      self.log_file.Append(err_msg.LOG_START.format(datetime_util.now(),
                                                    datetime_util.now(True)))

  def _initLogHandlers(self):

    filename = '{0}/{1}'.format(self.log_file.path, self.log_file.file)
    # Establish named log with File and Stream Handlers.
    self.logger = logging.getLogger(self._logname)
    self.logger.setLevel(logging.DEBUG)
    fh, sh = logging.FileHandler(filename), logging.StreamHandler()
    fh.setLevel(logging.DEBUG), sh.setLevel(logging.ERROR)


    # Format Handlers and add to logger.
    format = logging.Formatter(self._FORMAT)
    fh.setFormatter(format)
    sh.setFormatter(format)
    self.logger.addHandler(fh)
    self.logger.addHandler(sh)
    self.ready = True
    if self._issystem:
      self.logger.info('{} Logging operations initialized'.format(self._logname), extra=self.extra)
    else:
      SYSLOG.logger.info('{} Logging operations initialized'.format(self._logname), extra=self.extra)


  def _closeHandlers(self):
    if self._issystem:
      self.logger.info('Shutting down {} Log handlers.'.format(self._logname), extra=self.extra)
    else:
      SYSLOG.logger.info('Shutting down {} Log handlers.'.format(self._logname), extra=self.extra)

    for handle in self.logger.handlers:
      handle.close()
      self.logger.removeHandler(handle)
    self.ready = False

  def _initDataConnection(self):
    """Creates Path for Log Files.

    Path format: /data/logs/<system:user>/<YYYY>/<MM>/<DD>/
    File format: <HH>.log
    """
    data_path = 'data/logs'
    data_path += '/system' if self._issystem else '/users'

    date_dict = datetime_util.asDict(datetime_util.now(True))
    log_path = '/{0}/{1}/{2}'.format(date_dict['yr'], date_dict['mo'], date_dict['dy'])

    log_file = '{0}.log'.format(date_dict['hr'])
    self.log_hour = date_dict['hr']
    file_obj = file_util.File(data_path+log_path, log_file)
    file_obj.enableAllPermissions()
    if not file_obj.path_exists:
      file_obj.createPath()
    return file_obj

  def _convertLogLevel(self, val):
    """Standardizes input to acceptable LogType.

    Args:
      val: str/int, input to be analyzed/converted.
    Returns:
      log_type: LogTypes<Enum> object
    """
    log_type = None
    if isinstance(val, str):
      if val.upper() in [x.name for x in LogTypes]:
        log_type = LogTypes[val.upper()]
    elif isinstance(val, int):
      if val % 10 == 0:
        log_type = self._convertLogLevel(val/10)
      elif 0 <= val <= 5:
        log_type = LogTypes(val)
      else:
        log_type = _DEFAULT_LOG_LEVEL
    elif isinstance(val, type(LogTypes.INFO)):
      # fall-thru -- don't alter
      log_type = val
    else:
      log_type = _DEFAULT_LOG_LEVEL
    return log_type

  def _validMsgArgs(self, msg, *args):
    """Ensure msg contains same # of placeholders as len(args)."""
    return msg.count('{}') <= len(args) and msg

  def _getLogLevelMethod(self, lvl):
    """Retrieve logging action based on input.

    Args:
      lvl: LogTypes object
    Return:
      logging.info/debug/error/etc method
    """
    lvl = self._convertLogLevel(lvl) if not isinstance(lvl, type(LogTypes.INFO)) else lvl
    if lvl.value:
      return getattr(self.logger, lvl.name.lower())

    return None

  def write(self, msg=None, *args, **kwargs):
    if datetime_util.now(True).hour != self.log_hour:
      self.ready = False
      self._closeHandlers()

    if not self.ready:
      self._initLogs(self.user)
      self._initDataConnection()
      self._initLogHandlers()

    lvl = None
    for key in ['level', 'lvl', 'logtype', 'log_type']:
      if key in [x.lower() for x in kwargs.keys()]:
        lvl = [v for k, v in kwargs.iteritems() if k.lower() == key][0]
    kwargs['extra'] = self.extra
    lvl = getattr(logging, self._convertLogLevel(lvl).name)
    write_func = self._getLogLevelMethod(lvl)
    if self._validMsgArgs(msg, *args) and write_func:
      msg = msg.format(*args) if args else msg
      write_func(msg, **kwargs)
    else:
      msg = err_msg.LOG_MSG_MISMATCH.format(msg, msg.count('{}'), args, kwargs)
      self.logger.debug(msg, extra=self.extra)

SYSLOG = Log('system')

