import urllib2
import inspect
import json
import types
from core import core_constants
from experimental import alpha_vantage_utils as avu
from experimental import alpha_vantage_message as avm
from core.utils import file_util

_API_KEY = 'T3HW'

class AlphaVantage(object):

  _BASE = 'http://www.alphavantage.co/query?'
  _AV_COMMANDS_MAP = 'av_func_param_map.json'
  _REQD_PARAMS = ['apikey', 'symbol']

  def __init__(self, symbol=None):
    self.apikey = _API_KEY
    self.symbol = None
    self.commands = []
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
      self.commands.append(cmd)
      setattr(self, cmd, avu.copyFunction(self._av_template, cmd, 1))
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
        query = avu.dict_to_querystring(kwargs)
        return avu.parseAVjson(json.loads(avu.GetDataFromURL(self._BASE + query)), command)
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

