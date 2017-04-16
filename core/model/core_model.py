"""Model and Property classes and associated stuff.

A model class represents the structure of entities stored in the
datastore.  Applications define model classes to indicate the
structure of their entities, then instantiate those model classes
to create entities.

All model classes must inherit (directly or indirectly) from Model.
Through the magic of metaclasses, straightforward assignments in the
model class definition can be used to declare the model's structure::

  class Person(Model):
    name = StringProperty()
    age = IntegerProperty()

We can now create a Person entity and write it to Cloud Datastore::

  p = Person(name='Arthur Dent', age=42)
  k = p.put()

The return value from put() is a Key (see the documentation for
ndb/key.py), which can be used to retrieve the same entity later::

  p2 = k.get()
  p2 == p  # Returns True

To update an entity, simple change its attributes and write it back
(note that this doesn't change the key)::

  p2.name = 'Arthur Philip Dent'
  p2.put()

We can also delete an entity (by using the key)::

  k.delete()

The property definitions in the class body tell the system the names
and the types of the fields to be stored in Cloud Datastore, whether
they must be indexed, their default value, and more.

Many different Property types exist.  Most are indexed by default, the
exceptions indicated in the list below:

- StringProperty: a short text string, limited to 500 bytes

- TextProperty: an unlimited text string; unindexed

- BlobProperty: an unlimited byte string; unindexed

- IntegerProperty: a 64-bit signed integer

- FloatProperty: a double precision floating point number

- BooleanProperty: a bool value

- DateTimeProperty: a datetime object.  Note: App Engine always uses
  UTC as the timezone

- DateProperty: a date object

- TimeProperty: a time object

- GeoPtProperty: a geographical location, i.e. (latitude, longitude)

- KeyProperty: a Cloud Datastore Key value, optionally constrained to
  referring to a specific kind

- UserProperty: a User object (for backwards compatibility only)

- StructuredProperty: a field that is itself structured like an
  entity; see below for more details

- LocalStructuredProperty: like StructuredProperty but the on-disk
  representation is an opaque blob; unindexed

- ComputedProperty: a property whose value is computed from other
  properties by a user-defined function.  The property value is
  written to Cloud Datastore so that it can be used in queries, but the
  value from Cloud Datastore is not used when the entity is read back

- GenericProperty: a property whose type is not constrained; mostly
  used by the Expando class (see below) but also usable explicitly

- JsonProperty: a property whose value is any object that can be
  serialized using JSON; the value written to Cloud Datastore is a JSON
  representation of that object

- PickleProperty: a property whose value is any object that can be
  serialized using Python's pickle protocol; the value written to the
  Cloud Datastore is the pickled representation of that object, using the
  highest available pickle protocol

Most Property classes have similar constructor signatures.  They
accept several optional keyword arguments:

- name=<string>: the name used to store the property value in the
  datastore.  Unlike the following options, this may also be given as
  a positional argument

- indexed=<bool>: indicates whether the property should be indexed
  (allowing queries on this property's value)

- repeated=<bool>: indicates that this property can have multiple
  values in the same entity.

- write_empty_list<bool>: For repeated value properties, controls
  whether properties with no elements (the empty list) is
  written to Datastore. If true, written, if false, then nothing
  is written to Datastore.

- required=<bool>: indicates that this property must be given a value

- default=<value>: a default value if no explicit value is given

- choices=<list of values>: a list or tuple of allowable values

- validator=<function>: a general-purpose validation function.  It
  will be called with two arguments (prop, value) and should either
  return the validated value or raise an exception.  It is also
  allowed for the function to modify the value, but calling it again
  on the modified value should not modify the value further.  (For
  example: a validator that returns value.strip() or value.lower() is
  fine, but one that returns value + '$' is not.)

- verbose_name=<value>: A human readable name for this property.  This
  human readable name can be used for html form labels.

The repeated and required/default options are mutually exclusive: a
repeated property cannot be required nor can it specify a default
value (the default is always an empty list and an empty list is always
an allowed value), but a required property can have a default.

Some property types have additional arguments.  Some property types
do not support all options.

Repeated properties are always represented as Python lists; if there
is only one value, the list has only one element.  When a new list is
assigned to a repeated property, all elements of the list are
validated.  Since it is also possible to mutate lists in place,
repeated properties are re-validated before they are written to the
datastore.

No validation happens when an entity is read from Cloud Datastore;
however property values read that have the wrong type (e.g. a string
value for an IntegerProperty) are ignored.

For non-repeated properties, None is always a possible value, and no
validation is called when the value is set to None.  However for
required properties, writing the entity to Cloud Datastore requires
the value to be something other than None (and valid).

The StructuredProperty is different from most other properties; it
lets you define a sub-structure for your entities.  The substructure
itself is defined using a model class, and the attribute value is an
instance of that model class.  However it is not stored in the
datastore as a separate entity; instead, its attribute values are
included in the parent entity using a naming convention (the name of
the structured attribute followed by a dot followed by the name of the
subattribute).  For example::

  class Address(Model):
    street = StringProperty()
    city = StringProperty()

  class Person(Model):
    name = StringProperty()
    address = StructuredProperty(Address)

  p = Person(name='Harry Potter',
             address=Address(street='4 Privet Drive',
                             city='Little Whinging'))
  k.put()

This would write a single 'Person' entity with three attributes (as
you could verify using the Datastore Viewer in the Admin Console)::

  name = 'Harry Potter'
  address.street = '4 Privet Drive'
  address.city = 'Little Whinging'

Structured property types can be nested arbitrarily deep, but in a
hierarchy of nested structured property types, only one level can have
the repeated flag set.  It is fine to have multiple structured
properties referencing the same model class.

It is also fine to use the same model class both as a top-level entity
class and as for a structured property; however queries for the model
class will only return the top-level entities.

The LocalStructuredProperty works similar to StructuredProperty on the
Python side.  For example::

  class Address(Model):
    street = StringProperty()
    city = StringProperty()

  class Person(Model):
    name = StringProperty()
    address = LocalStructuredProperty(Address)

  p = Person(name='Harry Potter',
             address=Address(street='4 Privet Drive',
                             city='Little Whinging'))
  k.put()

However the data written to Cloud Datastore is different; it writes a
'Person' entity with a 'name' attribute as before and a single
'address' attribute whose value is a blob which encodes the Address
value (using the standard"protocol buffer" encoding).

Sometimes the set of properties is not known ahead of time.  In such
cases you can use the Expando class.  This is a Model subclass that
creates properties on the fly, both upon assignment and when loading
an entity from Cloud Datastore.  For example::

  class SuperPerson(Expando):
    name = StringProperty()
    superpower = StringProperty()

  razorgirl = SuperPerson(name='Molly Millions',
                          superpower='bionic eyes, razorblade hands',
                          rasta_name='Steppin\' Razor',
                          alt_name='Sally Shears')
  elastigirl = SuperPerson(name='Helen Parr',
                           superpower='stretchable body')
  elastigirl.max_stretch = 30  # Meters

You can inspect the properties of an expando instance using the
_properties attribute:

  >>> print razorgirl._properties.keys()
  ['rasta_name', 'name', 'superpower', 'alt_name']
  >>> print elastigirl._properties
  {'max_stretch': GenericProperty('max_stretch'),
   'name': StringProperty('name'),
   'superpower': StringProperty('superpower')}

Note: this property exists for plain Model instances too; it is just
not as interesting for those.

The Model class offers basic query support.  You can create a Query
object by calling the query() class method.  Iterating over a Query
object returns the entities matching the query one at a time.

Query objects are fully described in the docstring for query.py, but
there is one handy shortcut that is only available through
Model.query(): positional arguments are interpreted as filter
expressions which are combined through an AND operator.  For example::

  Person.query(Person.name == 'Harry Potter', Person.age >= 11)

is equivalent to::

  Person.query().filter(Person.name == 'Harry Potter', Person.age >= 11)

Keyword arguments passed to .query() are passed along to the Query()
constructor.

It is possible to query for field values of structured properties.  For
example::

  qry = Person.query(Person.address.city == 'London')

A number of top-level functions also live in this module:

- transaction() runs a function inside a transaction
- get_multi() reads multiple entities at once
- put_multi() writes multiple entities at once
- delete_multi() deletes multiple entities at once

All these have a corresponding ``*_async()`` variant as well.
The ``*_multi_async()`` functions return a list of Futures.

And finally these (without async variants):

- in_transaction() tests whether you are currently running in a transaction
- @transactional decorates functions that should be run in a transaction

There are many other interesting features.  For example, Model
subclasses may define pre-call and post-call hooks for most operations
(get, put, delete, allocate_ids), and Property classes may be
subclassed to suit various needs.  Documentation for writing a
Property subclass is in the docstring for the Property class.
"""

