"""Datetime utilities."""
import datetime as dt
from utils import constants

def now(utc=False):
  d = dt.datetime.now(tz=constants.LOCAL_TIMEZONE)
  if utc:
    return d.astimezone(constants.UTC_TIMEZONE)
  else:
    return d


def asDict(date_obj):
  tt = date_obj.timetuple()
  return {'yr': tt.tm_year,
          'mo': tt.tm_mon,
          'dy': tt.tm_mday,
          'hr': tt.tm_hour,
          'mi': tt.tm_min,
          'sc': tt.tm_sec,
          'DYint': tt.tm_wday,
          'YRDYint': tt.tm_yday,
          'isdst': tt.tm_isdst
          }


def convertToUTC(date_obj):
  tzinfo = date_obj.tzinfo
  if not tzinfo:
    #Assume local time.
    date_obj = date_obj.replace(tzinfo=constants.LOCAL_TIMEZONE)
  return date_obj.astimezone(constants.UTC_TIMEZONE)


def forceUTC(func):
  """Decorator that converts any datetime object to UTC."""

  def wrapper(*args, **kwargs):
    args = list(args)
    for idx, arg in enumerate(args):
      if isinstance(arg, dt.datetime):
        args[idx] = convertToUTC(arg)
    for k, v in kwargs:
      if isinstance(v, dt.datetime):
        kwargs[k] = convertToUTC(v)
    return func(*args, **kwargs)
  return wrapper

@forceUTC
def test(non_date_str, date_obj, kw1=False, kw2='hi'):
  def NDS():
    return 'non_date_str: {0}'

  def DOS():
    return 'date_obj: {0}'

  print NDS().format(non_date_str)
  print DOS().format(date_obj)
  print kw1
  print kw2