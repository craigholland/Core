
def _lateimportMessage():
  from core.base import core_message as cm
  return cm.Message, cm.MessageField


def _lateimportField():
  from core.base import core_field as cf
  return cf.StringField, cf.IntegerField

Message, MessageField = _lateimportMessage()
StringField, IntegerField = _lateimportField()


class ErrMsg(Message):
  key = StringField(1, required=True)
  value = StringField(2)

class LocalKey(Message):
  key = StringField(1, required=True)
  desc = StringField(2)
  location = StringField(3)
  messages = MessageField(ErrMsg, 4, repeated=True)


def errmsg(key, value):
  return ErrMsg(key=key, value=value)


def localkey(key, desc=None, location=None, messages=None):
  return LocalKey(key=key, desc=desc, location=location, messages=messages)

__all__ = ['localkey', 'errmsg']
