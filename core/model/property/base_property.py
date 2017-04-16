from core.model.core_model_utils import *
from core import core_utils as utils
from core.errors_old.core_error import *
from core.model.property.property_errors import *

class Property(ModelAttribute):
  """A class describing a typed, persisted attribute of a Cloud Datastore entity.

  Not to be confused with Python's 'property' built-in.

  This is just a base class; there are specific subclasses that
  describe Properties of various types (and GenericProperty which
  describes a dynamically typed property).

  All special property attributes, even those considered 'public',
  have names starting with an underscore, because StructuredProperty
  uses the non-underscore attribute namespace to refer to nested
  property names; this is essential for specifying queries on
  subproperties (see the module docstring).

  The property class and its predefined subclasses allow easy
  subclassing using composable (or stackable) validation and
  conversion APIs.  These require some terminology definitions:

  - A 'user value' is a value such as would be set and accessed by the
    application code using standard attributes on the entity.

  - A 'base value' is a value such as would be serialized to
    and deserialized from Cloud Datastore.

  The values stored in ent._values[name] and accessed by
  _store_value() and _retrieve_value() can be either user values or
  base values.  To retrieve user values, use
  _get_user_value().  To retrieve base values, use
  _get_base_value().  In particular, _get_value() calls
  _get_user_value(), and _serialize() effectively calls
  _get_base_value().

  To store a user value, just call _store_value().  To store a
  base value, wrap the value in a _BaseValue() and then
  call _store_value().

  A property subclass that wants to implement a specific
  transformation between user values and serializable values should
  implement two methods, _to_base_type() and _from_base_type().
  These should *NOT* call their super() method; super calls are taken
  care of by _call_to_base_type() and _call_from_base_type().
  This is what is meant by composable (or stackable) APIs.

  The API supports 'stacking' classes with ever more sophisticated
  user<-->base conversions: the user-->base conversion
  goes from more sophisticated to less sophisticated, while the
  base-->user conversion goes from less sophisticated to more
  sophisticated.  For example, see the relationship between
  BlobProperty, TextProperty and StringProperty.

  In addition to _to_base_type() and _from_base_type(), the
  _validate() method is also a composable API.

  The validation API distinguishes between 'lax' and 'strict' user
  values.  The set of lax values is a superset of the set of strict
  values.  The _validate() method takes a lax value and if necessary
  converts it to a strict value.  This means that when setting the
  property value, lax values are accepted, while when getting the
  property value, only strict values will be returned.  If no
  conversion is needed, _validate() may return None.  If the argument
  is outside the set of accepted lax values, _validate() should raise
  an exception, preferably TypeError or
  datastore_errors.BadValueError.

  Example/boilerplate:

  def _validate(self, value):
    'Lax user value to strict user value.'
    if not isinstance(value, <top type>):
      raise TypeError(...)  # Or datastore_errors.BadValueError(...).

  def _to_base_type(self, value):
    '(Strict) user value to base value.'
    if isinstance(value, <user type>):
      return <base type>(value)

  def _from_base_type(self, value):
    'base value to (strict) user value.'
    if not isinstance(value, <base type>):
      return <user type>(value)

  Things that _validate(), _to_base_type() and _from_base_type()
  do *not* need to handle:

  - None: They will not be called with None (and if they return None,
    this means that the value does not need conversion).

  - Repeated values: The infrastructure (_get_user_value() and
    _get_base_value()) takes care of calling
    _from_base_type() or _to_base_type() for each list item in a
    repeated value.

  - Wrapping values in _BaseValue(): The wrapping and unwrapping is
    taken care of by the infrastructure that calls the composable APIs.

  - Comparisons: The comparison operations call _to_base_type() on
    their operand.

  - Distinguishing between user and base values: the
    infrastructure guarantees that _from_base_type() will be called
    with an (unwrapped) base value, and that
    _to_base_type() will be called with a user value.

  - Returning the original value: if any of these return None, the
    original value is kept.  (Returning a differen value not equal to
    None will substitute the different value.)
  """

  # TODO: Separate 'simple' properties from base property class

  _code_name = None
  _name = None
  _indexed = True
  _repeated = False
  _required = False
  _default = None
  _choices = None
  _validator = None
  _verbose_name = None
  _write_empty_list = False

  __creation_counter_global = 0

  _attributes = ['_name', '_indexed', '_repeated', '_required', '_default',
                 '_choices', '_validator', '_verbose_name',
                 '_write_empty_list']
  _positional = 1  # Only name is a positional argument.

  @utils.positional(1 + _positional)  # Add 1 for self.
  def __init__(self, name=None, indexed=None, repeated=None,
               required=None, default=None, choices=None, validator=None,
               verbose_name=None, write_empty_list=None):
    """Constructor.  For arguments see the module docstring."""
    if name is not None:
      if isinstance(name, unicode):
        name = name.encode('utf-8')
      if not isinstance(name, str):
        raise TypeError('Name %r is not a string' % (name,))
      if '.' in name:
        raise ValueError('Name %r cannot contain period characters' % (name,))
      self._name = name
    if indexed is not None:
      self._indexed = indexed
    if repeated is not None:
      self._repeated = repeated
    if required is not None:
      self._required = required
    if default is not None:
      # TODO: Call _validate() on default?
      self._default = default
    if verbose_name is not None:
      self._verbose_name = verbose_name
    if write_empty_list is not None:
      self._write_empty_list = write_empty_list
    if self._repeated and (self._required or self._default is not None):
      raise ValueError('repeated is incompatible with required or default')
    if choices is not None:
      if not isinstance(choices, (list, tuple, set, frozenset)):
        raise TypeError('choices must be a list, tuple or set; received %r' %
                        choices)
      # TODO: Call _validate() on each choice?
      self._choices = frozenset(choices)
    if validator is not None:
      # The validator is called as follows:
      #   value = validator(prop, value)
      # It should return the value to be used, or raise an exception.
      # It should be idempotent, i.e. calling it a second time should
      # not further modify the value.  So a validator that returns e.g.
      # value.lower() or value.strip() is fine, but one that returns
      # value + '$' is not.
      if not hasattr(validator, '__call__'):
        raise TypeError('validator must be callable or None; received %r' %
                        validator)
      self._validator = validator
    # Keep a unique creation counter.
    Property.__creation_counter_global += 1
    self._creation_counter = Property.__creation_counter_global

  def __repr__(self):
    """Return a compact unambiguous string representation of a property."""
    args = []
    cls = self.__class__
    for i, attr in enumerate(self._attributes):
      val = getattr(self, attr)
      if val is not getattr(cls, attr):
        if isinstance(val, type):
          s = val.__name__
        else:
          s = repr(val)
        if i >= cls._positional:
          if attr.startswith('_'):
            attr = attr[1:]
          s = '%s=%s' % (attr, s)
        args.append(s)
    s = '%s(%s)' % (self.__class__.__name__, ', '.join(args))
    return s

  def _datastore_type(self, value):
    """Internal hook used by property filters.

    Sometimes the low-level query interface needs a specific data type
    in order for the right filter to be constructed.  See _comparison().
    """
    return value

  def _comparison(self, op, value):
    """Internal helper for comparison operators.

    Args:
      op: The operator ('=', '<' etc.).

    Returns:
      A FilterNode instance representing the requested comparison.
    """
    # NOTE: This is also used by query.gql().
    if not self._indexed:
      raise BadFilterError(
          'Cannot query for unindexed property %s' % self._name)
    from .query import FilterNode  # Import late to avoid circular imports.
    if value is not None:
      value = self._do_validate(value)
      value = self._call_to_base_type(value)
      value = self._datastore_type(value)
    return FilterNode(self._name, op, value)

  # Comparison operators on property instances don't compare the
  # properties; instead they return FilterNode instances that can be
  # used in queries.  See the module docstrings above and in query.py
  # for details on how these can be used.

  def __eq__(self, value):
    """Return a FilterNode instance representing the '=' comparison."""
    return self._comparison('=', value)

  def __ne__(self, value):
    """Return a FilterNode instance representing the '!=' comparison."""
    return self._comparison('!=', value)

  def __lt__(self, value):
    """Return a FilterNode instance representing the '<' comparison."""
    return self._comparison('<', value)

  def __le__(self, value):
    """Return a FilterNode instance representing the '<=' comparison."""
    return self._comparison('<=', value)

  def __gt__(self, value):
    """Return a FilterNode instance representing the '>' comparison."""
    return self._comparison('>', value)

  def __ge__(self, value):
    """Return a FilterNode instance representing the '>=' comparison."""
    return self._comparison('>=', value)

