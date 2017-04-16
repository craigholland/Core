
def _lateimportMessage():
  from core.base import core_message as cm
  return cm.Message, cm.MessageField


def _lateimportField():
  from core.base import core_field as cf
  return cf.StringField, cf.IntegerField

Message, MessageField = _lateimportMessage()
StringField, IntegerField = _lateimportField()


class MsgKey(Message):
  key = StringField(1, required=True)
  value = StringField(2)

class LocalKey(Message):
  desc = StringField(2)
  location = StringField(3)
  messages = MessageField(MsgKey, 4, repeated=True)

def msgkey(key, value):
  return MsgKey(key=key, value=value)


def localkey(key, desc=None, location=None, messages=None):
  return LocalKey(key=key, desc=desc, location=location, messages=messages)

__all__ = ['localkey', 'msgkey', 'LocalKey', 'MsgKey']
