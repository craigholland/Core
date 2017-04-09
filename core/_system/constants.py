import datetime
import dateutil.tz as tz
import importlib

import os
import inspect
import sys

IMPORTER = importlib.import_module

ROOT_PATH = os.path.abspath('.').replace('\\', '/')
ERROR_PATH = ROOT_PATH + '/errors'
DATA_PATH = ROOT_PATH + '/data'
LOG_PATH = DATA_PATH + '/logs'

LOCAL_TIMEZONE = tz.tzlocal()
UTC_TIMEZONE = tz.tzutc()
LOCAL_TIMEZONE_STR = datetime.datetime.now(tz.tzlocal()).tzname()

