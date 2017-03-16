import datetime
import dateutil.tz as tz

import os
import sys

ROOT_PATH = os.path.abspath('.')
DATA_PATH = ROOT_PATH + '/data'

LOCAL_TIMEZONE = tz.tzlocal()
UTC_TIMEZONE = tz.tzutc()
LOCAL_TIMEZONE_STR = datetime.datetime.now(tz.tzlocal()).tzname()

