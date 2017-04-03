"""Property-specific errors."""
import sys

from core.errors import core_error as errors
from core import core_utils


class KindError(errors.BadValueError):
  """Raised when an implementation for a kind can't be found.

  Also raised when the Kind is not an 8-bit string.
  """


class InvalidPropertyError(errors.Error):
  """Raised when a property is not applicable to a given use.

  For example, a property must exist and be indexed to be used in a query's
  projection or group by clause.
  """

# Mapping for legacy support.
BadProjectionError = InvalidPropertyError


class UnprojectedPropertyError(errors.Error):
  """Raised when getting a property value that's not in the projection."""


class ReadonlyPropertyError(errors.Error):
  """Raised when attempting to set a property value that is read-only."""


class ComputedPropertyError(ReadonlyPropertyError):
  """Raised when attempting to set a value to or delete a computed property."""


__all__ = core_utils.build_mod_all_list(sys.modules[__name__])
