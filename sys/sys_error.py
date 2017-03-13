"""System-level error-handling and logging."""

import os
import logging
import enum

_COMMON_ERROR_TYPES = frozenset(
    ['AttributeError',
     'TypeError',
     'ValueError'])

_ERROR_TYPES = frozenset(_COMMON_ERROR_TYPES + [
    'ArithmeticError',
    'AssertionError'
    'BaseException',
    'BufferError',
    'FloatingPointError'])

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

  USERLOG = logging.getLogger('USERLOG')
  SYSLOG = logging.getLogger('SYSLOG')

  def __init__(self):
    self.user, self.client_ip = _getUserIP()
    self.extra = {'user': self.user, 'clientip': self.client_ip}


  def _GetLog(self, log):
    if log in self.__members__
    self.USERLOG



def Alert(err_msg, err_type, do_raise=False, do_log=True, log_type=LogTypes.INFO):
    if err_type in _ERROR_TYPES:
      if do_log:

