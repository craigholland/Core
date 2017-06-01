from core.base import core_message

def isInt(n):
  return isinstance(n, int)

def isFloat(n):
  return isinstance(n, float)

def validate_posint(n):
  return isInt(n) and n > 0

def validate_posfloat(n):
  return isFloat(n) and n > 0


class TS_Interval(core_message.Enum):
  MIN1 = 1
  MIN5 = 5
  MIN15 = 15
  MIN30 = 30
  MIN60 = 60
  DAILY = 100
  WEEKLY = 101
  MONTHLY = 102

class AV_Outputsize(core_message.Enum):
  COMPACT = 0
  FULL = 1

class AV_Series_Type(core_message.Enum):
  OPEN = 0
  HIGH = 1
  LOW = 2
  CLOSE = 3

class AV_MA_Type(core_message.Enum):
  SMA = 0
  EMA = 1
  WMA = 2
  DEMA = 3
  TEMA = 4
  TRIMA = 5
  T3_MA = 6
  KAMA = 7
  MAMA = 8

class AV_Function(core_message.Enum):
  AD = 1
  ADOSC = 2
  ADX = 3
  ADXR = 4
  APO = 5
  AROON = 6
  AROONOSC = 7
  ATR = 8
  BBANDS = 9
  BOP = 10
  CCI = 11
  CMO = 12
  DEMA = 13
  DX = 14
  EMA = 15
  HT_DCPERIOD = 16
  HT_DCPHASE = 17
  HT_PHASOR = 18
  HT_SINE = 19
  HT_TRENDLINE = 20
  HT_TRENDMODE = 21
  KAMA = 22
  MACD = 23
  MACDEXT = 24
  MAMA = 25
  MFI = 26
  MIDPOINT = 27
  MIDPRICE = 28
  MINUS_DI = 29
  MINUS_DM = 30
  MOM = 31
  NATR = 32
  OBV = 33
  PLUS_DI = 34
  PLUS_DM = 35
  PP0 = 36
  ROC = 37
  ROCR = 38
  RSI = 39
  SAR = 40
  SECTOR = 41
  SMA = 42
  STOCH = 43
  STOCHF = 44
  STOCHRSI = 45
  T3 = 46
  TEMA = 47
  TIME_SERIES_DAILY = 48
  TIME_SERIES_DAILY_ADJUSTED = 49
  TIME_SERIES_INTRADAY = 50
  TIME_SERIES_MONTHLY = 51
  TIME_SERIES_WEEKLY = 52
  TRANGE = 53
  TRIMA = 54
  TRIX = 55
  ULTOSC = 56
  WILLR = 57
  WMA = 58


_AV_Param_Validation_Map = {
  'APIKEY' : None,
  'FUNCTION' : AV_Function,
  'SYMBOL' : None ,
  'INTERVAL' : TS_Interval,
  'OUTPUTSIZE' : AV_Outputsize,
  'TIME_PERIOD' : validate_posint,
  'SERIES_TYPE' : AV_Series_Type,
  'FASTLIMIT' : validate_posfloat,
  'SLOWLIMIT' : validate_posfloat,
  'FASTPERIOD' : validate_posint,
  'SLOWPERIOD' : validate_posint,
  'SIGNALPERIOD' : validate_posint,
  'FASTMATYPE' : AV_MA_Type,
  'SLOWMATYPE' : AV_MA_Type,
  'SIGNALMATYPE' : AV_MA_Type,
  'FASTKPERIOD' : validate_posint,
  'SLOWDPERIOD' : validate_posint,
  'SLOWKMATYPE' : AV_MA_Type,
  'SLOWDMATYPE' : AV_MA_Type,
  'FASTDPERIOD' : validate_posint,
  'MATYPE' : AV_MA_Type,
  'TIMEPERIOD1' : validate_posint,
  'TIMEPERIOD2' : validate_posint,
  'TIMEPERIOD3' : validate_posint,
  'NBDEVUP' : validate_posint,
  'NBDEVDN' : validate_posint,
  'ACCELERATION' : validate_posfloat,
  'MAXIMUM' : validate_posfloat,
}

class AV_Parameters(core_message.Enum):
  APIKEY = 0
  FUNCTION = 1
  SYMBOL = 2
  INTERVAL = 3
  OUTPUTSIZE = 4
  TIME_PERIOD = 5
  SERIES_TYPE = 6
  FASTLIMIT = 7
  SLOWLIMIT = 8
  FASTPERIOD = 9
  SLOWPERIOD = 10
  SIGNALPERIOD = 11
  FASTMATYPE = 12
  SLOWMATYPE = 13
  SIGNALMATYPE = 14
  FASTKPERIOD = 15
  SLOWDPERIOD = 16
  SLOWKMATYPE = 17
  SLOWDMATYPE = 18
  FASTDPERIOD = 19
  MATYPE = 20
  TIMEPERIOD1 = 21
  TIMEPERIOD2 = 22
  TIMEPERIOD3 = 23
  NBDEVUP = 24
  NBDEVDN = 25
  ACCELERATION = 26
  MAXIMUM = 27