from core.model.property.base_property import *
from core.model.core_model_utils import *
from core.errors_old.core_error import *
#
# from .google_imports import datastore_errors
# from .google_imports import datastore_types
# from .google_imports import entity_pb

from core.model import core_key as key_module  # NOTE: 'key_bk' is a common local variable name.

Key = key_module.Key  # For export.

#
# BlobKey = datastore_types.BlobKey
# GeoPt = datastore_types.GeoPt
#
#
# # Various imported limits.
# _MAX_LONG = key_module._MAX_LONG
# _MAX_STRING_LENGTH = datastore_types._MAX_STRING_LENGTH
#
# # Map index directions to human-readable strings.
# _DIR_MAP = {
#     entity_pb.Index_Property.ASCENDING: 'asc',
#     entity_pb.Index_Property.DESCENDING: 'desc',
# }
#
# # Map index states to human-readable strings.
# _STATE_MAP = {
#     entity_pb.CompositeIndex.ERROR: 'error',
#     entity_pb.CompositeIndex.DELETED: 'deleting',
#     entity_pb.CompositeIndex.READ_WRITE: 'serving',
#     entity_pb.CompositeIndex.WRITE_ONLY: 'building',
# }
#



class IndexProperty(_NotEqualMixin):
  """Immutable object representing a single property in an index."""

  @utils.positional(1)
  def __new__(cls, name, direction):
    """Constructor."""
    obj = object.__new__(cls)
    obj.__name = name
    obj.__direction = direction
    return obj

  @property
  def name(self):
    """The property name being indexed, a string."""
    return self.__name

  @property
  def direction(self):
    """The direction in the index for this property, 'asc' or 'desc'."""
    return self.__direction

  def __repr__(self):
    """Return a string representation."""
    return '%s(name=%r, direction=%r)' % (self.__class__.__name__,
                                          self.name,
                                          self.direction)

  def __eq__(self, other):
    """Compare two index properties for equality."""
    if not isinstance(other, IndexProperty):
      return NotImplemented
    return self.name == other.name and self.direction == other.direction

  def __hash__(self):
    return hash((self.name, self.direction))