# TEMP-REMOVE
#   # pylint: disable=invalid-name
#   def _IN(self, value):
#     """Comparison operator for the 'in' comparison operator.
#
#     The Python 'in' operator cannot be overloaded in the way we want
#     to, so we define a method.  For example::
#
#       Employee.query(Employee.rank.IN([4, 5, 6]))
#
#     Note that the method is called ._IN() but may normally be invoked
#     as .IN(); ._IN() is provided for the case you have a
#     StructuredProperty with a model that has a property named IN.
#     """
#     if not self._indexed:
#       raise BadFilterError(
#           'Cannot query for unindexed property %s' % self._name)
#     from .query import FilterNode  # Import late to avoid circular imports.
#     if not isinstance(value, (list, tuple, set, frozenset)):
#       raise BadArgumentError(
#           'Expected list, tuple or set, got %r' % (value,))
#     values = []
#     for val in value:
#       if val is not None:
#         val = self._do_validate(val)
#         val = self._call_to_base_type(val)
#         val = self._datastore_type(val)
#       values.append(val)
#     return FilterNode(self._name, 'in', values)
#   IN = _IN
#
#   def __neg__(self):
#     """Return a descending sort order on this property.
#
#     For example::
#
#       Employee.query().order(-Employee.rank)
#     """
#     return datastore_query.PropertyOrder(
#         self._name, datastore_query.PropertyOrder.DESCENDING)
#
#   def __pos__(self):
#     """Return an ascending sort order on this property.
#
#     Note that this is redundant but provided for consistency with
#     __neg__.  For example, the following two are equivalent::
#
#       Employee.query().order(+Employee.rank)
#       Employee.query().order(Employee.rank)
#     """
#     return datastore_query.PropertyOrder(self._name)

  def _do_validate(self, value):
    """Call all validations on the value.

    This calls the most derived _validate() method(s), then the custom
    validator function, and then checks the choices.  It returns the
    value, possibly modified in an idempotent way, or raises an
    exception.

    Note that this does not call all composable _validate() methods.
    It only calls _validate() methods up to but not including the
    first _to_base_type() method, when the MRO is traversed looking
    for _validate() and _to_base_type() methods.  (IOW if a class
    defines both _validate() and _to_base_type(), its _validate()
    is called and then the search is aborted.)

    Note that for a repeated property this function should be called
    for each item in the list, not for the list as a whole.
    """
    if isinstance(value, _BaseValue):
      return value
    value = self._call_shallow_validation(value)
    if self._validator is not None:
      newvalue = self._validator(self, value)
      if newvalue is not None:
        value = newvalue
    if self._choices is not None:
      if value not in self._choices:
        raise BadValueError(
            'Value %r for property %s is not an allowed choice' %
            (value, self._name))
    return value

  def _fix_up(self, cls, code_name):
    """Internal helper called to tell the property its name.

    This is called by _fix_up_properties() which is called by
    MetaModel when finishing the construction of a Model subclass.
    The name passed in is the name of the class attribute to which the
    property is assigned (a.k.a. the code name).  Note that this means
    that each property instance must be assigned to (at most) one
    class attribute.  E.g. to declare three strings, you must call
    StringProperty() three times, you cannot write

      foo = bar = baz = StringProperty()
    """
    self._code_name = code_name
    if self._name is None:
      self._name = code_name

  def _store_value(self, entity, value):
    """Internal helper to store a value in an entity for a property.

    This assumes validation has already taken place.  For a repeated
    property the value should be a list.
    """
    entity._values[self._name] = value

  def _set_value(self, entity, value):
    """Internal helper to set a value in an entity for a property.

    This performs validation first.  For a repeated property the value
    should be a list.
    """
    if entity._projection:
      raise ReadonlyPropertyError(
          'You cannot set property values of a projection entity')
    if self._repeated:
      if not isinstance(value, (list, tuple, set, frozenset)):
        raise BadValueError('Expected list or tuple, got %r' %
                                             (value,))
      value = [self._do_validate(v) for v in value]
    else:
      if value is not None:
        value = self._do_validate(value)
    self._store_value(entity, value)

  def _has_value(self, entity, unused_rest=None):
    """Internal helper to ask if the entity has a value for this property."""
    return self._name in entity._values

  def _retrieve_value(self, entity, default=None):
    """Internal helper to retrieve the value for this property from an entity.

    This returns None if no value is set, or the default argument if
    given.  For a repeated property this returns a list if a value is
    set, otherwise None.  No additional transformations are applied.
    """
    return entity._values.get(self._name, default)

  def _get_user_value(self, entity):
    """Return the user value for this property of the given entity.

    This implies removing the _BaseValue() wrapper if present, and
    if it is, calling all _from_base_type() methods, in the reverse
    method resolution order of the property's class.  It also handles
    default values and repeated properties.
    """
    return self._apply_to_values(entity, self._opt_call_from_base_type)

  def _get_base_value(self, entity):
    """Return the base value for this property of the given entity.

    This implies calling all _to_base_type() methods, in the method
    resolution order of the property's class, and adding a
    _BaseValue() wrapper, if one is not already present.  (If one
    is present, no work is done.)  It also handles default values and
    repeated properties.
    """
    return self._apply_to_values(entity, self._opt_call_to_base_type)

  # TODO: Invent a shorter name for this.
  def _get_base_value_unwrapped_as_list(self, entity):
    """Like _get_base_value(), but always returns a list.

    Returns:
      A new list of unwrapped base values.  For an unrepeated
      property, if the value is missing or None, returns [None]; for a
      repeated property, if the original value is missing or None or
      empty, returns [].
    """
    wrapped = self._get_base_value(entity)
    if self._repeated:
      if wrapped is None:
        return []
      assert isinstance(wrapped, list)
      return [w.b_val for w in wrapped]
    else:
      if wrapped is None:
        return [None]
      assert isinstance(wrapped, _BaseValue)
      return [wrapped.b_val]

  def _opt_call_from_base_type(self, value):
    """Call _from_base_type() if necessary.

    If the value is a _BaseValue instance, unwrap it and call all
    _from_base_type() methods.  Otherwise, return the value
    unchanged.
    """
    if isinstance(value, _BaseValue):
      value = self._call_from_base_type(value.b_val)
    return value

  def _value_to_repr(self, value):
    """Turn a value (base or not) into its repr().

    This exists so that property classes can override it separately.
    """
    # Manually apply _from_base_type() so as not to have a side
    # effect on what's contained in the entity.  Printing a value
    # should not change it!
    val = self._opt_call_from_base_type(value)
    return repr(val)

  def _opt_call_to_base_type(self, value):
    """Call _to_base_type() if necessary.

    If the value is a _BaseValue instance, return it unchanged.
    Otherwise, call all _validate() and _to_base_type() methods and
    wrap it in a _BaseValue instance.
    """
    if not isinstance(value, _BaseValue):
      value = _BaseValue(self._call_to_base_type(value))
    return value

  def _call_from_base_type(self, value):
    """Call all _from_base_type() methods on the value.

    This calls the methods in the reverse method resolution order of
    the property's class.
    """
    methods = self._find_methods('_from_base_type', reverse=True)
    call = self._apply_list(methods)
    return call(value)

  def _call_to_base_type(self, value):
    """Call all _validate() and _to_base_type() methods on the value.

    This calls the methods in the method resolution order of the
    property's class.
    """
    methods = self._find_methods('_validate', '_to_base_type')
    call = self._apply_list(methods)
    return call(value)

  def _call_shallow_validation(self, value):
    """Call the initial set of _validate() methods.

    This is similar to _call_to_base_type() except it only calls
    those _validate() methods that can be called without needing to
    call _to_base_type().

    An example: suppose the class hierarchy is A -> B -> C ->
    property, and suppose A defines _validate() only, but B and C
    define _validate() and _to_base_type().  The full list of
    methods called by _call_to_base_type() is::

      A._validate()
      B._validate()
      B._to_base_type()
      C._validate()
      C._to_base_type()

    This method will call A._validate() and B._validate() but not the
    others.
    """
    methods = []
    for method in self._find_methods('_validate', '_to_base_type'):
      if method.__name__ != '_validate':
        break
      methods.append(method)
    call = self._apply_list(methods)
    return call(value)

  @classmethod
  def _find_methods(cls, *names, **kwds):
    """Compute a list of composable methods.

    Because this is a common operation and the class hierarchy is
    static, the outcome is cached (assuming that for a particular list
    of names the reversed flag is either always on, or always off).

    Args:
      *names: One or more method names.
      reverse: Optional flag, default False; if True, the list is
        reversed.

    Returns:
      A list of callable class method objects.
    """
    reverse = kwds.pop('reverse', False)
    assert not kwds, repr(kwds)
    cache = cls.__dict__.get('_find_methods_cache')
    if cache:
      hit = cache.get(names)
      if hit is not None:
        return hit
    else:
      cls._find_methods_cache = cache = {}
    methods = []
    for c in cls.__mro__:
      for name in names:
        method = c.__dict__.get(name)
        if method is not None:
          methods.append(method)
    if reverse:
      methods.reverse()
    cache[names] = methods
    return methods

  def _apply_list(self, methods):
    """Return a single callable that applies a list of methods to a value.

    If a method returns None, the last value is kept; if it returns
    some other value, that replaces the last value.  Exceptions are
    not caught.
    """
    def call(value):
      for method in methods:
        newvalue = method(self, value)
        if newvalue is not None:
          value = newvalue
      return value
    return call

  def _apply_to_values(self, entity, function):
    """Apply a function to the property value/values of a given entity.

    This retrieves the property value, applies the function, and then
    stores the value back.  For a repeated property, the function is
    applied separately to each of the values in the list.  The
    resulting value or list of values is both stored back in the
    entity and returned from this method.
    """
    value = self._retrieve_value(entity, self._default)
    if self._repeated:
      if value is None:
        value = []
        self._store_value(entity, value)
      else:
        value[:] = map(function, value)
    else:
      if value is not None:
        newvalue = function(value)
        if newvalue is not None and newvalue is not value:
          self._store_value(entity, newvalue)
          value = newvalue
    return value

  def _get_value(self, entity):
    """Internal helper to get the value for this property from an entity.

    For a repeated property this initializes the value to an empty
    list if it is not set.
    """
    if entity._projection:
      if self._name not in entity._projection:
        raise UnprojectedPropertyError(
            'property %s is not in the projection' % (self._name,))
    return self._get_user_value(entity)

  def _delete_value(self, entity):
    """Internal helper to delete the value for this property from an entity.

    Note that if no value exists this is a no-op; deleted values will
    not be serialized but requesting their value will return None (or
    an empty list in the case of a repeated property).
    """
    if self._name in entity._values:
      del entity._values[self._name]

  def _is_initialized(self, entity):
    """Internal helper to ask if the entity has a value for this property.

    This returns False if a value is stored but it is None.
    """
    return (not self._required or
            ((self._has_value(entity) or self._default is not None) and
             self._get_value(entity) is not None))

  def __get__(self, entity, unused_cls=None):
    """Descriptor protocol: get the value from the entity."""
    if entity is None:
      return self  # __get__ called on class
    return self._get_value(entity)

  def __set__(self, entity, value):
    """Descriptor protocol: set the value on the entity."""
    self._set_value(entity, value)

  def __delete__(self, entity):
    """Descriptor protocol: delete the value from the entity."""
    self._delete_value(entity)

