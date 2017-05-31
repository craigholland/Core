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
  TIME_SERIES_INTRADAY = 1
  TIME_SERIES_DAILY = 2
  TIME_SERIES_DAILY_ADJUSTED = 3
  TIME_SERIES_WEEKLY = 4
  TIME_SERIES_MONTHLY = 5
  SMA = 6
  EMA = 7
  DEMA = 8
  TEMA = 9
  TRIMA = 10
  KAMA = 11
  MAMA = 12
  T3 = 13
  MACD = 14
  MACDEXT = 15
  STOCH = 16
  STOCHF = 17
  RSI = 18
  STOCHRSI = 19
  WILLR = 20
  ADX = 21
  ADXR = 22
  APO = 23
  PP0 = 24
  MOM = 25
  BOP = 26
  CCI = 27
  CMO = 28
  ROC = 29
  ROCR = 30
  AROON = 31
  AROONOSC = 32
  MFI = 33
  TRIX = 34
  ULTOSC = 35
  DX = 36
  MINUS_DI = 37
  PLUS_DI = 38
  MINUS_DM = 39
  PLUS_DM = 40
  BBANDS = 41
  MIDPOINT = 42
  MIDPRICE = 43
  SAR = 44
  TRANGE = 45
  ATR = 46
  NATR = 47
  AD = 48
  ADOSC = 49
  OBV = 50
  HT_TRENDLINE = 51
  HT_SINE = 52
  HT_TRENDMODE = 53
  HT_DCPERIOD = 54
  HT_DCPHASE = 55
  HT_PHASOR = 56
  SECTOR = 57

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

class AV_Query(core_message.Message):
  function = core_message.EnumField(AV_Function, 1, required=True)
  req_param = core_message.EnumField(AV_Parameters, 2, repeated=True)
  opt_param = core_message.EnumField(AV_Parameters, 3, repeated=True)

