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

class LogTypes(enum.Enum):

def Alert(err_msg, err_type, doRaise=False, doLog=True, log_type=):
    if err_type in _ERROR_TYPES:
