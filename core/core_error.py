import core_utils

Error = core_utils.Error


class EnumDefinitionError(Error):
  """Enumeration definition error."""


class FieldDefinitionError(Error):
  """Field definition error."""


class InvalidVariantError(FieldDefinitionError):
  """Invalid variant provided to field."""


class InvalidDefaultError(FieldDefinitionError):
  """Invalid default provided to field."""


class InvalidNumberError(FieldDefinitionError):
  """Invalid number provided to field."""


class MessageDefinitionError(Error):
  """Message definition error."""


class DuplicateNumberError(Error):
  """Duplicate number assigned to field."""


class DefinitionNotFoundError(Error):
  """Raised when definition is not found."""


class DecodeError(Error):
  """Error found decoding message from encoded form."""


class EncodeError(Error):
  """Error found when encoding message."""


class ValidationError(Error):
  """Invalid value for message error."""

  def __str__(self):
    """Prints string with field name if present on exception."""
    message = Error.__str__(self)
    try:
      field_name = self.field_name
    except AttributeError:
      return message
    else:
      return message