# TEMP-REMOVE:
#   def _serialize(self, entity, pb, prefix='', parent_repeated=False,
#                  projection=None):
#     """Internal helper to serialize this property to a protocol buffer.
#
#     Subclasses may override this method.
#
#     Args:
#       entity: The entity, a Model (subclass) instance.
#       pb: The protocol buffer, an EntityProto instance.
#       prefix: Optional name prefix used for StructuredProperty
#         (if present, must end in '.').
#       parent_repeated: True if the parent (or an earlier ancestor)
#         is a repeated property.
#       projection: A list or tuple of strings representing the projection for
#         the model instance, or None if the instance is not a projection.
#     """
#     values = self._get_base_value_unwrapped_as_list(entity)
#     name = prefix + self._name
#     if projection and name not in projection:
#       return
#
#     if self._indexed:
#       create_prop = lambda: pb.add_property()
#     else:
#       create_prop = lambda: pb.add_raw_property()
#
#     if self._repeated and not values and self._write_empty_list:
#       # We want to write the empty list
#       p = create_prop()
#       p.set_name(name)
#       p.set_multiple(False)
#       p.set_meaning(entity_pb.Property.EMPTY_LIST)
#       p.mutable_value()
#     else:
#       # We write a list, or a single property
#       for val in values:
#         p = create_prop()
#         p.set_name(name)
#         p.set_multiple(self._repeated or parent_repeated)
#         v = p.mutable_value()
#         if val is not None:
#           self._db_set_value(v, p, val)
#           if projection:
#             # Projected properties have the INDEX_VALUE meaning and only contain
#             # the original property's name and value.
#             new_p = entity_pb.Property()
#             new_p.set_name(p.name())
#             new_p.set_meaning(entity_pb.Property.INDEX_VALUE)
#             new_p.set_multiple(False)
#             new_p.mutable_value().CopyFrom(v)
#             p.CopyFrom(new_p)
#
#   def _deserialize(self, entity, p, unused_depth=1):
#     """Internal helper to deserialize this property from a protocol buffer.
#
#     Subclasses may override this method.
#
#     Args:
#       entity: The entity, a Model (subclass) instance.
#       p: A property Message object (a protocol buffer).
#       depth: Optional nesting depth, default 1 (unused here, but used
#         by some subclasses that override this method).
#     """
#     if p.meaning() == entity_pb.Property.EMPTY_LIST:
#       self._store_value(entity, [])
#       return
#
#     val = self._db_get_value(p.value(), p)
#     if val is not None:
#       val = _BaseValue(val)
#
#     # TODO: replace the remainder of the function with the following commented
#     # out code once its feasible to make breaking changes such as not calling
#     # _store_value().
#
#     # if self._repeated:
#     #   entity._values.setdefault(self._name, []).append(val)
#     # else:
#     #   entity._values[self._name] = val
#
#     if self._repeated:
#       if self._has_value(entity):
#         value = self._retrieve_value(entity)
#         assert isinstance(value, list), repr(value)
#         value.append(val)
#       else:
#         # We promote single values to lists if we are a list property
#         value = [val]
#     else:
#       value = val
#     self._store_value(entity, value)

  def _prepare_for_put(self, entity):
    pass

  def _check_property(self, rest=None, require_indexed=True):
    """Internal helper to check this property for specific requirements.

    Called by Model._check_properties().

    Args:
      rest: Optional subproperty to check, of the form 'name1.name2...nameN'.

    Raises:
      InvalidPropertyError if this property does not meet the given
      requirements or if a subproperty is specified.  (StructuredProperty
      overrides this method to handle subproperties.)
    """
    if require_indexed and not self._indexed:
      raise InvalidPropertyError('property is unindexed %s' % self._name)
    if rest:
      raise InvalidPropertyError('Referencing subproperty %s.%s '
                                 'but %s is not a structured property' %
                                 (self._name, rest, self._name))

  def _get_for_dict(self, entity):
    """Retrieve the value like _get_value(), processed for _to_dict().

    property subclasses can override this if they want the dictionary
    returned by entity._to_dict() to contain a different value.  The
    main use case is StructuredProperty and LocalStructuredProperty.

    NOTES::

    - If you override _get_for_dict() to return a different type, you
      must override _validate() to accept values of that type and
      convert them back to the original type.

    - If you override _get_for_dict(), you must handle repeated values
      and None correctly.  (See _StructuredGetForDictMixin for an
      example.)  However, _validate() does not need to handle these.
    """
    return self._get_value(entity)