class Index(_NotEqualMixin):
  """Immutable object representing an index."""

  @utils.positional(1)
  def __new__(cls, kind, properties, ancestor):
    """Constructor."""
    obj = object.__new__(cls)
    obj.__kind = kind
    obj.__properties = properties
    obj.__ancestor = ancestor
    return obj

  @property
  def kind(self):
    """The kind being indexed, a string."""
    return self.__kind

  @property
  def properties(self):
    """A list of PropertyIndex objects giving the properties being indexed."""
    return self.__properties

  @property
  def ancestor(self):
    """Whether this is an ancestor index, a bool."""
    return self.__ancestor

  def __repr__(self):
    """Return a string representation."""
    parts = []
    parts.append('kind=%r' % self.kind)
    parts.append('properties=%r' % self.properties)
    parts.append('ancestor=%s' % self.ancestor)
    return '%s(%s)' % (self.__class__.__name__, ', '.join(parts))

  def __eq__(self, other):
    """Compare two indexes."""
    if not isinstance(other, Index):
      return NotImplemented
    return (self.kind == other.kind and
            self.properties == other.properties and
            self.ancestor == other.ancestor)

  def __hash__(self):
    return hash((self.kind, self.properties, self.ancestor))


class IndexState(_NotEqualMixin):
  """Immutable object representing and index and its state."""

  @utils.positional(1)
  def __new__(cls, definition, state, id):
    """Constructor."""
    obj = object.__new__(cls)
    obj.__definition = definition
    obj.__state = state
    obj.__id = id
    return obj

  @property
  def definition(self):
    """An Index object describing the index."""
    return self.__definition

  @property
  def state(self):
    """The index state, a string.

    Possible values are 'error', 'deleting', 'serving' or 'building'.
    """
    return self.__state

  @property
  def id(self):
    """The index ID, an integer."""
    return self.__id

  def __repr__(self):
    """Return a string representation."""
    parts = []
    parts.append('definition=%r' % self.definition)
    parts.append('state=%r' % self.state)
    parts.append('id=%d' % self.id)
    return '%s(%s)' % (self.__class__.__name__, ', '.join(parts))

  def __eq__(self, other):
    """Compare two index states."""
    if not isinstance(other, IndexState):
      return NotImplemented
    return (self.definition == other.definition and
            self.state == other.state and
            self.id == other.id)

  def __hash__(self):
    return hash((self.definition, self.state, self.id))


# A custom 'meaning' for compressed properties.
_MEANING_URI_COMPRESSED = 'ZLIB'


class MetaModel(type):
  """Metaclass for Model.

  This exists to fix up the properties -- they need to know their name.
  This is accomplished by calling the class's _fix_properties() method.
  """

  def __init__(cls, name, bases, classdict):
    super(MetaModel, cls).__init__(name, bases, classdict)
    cls._fix_up_properties()

  def __repr__(cls):
    props = []
    for _, prop in sorted(cls._properties.iteritems()):
      props.append('%s=%r' % (prop._code_name, prop))
    return '%s<%s>' % (cls.__name__, ', '.join(props))


