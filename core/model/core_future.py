"""Currently unusable classes/methods related to core.model."""

class ModelAdapter(datastore_rpc.AbstractAdapter):
  """Conversions between 'our' Key and Model classes and protobufs.

  This is needed to construct a Connection object, which in turn is
  needed to construct a Context object.

  See the base class docstring for more info about the signatures.
  """

  def __init__(self, default_model=None, id_resolver=None):
    """Constructor.

    Args:
      default_model: If an implementation for the kind cannot be found, use
        this model class.  If none is specified, an exception will be thrown
        (default).
      id_resolver: A datastore_pbs.IdResolver that can resolve
        application ids. This is only necessary when running on the Cloud
        Datastore v1 API.
    """
    # TODO(pcostello): Remove this once AbstractAdapter's constructor makes
    # it into production.
    try:
      super(ModelAdapter, self).__init__(id_resolver)
    except:
      pass
    self.default_model = default_model
    self.want_pbs = 0

  # Make this a context manager to request setting _orig_pb.
  # Used in query.py by _MultiQuery.run_to_queue().

  def __enter__(self):
    self.want_pbs += 1

  def __exit__(self, *unused_args):
    self.want_pbs -= 1

  def pb_to_key(self, pb):
    return Key(reference=pb)

  def key_to_pb(self, key):
    return key.reference()

  def pb_to_entity(self, pb):
    key = None
    kind = None
    if pb.key().path().element_size():
      key = Key(reference=pb.key())
      kind = key.kind()
    modelclass = Model._lookup_model(kind, self.default_model)
    entity = modelclass._from_pb(pb, key=key, set_key=False)
    if self.want_pbs:
      entity._orig_pb = pb
    return entity

  def entity_to_pb(self, ent):
    pb = ent._to_pb()
    return pb

  def pb_to_index(self, pb):
    index_def = pb.definition()
    properties = [IndexProperty(name=prop.name(),
                                direction=_DIR_MAP[prop.direction()])
                  for prop in index_def.property_list()]
    index = Index(kind=index_def.entity_type(),
                  properties=properties,
                  ancestor=bool(index_def.ancestor()),
                 )
    index_state = IndexState(definition=index,
                             state=_STATE_MAP[pb.state()],
                             id=pb.id(),
                            )
    return index_state


def make_connection(config=None, default_model=None,
                    _api_version=datastore_rpc._DATASTORE_V3,
                    _id_resolver=None):
  """Create a new Connection object with the right adapter.

  Optionally you can pass in a datastore_rpc.Configuration object.
  """
  return datastore_rpc.Connection(
      adapter=ModelAdapter(default_model, id_resolver=_id_resolver),
      config=config,
      _api_version=_api_version)

