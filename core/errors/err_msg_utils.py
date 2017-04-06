def lateimportMessage():
  from core.base import core_message as cm
  return cm.Message, cm.MessageField

def lateimportField():
  from core.base import core_field as cf
  return cf.StringField, cf.IntegerField

Message, MessageField = lateimportMessage()
StringField, IntegerField = lateimportField()

class ErrMsg(Message):
  key = StringField(1, required=True)
  value = StringField(2)

class LocalKey(Message):
  key = StringField(1, required=True)
  desc = StringField(2)
  location = StringField(3)
  messages = MessageField(ErrMsg, 4, repeated=True)

class BaseKey(Message):
  key = StringField(1, required=True)
  desc = StringField(2)
  location = StringField(3)
  local_keys = MessageField(LocalKey, 4, repeated=True)


__all__ = ['LocalKey', 'BaseKey']