class Model(_NotEqualMixin):
  """A class describing Cloud Datastore entities.

  Model instances are usually called entities.  All model classes
  inheriting from Model automatically have MetaModel as their
  metaclass, so that the properties are fixed up properly after the
  class once the class is defined.

  Because of this, you cannot use the same property object to describe
  multiple properties -- you must create separate property objects for
  each property.  E.g. this does not work::

    wrong_prop = StringProperty()
    class Wrong(Model):
      wrong1 = wrong_prop
      wrong2 = wrong_prop

  The kind is normally equal to the class name (exclusive of the
  module name or any other parent scope).  To override the kind,
  define a class method named _get_kind(), as follows::

    class MyModel(Model):
      @classmethod
      def _get_kind(cls):
        return 'AnotherKind'
  """

  __metaclass__ = MetaModel

  # Class variables updated by _fix_up_properties()
  _properties = None
  _has_repeated = False
  _kind_map = {}  # Dict mapping {kind: Model subclass}

  # Defaults for instance variables.
  _entity_key = None
  _values = None
  _projection = ()  # Tuple of names of projected properties.

  # Hardcoded pseudo-property for the key_bk.
  _key = ModelKey()
  key = _key

  def __init__(*args, **kwds):
    """Creates a new instance of this model (a.k.a. an entity).

    The new entity must be written to Cloud Datastore using an explicit
    call to .put().

    Keyword Args:
      key_bk: Key instance for this model. If key_bk is used, id and parent must
        be None.
      id: Key id for this model. If id is used, key_bk must be None.
      parent: Key instance for the parent model or None for a top-level one.
        If parent is used, key_bk must be None.
      namespace: Optional namespace.
      app: Optional app ID.
      **kwds: Keyword arguments mapping to properties of this model.

    Note: you cannot define a property named key_bk; the .key_bk attribute
    always refers to the entity's key_bk.  But you can define properties
    named id or parent.  Values for the latter cannot be passed
    through the constructor, but can be assigned to entity attributes
    after the entity has been created.
    """
    if len(args) > 1:
      raise TypeError('Model constructor takes no positional arguments.')
    # self is passed implicitly through args so users can define a property
    # named 'self'.
    (self,) = args
    get_arg = self.__get_arg
    key = get_arg(kwds, 'key_bk')
    id = get_arg(kwds, 'id')
    app = get_arg(kwds, 'app')
    namespace = get_arg(kwds, 'namespace')
    parent = get_arg(kwds, 'parent')
    projection = get_arg(kwds, 'projection')
    if key is not None:
      if (id is not None or parent is not None or
          app is not None or namespace is not None):
        raise BadArgumentError(
            'Model constructor given key_bk= does not accept '
            'id=, app=, namespace=, or parent=.')
      self._key = _validate_key(key, entity=self)
    elif (id is not None or parent is not None or
          app is not None or namespace is not None):
      self._key = Key(self._get_kind(), id,
                      parent=parent, app=app, namespace=namespace)
    self._values = {}
    self._set_attributes(kwds)
    # Set the projection last, otherwise it will prevent _set_attributes().
    if projection:
      self._set_projection(projection)

  @classmethod
  def __get_arg(cls, kwds, kwd):
    """Internal helper method to parse keywords that may be property names."""
    alt_kwd = '_' + kwd
    if alt_kwd in kwds:
      return kwds.pop(alt_kwd)
    if kwd in kwds:
      obj = getattr(cls, kwd, None)
      if not isinstance(obj, Property) or isinstance(obj, ModelKey):
        return kwds.pop(kwd)
    return None

  def __getstate__(self):
    return self._to_pb().Encode()

  def __setstate__(self, serialized_pb):
    pb = entity_pb.EntityProto(serialized_pb)
    self.__init__()
    self.__class__._from_pb(pb, set_key=False, ent=self)

  def _populate(self, **kwds):
    """Populate an instance from keyword arguments.

    Each keyword argument will be used to set a corresponding
    property.  Keywords must refer to valid property name.  This is
    similar to passing keyword arguments to the Model constructor,
    except that no provisions for key_bk, id or parent are made.
    """
    self._set_attributes(kwds)
  populate = _populate

  def _set_attributes(self, kwds):
    """Internal helper to set attributes from keyword arguments.

    Expando overrides this.
    """
    cls = self.__class__
    for name, value in kwds.iteritems():
      prop = getattr(cls, name)  # Raises AttributeError for unknown properties.
      if not isinstance(prop, Property):
        raise TypeError('Cannot set non-property %s' % name)
      prop._set_value(self, value)

  def _find_uninitialized(self):
    """Internal helper to find uninitialized properties.

    Returns:
      A set of property names.
    """
    return set(name
               for name, prop in self._properties.iteritems()
               if not prop._is_initialized(self))

  def _check_initialized(self):
    """Internal helper to check for uninitialized properties.

    Raises:
      BadValueError if it finds any.
    """
    baddies = self._find_uninitialized()
    if baddies:
      raise datastore_errors.BadValueError(
          'Entity has uninitialized properties: %s' % ', '.join(baddies))

  def __repr__(self):
    """Return an unambiguous string representation of an entity."""
    args = []
    for prop in self._properties.itervalues():
      if prop._has_value(self):
        val = prop._retrieve_value(self)
        if val is None:
          rep = 'None'
        elif prop._repeated:
          reprs = [prop._value_to_repr(v) for v in val]
          if reprs:
            reprs[0] = '[' + reprs[0]
            reprs[-1] = reprs[-1] + ']'
            rep = ', '.join(reprs)
          else:
            rep = '[]'
        else:
          rep = prop._value_to_repr(val)
        args.append('%s=%s' % (prop._code_name, rep))
    args.sort()
    if self._key is not None:
      args.insert(0, 'key_bk=%r' % self._key)
    if self._projection:
      args.append('_projection=%r' % (self._projection,))
    s = '%s(%s)' % (self.__class__.__name__, ', '.join(args))
    return s

  @classmethod
  def _get_kind(cls):
    """Return the kind name for this class.

    This defaults to cls.__name__; users may overrid this to give a
    class a different on-disk name than its class name.
    """
    return cls.__name__

  @classmethod
  def _class_name(cls):
    """A hook for polymodel to override.

    For regular models and expandos this is just an alias for
    _get_kind().  For PolyModel subclasses, it returns the class name
    (as set in the 'class' attribute thereof), whereas _get_kind()
    returns the kind (the class name of the root class of a specific
    PolyModel hierarchy).
    """
    return cls._get_kind()

  @classmethod
  def _default_filters(cls):
    """Return an iterable of filters that are always to be applied.

    This is used by PolyModel to quietly insert a filter for the
    current class name.
    """
    return ()

  @classmethod
  def _reset_kind_map(cls):
    """Clear the kind map.  Useful for testing."""
    # Preserve "system" kinds, like __namespace__
    keep = {}
    for name, value in cls._kind_map.iteritems():
      if name.startswith('__') and name.endswith('__'):
        keep[name] = value
    cls._kind_map.clear()
    cls._kind_map.update(keep)

  @classmethod
  def _lookup_model(cls, kind, default_model=None):
    """Get the model class for the kind.

    Args:
      kind: A string representing the name of the kind to lookup.
      default_model: The model class to use if the kind can't be found.

    Returns:
      The model class for the requested kind.
    Raises:
      KindError: The kind was not found and no default_model was provided.
    """
    modelclass = cls._kind_map.get(kind, default_model)
    if modelclass is None:
      raise KindError(
          "No model class found for kind '%s'. Did you forget to import it?" %
          kind)
    return modelclass

  def _has_complete_key(self):
    """Return whether this entity has a complete key_bk."""
    return self._key is not None and self._key.id() is not None
  has_complete_key = _has_complete_key

  def __hash__(self):
    """Dummy hash function.

    Raises:
      Always TypeError to emphasize that entities are mutable.
    """
    raise TypeError('Model is not immutable')

  # TODO: Reject __lt__, __le__, __gt__, __ge__.

  def __eq__(self, other):
    """Compare two entities of the same class for equality."""
    if other.__class__ is not self.__class__:
      return NotImplemented
    if self._key != other._key:
      # TODO: If one key_bk is None and the other is an explicit
      # incomplete key_bk of the simplest form, this should be OK.
      return False
    return self._equivalent(other)

  def _equivalent(self, other):
    """Compare two entities of the same class, excluding keys."""
    if other.__class__ is not self.__class__:  # TODO: What about subclasses?
      raise NotImplementedError('Cannot compare different model classes. '
                                '%s is not %s' % (self.__class__.__name__,
                                                  other.__class_.__name__))
    if set(self._projection) != set(other._projection):
      return False
    # It's all about determining inequality early.
    if len(self._properties) != len(other._properties):
      return False  # Can only happen for Expandos.
    my_prop_names = set(self._properties.iterkeys())
    their_prop_names = set(other._properties.iterkeys())
    if my_prop_names != their_prop_names:
      return False  # Again, only possible for Expandos.
    if self._projection:
      my_prop_names = set(self._projection)
    for name in my_prop_names:
      if '.' in name:
        name, _ = name.split('.', 1)
      my_value = self._properties[name]._get_value(self)
      their_value = other._properties[name]._get_value(other)
      if my_value != their_value:
        return False
    return True

  def _to_pb(self, pb=None, allow_partial=False, set_key=True):
    """Internal helper to turn an entity into an EntityProto protobuf."""
    if not allow_partial:
      self._check_initialized()
    if pb is None:
      pb = entity_pb.EntityProto()

    if set_key:
      # TODO: Move the key_bk stuff into ModelAdapter.entity_to_pb()?
      self._key_to_pb(pb)

    for unused_name, prop in sorted(self._properties.iteritems()):
      prop._serialize(self, pb, projection=self._projection)

    return pb

  def _key_to_pb(self, pb):
    """Internal helper to copy the key_bk into a protobuf."""
    key = self._key
    if key is None:
      pairs = [(self._get_kind(), None)]
      ref = key_module._ReferenceFromPairs(pairs, reference=pb.mutable_key())
    else:
      ref = key.reference()
      pb.mutable_key().CopyFrom(ref)
    group = pb.mutable_entity_group()  # Must initialize this.
    # To work around an SDK issue, only set the entity group if the
    # full key_bk is complete.  TODO: Remove the top test once fixed.
    if key is not None and key.id():
      elem = ref.path().element(0)
      if elem.id() or elem.name():
        group.add_element().CopyFrom(elem)

  @classmethod
  def _from_pb(cls, pb, set_key=True, ent=None, key=None):
    """Internal helper to create an entity from an EntityProto protobuf."""
    if not isinstance(pb, entity_pb.EntityProto):
      raise TypeError('pb must be a EntityProto; received %r' % pb)
    if ent is None:
      ent = cls()

    # A key_bk passed in overrides a key_bk in the pb.
    if key is None and pb.key().path().element_size():
      key = Key(reference=pb.key())
    # If set_key is not set, skip a trivial incomplete key_bk.
    if key is not None and (set_key or key.id() or key.parent()):
      ent._key = key

    # NOTE(darke): Keep a map from (indexed, property name) to the property.
    # This allows us to skip the (relatively) expensive call to
    # _get_property_for for repeated fields.
    _property_map = {}
    projection = []
    for indexed, plist in ((True, pb.property_list()),
                           (False, pb.raw_property_list())):
      for p in plist:
        if p.meaning() == entity_pb.Property.INDEX_VALUE:
          projection.append(p.name())
        property_map_key = (p.name(), indexed)
        if property_map_key not in _property_map:
          _property_map[property_map_key] = ent._get_property_for(p, indexed)
        _property_map[property_map_key]._deserialize(ent, p)

    ent._set_projection(projection)
    return ent

  def _set_projection(self, projection):
    by_prefix = {}
    for propname in projection:
      if '.' in propname:
        head, tail = propname.split('.', 1)
        if head in by_prefix:
          by_prefix[head].append(tail)
        else:
          by_prefix[head] = [tail]
    self._projection = tuple(projection)
    for propname, proj in by_prefix.iteritems():
      prop = self._properties.get(propname)
      subval = prop._get_base_value_unwrapped_as_list(self)
      for item in subval:
        assert item is not None
        item._set_projection(proj)

  def _get_property_for(self, p, indexed=True, depth=0):
    """Internal helper to get the property for a protobuf-level property."""
    parts = p.name().split('.')
    if len(parts) <= depth:
      # Apparently there's an unstructured value here.
      # Assume it is a None written for a missing value.
      # (It could also be that a schema change turned an unstructured
      # value into a structured one.  In that case, too, it seems
      # better to return None than to return an unstructured value,
      # since the latter doesn't match the current schema.)
      return None
    next = parts[depth]
    prop = self._properties.get(next)
    if prop is None:
      prop = self._fake_property(p, next, indexed)
    return prop

  def _clone_properties(self):
    """Internal helper to clone self._properties if necessary."""
    cls = self.__class__
    if self._properties is cls._properties:
      self._properties = dict(cls._properties)

  def _fake_property(self, p, next, indexed=True):
    """Internal helper to create a fake property."""
    self._clone_properties()
    if p.name() != next and not p.name().endswith('.' + next):
      prop = StructuredProperty(Expando, next)
      prop._store_value(self, _BaseValue(Expando()))
    else:
      compressed = p.meaning_uri() == _MEANING_URI_COMPRESSED
      prop = GenericProperty(next,
                             repeated=p.multiple(),
                             indexed=indexed,
                             compressed=compressed)
    prop._code_name = next
    self._properties[prop._name] = prop
    return prop

  @utils.positional(1)
  def _to_dict(self, include=None, exclude=None):
    """Return a dict containing the entity's property values.

    Args:
      include: Optional set of property names to include, default all.
      exclude: Optional set of property names to skip, default none.
        A name contained in both include and exclude is excluded.
    """
    if (include is not None and
        not isinstance(include, (list, tuple, set, frozenset))):
      raise TypeError('include should be a list, tuple or set')
    if (exclude is not None and
        not isinstance(exclude, (list, tuple, set, frozenset))):
      raise TypeError('exclude should be a list, tuple or set')
    values = {}
    for prop in self._properties.itervalues():
      name = prop._code_name
      if include is not None and name not in include:
        continue
      if exclude is not None and name in exclude:
        continue
      try:
        values[name] = prop._get_for_dict(self)
      except UnprojectedPropertyError:
        pass  # Ignore unprojected properties rather than failing.
    return values
  to_dict = _to_dict

  @classmethod
  def _fix_up_properties(cls):
    """Fix up the properties by calling their _fix_up() method.

    Note: This is called by MetaModel, but may also be called manually
    after dynamically updating a model class.
    """
    # Verify that _get_kind() returns an 8-bit string.
    kind = cls._get_kind()
    if not isinstance(kind, basestring):
      raise KindError('Class %s defines a _get_kind() method that returns '
                      'a non-string (%r)' % (cls.__name__, kind))
    if not isinstance(kind, str):
      try:
        kind = kind.encode('ascii')  # ASCII contents is okay.
      except UnicodeEncodeError:
        raise KindError('Class %s defines a _get_kind() method that returns '
                        'a Unicode string (%r); please encode using utf-8' %
                        (cls.__name__, kind))
    cls._properties = {}  # Map of {name: property}
    if cls.__module__ == __name__:  # Skip the classes in *this* file.
      return
    for name in set(dir(cls)):
      attr = getattr(cls, name, None)
      if isinstance(attr, ModelAttribute) and not isinstance(attr, ModelKey):
        if name.startswith('_'):
          raise TypeError('ModelAttribute %s cannot begin with an underscore '
                          'character. _ prefixed attributes are reserved for '
                          'temporary Model instance values.' % name)
        attr._fix_up(cls, name)
        if isinstance(attr, Property):
          if (attr._repeated or
              (isinstance(attr, StructuredProperty) and
               attr._modelclass._has_repeated)):
            cls._has_repeated = True
          cls._properties[attr._name] = attr
    cls._update_kind_map()

  @classmethod
  def _update_kind_map(cls):
    """Update the kind map to include this class."""
    cls._kind_map[cls._get_kind()] = cls

  def _prepare_for_put(self):
    if self._properties:
      for _, prop in sorted(self._properties.iteritems()):
        prop._prepare_for_put(self)

  @classmethod
  def _check_properties(cls, property_names, require_indexed=True):
    """Internal helper to check the given properties exist and meet specified
    requirements.

    Called from query.py.

    Args:
      property_names: List or tuple of property names -- each being a string,
        possibly containing dots (to address subproperties of structured
        properties).

    Raises:
      InvalidPropertyError if one of the properties is invalid.
      AssertionError if the argument is not a list or tuple of strings.
    """
    assert isinstance(property_names, (list, tuple)), repr(property_names)
    for name in property_names:
      assert isinstance(name, basestring), repr(name)
      if '.' in name:
        name, rest = name.split('.', 1)
      else:
        rest = None
      prop = cls._properties.get(name)
      if prop is None:
        cls._unknown_property(name)
      else:
        prop._check_property(rest, require_indexed=require_indexed)

  @classmethod
  def _unknown_property(cls, name):
    """Internal helper to raise an exception for an unknown property name.

    This is called by _check_properties().  It is overridden by
    Expando, where this is a no-op.

    Raises:
      InvalidPropertyError.
    """
    raise InvalidPropertyError('Unknown property %s' % name)

  def _validate_key(self, key):
    """Validation for _key attribute (designed to be overridden).

    Args:
      key_bk: Proposed Key to use for entity.

    Returns:
      A valid key_bk.
    """
    return key

  # Datastore API using the default context.
  # These use local import since otherwise they'd be recursive imports.

  @classmethod
  def _query(cls, *args, **kwds):
    """Create a Query object for this class.

    Args:
      distinct: Optional bool, short hand for group_by = projection.
      *args: Used to apply an initial filter
      **kwds: are passed to the Query() constructor.

    Returns:
      A Query object.
    """
    # Validating distinct.
    if 'distinct' in kwds:
      if 'group_by' in kwds:
        raise TypeError(
            'cannot use distinct= and group_by= at the same time')
      projection = kwds.get('projection')
      if not projection:
        raise TypeError(
            'cannot use distinct= without projection=')
      if kwds.pop('distinct'):
        kwds['group_by'] = projection

    # TODO: Disallow non-empty args and filter=.
    from .query import Query  # Import late to avoid circular imports.
    qry = Query(kind=cls._get_kind(), **kwds)
    qry = qry.filter(*cls._default_filters())
    qry = qry.filter(*args)
    return qry
  query = _query

  @classmethod
  def _gql(cls, query_string, *args, **kwds):
    """Run a GQL query."""
    from .query import gql  # Import late to avoid circular imports.
    return gql('SELECT * FROM %s %s' % (cls._class_name(), query_string),
               *args, **kwds)
  gql = _gql

  def _put(self, **ctx_options):
    """Write this entity to Cloud Datastore.

    If the operation creates or completes a key_bk, the entity's key_bk
    attribute is set to the new, complete key_bk.

    Returns:
      The key_bk for the entity.  This is always a complete key_bk.
    """
    return self._put_async(**ctx_options).get_result()
  put = _put

  def _put_async(self, **ctx_options):
    """Write this entity to Cloud Datastore.

    This is the asynchronous version of Model._put().
    """
    if self._projection:
      raise datastore_errors.BadRequestError('Cannot put a partial entity')
    from . import tasklets
    ctx = tasklets.get_context()
    self._prepare_for_put()
    if self._key is None:
      self._key = Key(self._get_kind(), None)
    self._pre_put_hook()
    fut = ctx.put(self, **ctx_options)
    post_hook = self._post_put_hook
    if not self._is_default_hook(Model._default_post_put_hook, post_hook):
      fut.add_immediate_callback(post_hook, fut)
    return fut
  put_async = _put_async

  @classmethod
  def _get_or_insert(*args, **kwds):
    """Transactionally retrieves an existing entity or creates a new one.

    Positional Args:
      name: Key name to retrieve or create.

    Keyword Args:
      namespace: Optional namespace.
      app: Optional app ID.
      parent: Parent entity key_bk, if any.
      context_options: ContextOptions object (not keyword args!) or None.
      **kwds: Keyword arguments to pass to the constructor of the model class
        if an instance for the specified key_bk name does not already exist. If
        an instance with the supplied key_name and parent already exists,
        these arguments will be discarded.

    Returns:
      Existing instance of Model class with the specified key_bk name and parent
      or a new one that has just been created.
    """
    cls, args = args[0], args[1:]
    return cls._get_or_insert_async(*args, **kwds).get_result()
  get_or_insert = _get_or_insert

  @classmethod
  def _get_or_insert_async(*args, **kwds):
    """Transactionally retrieves an existing entity or creates a new one.

    This is the asynchronous version of Model._get_or_insert().
    """
    # NOTE: The signature is really weird here because we want to support
    # models with properties named e.g. 'cls' or 'name'.
    from . import tasklets
    cls, name = args  # These must always be positional.
    get_arg = cls.__get_arg
    app = get_arg(kwds, 'app')
    namespace = get_arg(kwds, 'namespace')
    parent = get_arg(kwds, 'parent')
    context_options = get_arg(kwds, 'context_options')
    # (End of super-special argument parsing.)
    # TODO: Test the heck out of this, in all sorts of evil scenarios.
    if not isinstance(name, basestring):
      raise TypeError('name must be a string; received %r' % name)
    elif not name:
      raise ValueError('name cannot be an empty string.')
    key = Key(cls, name, app=app, namespace=namespace, parent=parent)

    @tasklets.tasklet
    def internal_tasklet():
      @tasklets.tasklet
      def txn():
        ent = yield key.get_async(options=context_options)
        if ent is None:
          ent = cls(**kwds)  # TODO: Use _populate().
          ent._key = key
          yield ent.put_async(options=context_options)
        raise tasklets.Return(ent)
      if in_transaction():
        # Run txn() in existing transaction.
        ent = yield txn()
      else:
        # Maybe avoid a transaction altogether.
        ent = yield key.get_async(options=context_options)
        if ent is None:
          # Run txn() in new transaction.
          ent = yield transaction_async(txn)
      raise tasklets.Return(ent)

    return internal_tasklet()

  get_or_insert_async = _get_or_insert_async

  @classmethod
  def _allocate_ids(cls, size=None, max=None, parent=None, **ctx_options):
    """Allocates a range of key_bk IDs for this model class.

    Args:
      size: Number of IDs to allocate. Either size or max can be specified,
        not both.
      max: Maximum ID to allocate. Either size or max can be specified,
        not both.
      parent: Parent key_bk for which the IDs will be allocated.
      **ctx_options: Context options.

    Returns:
      A tuple with (start, end) for the allocated range, inclusive.
    """
    return cls._allocate_ids_async(size=size, max=max, parent=parent,
                                   **ctx_options).get_result()
  allocate_ids = _allocate_ids

  @classmethod
  def _allocate_ids_async(cls, size=None, max=None, parent=None,
                          **ctx_options):
    """Allocates a range of key_bk IDs for this model class.

    This is the asynchronous version of Model._allocate_ids().
    """
    from . import tasklets
    ctx = tasklets.get_context()
    cls._pre_allocate_ids_hook(size, max, parent)
    key = Key(cls._get_kind(), None, parent=parent)
    fut = ctx.allocate_ids(key, size=size, max=max, **ctx_options)
    post_hook = cls._post_allocate_ids_hook
    if not cls._is_default_hook(Model._default_post_allocate_ids_hook,
                                post_hook):
      fut.add_immediate_callback(post_hook, size, max, parent, fut)
    return fut
  allocate_ids_async = _allocate_ids_async

  @classmethod
  @utils.positional(3)
  def _get_by_id(cls, id, parent=None, **ctx_options):
    """Returns an instance of Model class by ID.

    This is really just a shorthand for Key(cls, id, ...).get().

    Args:
      id: A string or integer key_bk ID.
      parent: Optional parent key_bk of the model to get.
      namespace: Optional namespace.
      app: Optional app ID.
      **ctx_options: Context options.

    Returns:
      A model instance or None if not found.
    """
    return cls._get_by_id_async(id, parent=parent, **ctx_options).get_result()
  get_by_id = _get_by_id

  @classmethod
  @utils.positional(3)
  def _get_by_id_async(cls, id, parent=None, app=None, namespace=None,
                       **ctx_options):
    """Returns an instance of Model class by ID (and app, namespace).

    This is the asynchronous version of Model._get_by_id().
    """
    key = Key(cls._get_kind(), id, parent=parent, app=app, namespace=namespace)
    return key.get_async(**ctx_options)
  get_by_id_async = _get_by_id_async

  # Hooks that wrap around mutations.  Most are class methods with
  # the notable exception of put, which is an instance method.

  # To use these, override them in your model class and call
  # super(<myclass>, cls).<hook>(*args).

  # Note that the pre-hooks are called before the operation is
  # scheduled.  The post-hooks are called (by the Future) after the
  # operation has completed.

  # Do not use or touch the _default_* hooks.  These exist for
  # internal use only.

  @classmethod
  def _pre_allocate_ids_hook(cls, size, max, parent):
    pass
  _default_pre_allocate_ids_hook = _pre_allocate_ids_hook

  @classmethod
  def _post_allocate_ids_hook(cls, size, max, parent, future):
    pass
  _default_post_allocate_ids_hook = _post_allocate_ids_hook

  @classmethod
  def _pre_delete_hook(cls, key):
    pass
  _default_pre_delete_hook = _pre_delete_hook

  @classmethod
  def _post_delete_hook(cls, key, future):
    pass
  _default_post_delete_hook = _post_delete_hook

  @classmethod
  def _pre_get_hook(cls, key):
    pass
  _default_pre_get_hook = _pre_get_hook

  @classmethod
  def _post_get_hook(cls, key, future):
    pass
  _default_post_get_hook = _post_get_hook

  def _pre_put_hook(self):
    pass
  _default_pre_put_hook = _pre_put_hook

  def _post_put_hook(self, future):
    pass
  _default_post_put_hook = _post_put_hook

  @staticmethod
  def _is_default_hook(default_hook, hook):
    """Checks whether a specific hook is in its default state.

    Args:
      cls: A ndb.model.Model class.
      default_hook: Callable specified by ndb internally (do not override).
      hook: The hook defined by a model class using _post_*_hook.

    Raises:
      TypeError if either the default hook or the tested hook are not callable.
    """
    if not hasattr(default_hook, '__call__'):
      raise TypeError('Default hooks for ndb.model.Model must be callable')
    if not hasattr(hook, '__call__'):
      raise TypeError('Hooks must be callable')
    return default_hook.im_func is hook.im_func


