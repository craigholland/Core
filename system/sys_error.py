"""System-level error-handling and logging."""

import os
import logging
import enum
import inspect

from utils import constants
from utils import file_util
from utils import user_util


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






# def Alert(err_msg, err_type, do_raise=False, do_log=True, log_type=LogTypes.INFO):
#     if err_type in _ERROR_TYPES:
#       if do_log:

