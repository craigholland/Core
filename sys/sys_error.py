"""System-level error-handling and logging."""

import os
import logging
import enum
import inspect

_COMMON_ERROR_TYPES = frozenset(
    ['AttributeError',
     'TypeError',
     'ValueError'])

_ERROR_TYPES = frozenset(list(_COMMON_ERROR_TYPES) + [
    'ArithmeticError',
    'AssertionError'
    'BaseException',
    'BufferError',
    'FloatingPointError'])

_LogNames = ['USERLOG', 'SYSLOG']

def _getUserIP():
  return 'hollandc', '192.168.0.1'

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
  _initialized = False

  @classmethod
  def _createLogs(cls):
      for n in _LogNames:
          setattr(cls, n, logging.getLogger(n))
      cls._initialized=True

  def __init__(self):
    self.user, self.client_ip = _getUserIP()
    self.extra = {'user': self.user, 'clientip': self.client_ip}
    if not self._initialized:
        self._createLogs()

  def _GetLog(self, log):
    if log in _LogNames:
        return getattr(self, log)





# def Alert(err_msg, err_type, do_raise=False, do_log=True, log_type=LogTypes.INFO):
#     if err_type in _ERROR_TYPES:
#       if do_log:

