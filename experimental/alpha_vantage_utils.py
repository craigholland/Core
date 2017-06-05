import types
import urllib2
from core import core_constants
from core.errors.core_error import Error

def copyFunction(func, name, args):
  f_code = types.CodeType(args,
                          func.func_code.co_nlocals,
                          func.func_code.co_stacksize,
                          func.func_code.co_flags,
                          func.func_code.co_code,
                          func.func_code.co_consts,
                          func.func_code.co_names,
                          func.func_code.co_varnames,
                          func.func_code.co_filename,
                          name,
                          func.func_code.co_firstlineno,
                          func.func_code.co_lnotab)
  return types.FunctionType(f_code, func.func_globals, name)


def GetDataFromURL(url, head=core_constants.URL_HEADER):
  response = urllib2.Request(url, headers=head)
  con = urllib2.urlopen(response)
  return con.read()


def dict_to_querystring(d):
  q = ''
  for k, v in d.iteritems():
    if q:
      q += '&'
    q += '{0}={1}'.format(k, v)
  return q


def format_timeseries_keys(key_name):
  titles = ['open', 'close', 'low', 'high', 'volume', 'information',
            'symbol', 'last refreshed', 'time zone']
  if any(map(lambda x: x in key_name.lower(), titles)):
    key_name = key_name.split('. ')[1]
  return key_name


def parseAVjson(val, cmd):
    time_series = ["TIME_SERIES_INTRADAY", "TIME_SERIES_DAILY",
                   "TIME_SERIES_DAILY_ADJUSTED", "TIME_SERIES_WEEKLY",
                   "TIME_SERIES_MONTHLY"]
    retval = {}
    if isinstance(val, dict):
        for k, v in sorted(val.iteritems()):
          if cmd in time_series:
            k = str(format_timeseries_keys(k))
          else:
            k = str(k)
          retval[k] = parseAVjson(v, cmd)

    elif isinstance(val, list):
        return [parseAVjson(x) for x in val]
    elif isinstance(val, str) or isinstance(val, unicode):
        try:
            return int(val)
        except:
            try:
                return float(val)
            except:
                val = str(val)
                if val.lower() in ['false','true']:
                    return ['false', 'true'].index(val.lower())
                else:
                    return val
    else:
      if not isinstance(val, (float, int, bool)):
        print 'ERROR - Unexpected value type: {0} ({1})'.format(val, type(val))
    return retval

class ConversionError(Error, ValueError):
  """General Conversion Error."""

class ConversiontoIntegerError(ConversionError):
  """Conversion to Integer Error."""


def convert_to_int(val, errors):
  """converts val to integer.

  If given iterable, takes 0-index as input."""
  val = val[0] if isinstance(val, (dict, list)) else val

  try:
    if val:
      return int(val)
    else:
      return 0
  except ValueError:
    # errors.Add()
    return None

def convert_to_float(val, errors):
  """converts val to float.

  If given iterable, takes 0-index as input."""
  val = val[0] if isinstance(val, (dict, list)) else val

  try:
    if val:
      return float(val)
    else:
      return 0.0
  except ValueError:
    # errors.Add()
    return None





















