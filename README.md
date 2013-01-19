`ds-debug` is a debugging tool that lets you send data structures to a python interpreter, as an alternative to printing and examining it by eye.

## Usage

(Subject to change at any time.)

Put `ds_debug.py` in your `sys.path`.

Run the program `ds-debug`. This puts you in a python interpreter with a server running in the background.

Now in a seperate process, import `ds_debug` and call its `debug` function with keyword arguments `name=data`. For example:

```python
>>> import ds_debug as ds
>>> ds.debug(foo=13, bar=['hello'], baz=dict(x=12, y=[]))
```

Return to the `ds-debug` process, and these variables will be available through the object `v`.

```python
>>> v.foo
13
>>> v.bar
[u'hello']
>>> v.baz
storage(y=[], x=12)
>>> v.baz.y
[]
```

(`dict`s get turned into `storage` objects. These inherit from `dict`, but attribute lookup falls back to item lookup: `v.baz.y` becomes `v.baz['y']`. Attributes that actually exist on `dict` do not get overridden: `s.keys()` is a method call, regardless of whether `s['keys']` exists. `v` is also a `storage`.)

If you call `debug` again with some of the same variable names, the old values will be overwritten, but a history will be kept in object `h` (another `storage`):

```python
# Client process
>>> ds.debug(bar=13, baz=['hello'], quux=dict(x=12, y=[]))

# Server process
>>> (v.foo, v.bar, v.baz, v.quux)
(13, 13, [u'hello'], storage(y=[], x=12))
>>> (h.foo, h.bar, h.baz, h.quux)
([13], [[u'hello'], 13], [storage(y=[], x=12), [u'hello']], [storage(y=[], x=12)])
```

## Bugs

* Only JSON-serialisable objects can currently be sent.

* There's no graceful failure handling.

* Only one server thread runs at a time. If two processes are trying to debug at once, they'll step on each other's toes.


## Architecture

(Subject to change at any time.)

The server is a `ReaderThread` instance, which listens for connections on port 7575. It accepts data in the form

    length
    json

where `length` is an integer up to 19 decimal digits long, and `json` is a JSON string of `length` bytes, encoding a dict. The dict should have keys `name` and `val`, and other keys are ignored.

The client simply connects to this, and sends one packet of data for each `name=val` pair it was passed. Clients for other languages would be easy to write.

For that matter, it would be easy to write another server, if you want to examine your data with something other than python.