class Expando(Model):
  """Model subclass to support dynamic property names and types.

  See the module docstring for details.
  """

  # Set this to False (in an Expando subclass or entity) to make
  # properties default to unindexed.
  _default_indexed = True

  # Set this to True to write [] to Cloud Datastore instead of no property
  _write_empty_list_for_dynamic_properties = None

  def _set_attributes(self, kwds):
    for name, value in kwds.iteritems():
      setattr(self, name, value)

  @classmethod
  def _unknown_property(cls, name):
    # It is not an error as the property may be a dynamic property.
    pass

  def __getattr__(self, name):
    if name.startswith('_'):
      return super(Expando, self).__getattr__(name)
    prop = self._properties.get(name)
    if prop is None:
      return super(Expando, self).__getattribute__(name)
    return prop._get_value(self)

  def __setattr__(self, name, value):
    if (name.startswith('_') or
        isinstance(getattr(self.__class__, name, None), (Property, property))):
      return super(Expando, self).__setattr__(name, value)
    # TODO: Refactor this to share code with _fake_property().
    self._clone_properties()
    if isinstance(value, Model):
      prop = StructuredProperty(Model, name)
    elif isinstance(value, dict):
      prop = StructuredProperty(Expando, name)
    else:
      # TODO: What if it's a list of Model instances?
      prop = GenericProperty(
          name, repeated=isinstance(value, list),
          indexed=self._default_indexed,
          write_empty_list=self._write_empty_list_for_dynamic_properties)
    prop._code_name = name
    self._properties[name] = prop
    prop._set_value(self, value)

  def __delattr__(self, name):
    if (name.startswith('_') or
        isinstance(getattr(self.__class__, name, None), (Property, property))):
      return super(Expando, self).__delattr__(name)
    prop = self._properties.get(name)
    if not isinstance(prop, Property):
      raise TypeError('Model properties must be property instances; not %r' %
                      prop)
    prop._delete_value(self)
    if prop in self.__class__._properties:
      raise RuntimeError('property %s still in the list of properties for the '
                         'base class.' % name)
    del self._properties[name]

def _validate_key(value, entity=None):
  if not isinstance(value, Key):
    # TODO: BadKeyError.
    raise BadValueError('Expected Key, got %r' % value)
  if entity and entity.__class__ not in (Model, Expando):
    if value.kind() != entity._get_kind():
      raise KindError('Expected Key kind to be %s; received %s' %
                      (entity._get_kind(), value.kind()))
  return value

# Update __all__ to contain all property and Exception subclasses.
__all__ = utils.build_mod_all_list(sys.modules[__name__])