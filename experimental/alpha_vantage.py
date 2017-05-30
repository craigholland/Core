import urllib2
import json
from core import core_constants

_API_KEY = 'T3HW'

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

class AlphaVantage():
  _OUTPUTSIZE = 'compact'
  _BASE = 'http://www.alphavantage.co/query?'

  def __init__(self):
    self.apikey = _API_KEY

  def TS_Intraday(self, symbol, interval='60min'):
    query = dict_to_querystring({
      'apikey': self.apikey,
      'function': 'TIME_SERIES_INTRADAY',
      'symbol': symbol,
      'interval': interval,
      'outputsize': self._OUTPUTSIZE
    })
    print query
    return json.loads(GetDataFromURL(self._BASE + query).encode('utf-8'))

