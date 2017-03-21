
@utils.positional(1)
def transaction(callback, **ctx_options):
  """Run a callback in a transaction.

  Args:
    callback: A function or tasklet to be called.
    **ctx_options: Transaction options.

  Useful options include:
    retries=N: Retry up to N times (i.e. try up to N+1 times)
    propagation=<flag>: Determines how an existing transaction should be
      propagated, where <flag> can be one of the following:
      TransactionOptions.NESTED: Start a nested transaction (this is the
        default; but actual nested transactions are not yet implemented,
        so effectively you can only use this outside an existing transaction).
      TransactionOptions.MANDATORY: A transaction must already be in progress.
      TransactionOptions.ALLOWED: If a transaction is in progress, join it.
      TransactionOptions.INDEPENDENT: Always start a new parallel transaction.
    xg=True: On the High Replication Datastore, enable cross-group
      transactions, i.e. allow writing to up to 5 entity groups.

  WARNING: Using anything other than NESTED for the propagation flag
  can have strange consequences.  When using ALLOWED or MANDATORY, if
  an exception is raised, the transaction is likely not safe to
  commit.  When using INDEPENDENT it is not generally safe to return
  values read to the caller (as they were not read in the caller's
  transaction).

  Returns:
    Whatever callback() returns.

  Raises:
    Whatever callback() raises; datastore_errors.TransactionFailedError
    if the transaction failed.

  Note:
    To pass arguments to a callback function, use a lambda, e.g.
      def my_callback(key, inc):
        ...
      transaction(lambda: my_callback(Key(...), 1))
  """
  fut = transaction_async(callback, **ctx_options)
  return fut.get_result()


@utils.positional(1)
def transaction_async(callback, **ctx_options):
  """Run a callback in a transaction.

  This is the asynchronous version of transaction().
  """
  from . import tasklets
  return tasklets.get_context().transaction(callback, **ctx_options)


def in_transaction():
  """Return whether a transaction is currently active."""
  from . import tasklets
  return tasklets.get_context().in_transaction()


@utils.decorator
def transactional(func, args, kwds, **options):
  """Decorator to make a function automatically run in a transaction.

  Args:
    **ctx_options: Transaction options (see transaction(), but propagation
      default to TransactionOptions.ALLOWED).

  This supports two forms:

  (1) Vanilla:
      @transactional
      def callback(arg):
        ...

  (2) With options:
      @transactional(retries=1)
      def callback(arg):
        ...
  """
  return transactional_async.wrapped_decorator(
      func, args, kwds, **options).get_result()


@utils.decorator
def transactional_async(func, args, kwds, **options):
  """The async version of @ndb.transaction."""
  options.setdefault('propagation', datastore_rpc.TransactionOptions.ALLOWED)
  if args or kwds:
    return transaction_async(lambda: func(*args, **kwds), **options)
  return transaction_async(func, **options)


@utils.decorator
def transactional_tasklet(func, args, kwds, **options):
  """The async version of @ndb.transaction.

  Will return the result of the wrapped function as a Future.
  """
  from . import tasklets
  func = tasklets.tasklet(func)
  return transactional_async.wrapped_decorator(func, args, kwds, **options)


@utils.decorator
def non_transactional(func, args, kwds, allow_existing=True):
  """A decorator that ensures a function is run outside a transaction.

  If there is an existing transaction (and allow_existing=True), the
  existing transaction is paused while the function is executed.

  Args:
    allow_existing: If false, throw an exception if called from within
      a transaction.  If true, temporarily re-establish the
      previous non-transactional context.  Defaults to True.

  This supports two forms, similar to transactional().

  Returns:
    A wrapper for the decorated function that ensures it runs outside a
    transaction.
  """
  from . import tasklets
  ctx = tasklets.get_context()
  if not ctx.in_transaction():
    return func(*args, **kwds)
  if not allow_existing:
    raise datastore_errors.BadRequestError(
        '%s cannot be called within a transaction.' % func.__name__)
  save_ctx = ctx
  while ctx.in_transaction():
    ctx = ctx._parent_context
    if ctx is None:
      raise datastore_errors.BadRequestError(
          'Context without non-transactional ancestor')
  save_ds_conn = datastore._GetConnection()
  try:
    if hasattr(save_ctx, '_old_ds_conn'):
      datastore._SetConnection(save_ctx._old_ds_conn)
    tasklets.set_context(ctx)
    return func(*args, **kwds)
  finally:
    tasklets.set_context(save_ctx)
    datastore._SetConnection(save_ds_conn)
