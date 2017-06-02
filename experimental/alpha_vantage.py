import urllib2
import inspect
import json
import types
from core import core_constants
from experimental import alpha_vantage_message as avm
from core.utils import file_util

_API_KEY = 'T3HW'

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

def parseAVjson(val):
    retval = {}
    if isinstance(val, dict):
        for k, v in val.iteritems():
            retval[str(k)] = parseAVjson(v)
            if str(k) == '2017-05-10':
                break
    elif isinstance(val, list):
        return [parseAVjson(x) for x in val]
    elif isinstance(val, str):
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
    return retval


class AlphaVantage(object):

  _BASE = 'http://www.alphavantage.co/query?'
  _AV_COMMANDS_MAP = 'av_func_param_map.json'
  _REQD_PARAMS = ['apikey', 'symbol']

  def __init__(self, symbol=None):
    self.apikey = _API_KEY
    self.symbol = None
    if symbol:
      #validate symbol first
      self.symbol = symbol

    commands = file_util.File('', self._AV_COMMANDS_MAP)
    self.command_dict = json.loads(commands.Read())
    if not self._test_AVFunction():
      pass
      #Error Message here

    for cmd in self.command_dict.keys():
      cmd = str(cmd)
      setattr(self, cmd, copyFunction(self._av_template, cmd, 0))
      setattr(self, cmd, self.av_wrapper(getattr(self, cmd)))



    self._testConfig()

  @staticmethod
  def _av_template(**kwargs):
      pass

  def av_wrapper(self, func):
    def wrapper(**kwargs):
      command = func.__name__
      cmd_dct = self.command_dict[command]
      req, opt = cmd_dct['req'], cmd_dct['opt']
      if self.symbol and self._validateCommandParam(kwargs, req, opt):
        # validate param values
        kwargs['symbol'] = self.symbol
        kwargs['apikey'] = _API_KEY
        kwargs['function'] = command
        query = dict_to_querystring(kwargs)
        return parseAVjson(json.loads(GetDataFromURL(self._BASE + query)))
    return wrapper

  def _validateCommandParam(self, params, req, opt):
    """
    Args:
      params: dict, dict of params in func.
      req: list, list of required params for func.
      opt: list, list of optional params for func.
    Returns:
      retval: bool, validation result
    """
    retval = True
    if isinstance(params, dict):
      pkeys = set(params.keys())
      if len(pkeys - set(req) - set(opt)):
        print 'Unexpected Parameter'
        retval = False
      if len(set(req) - pkeys):
        print 'Missing Parameter'
        retval = False
    else:
      print 'Invalid Param Dict'
      retval = False

    return retval


  def _test_AVFunction(self):
    com_map = set(self.command_dict.keys())
    com_enum = set(avm.AV_Function.names())
    if len(com_map ^ com_enum):
      return False
    return True
  def _testConfig(self):
    test = True
    if not self._test_AVFunction():
      print 'Command Config Error'
      test = False
    return test


  def test_TS_Intraday(self, symbol, interval='60min'):
    query = dict_to_querystring({
      'apikey': self.apikey,
      'function': 'TIME_SERIES_INTRADAY',
      'symbol': symbol,
      'interval': interval,
      'outputsize': self._OUTPUTSIZE
    })
    print query
    return json.loads(GetDataFromURL(self._BASE + query).encode('utf-8'))

