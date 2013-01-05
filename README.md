`ds-debug` is a debugging tool that lets you send data to a python interpreter, as an alternative to printing and examining it by eye.

## Usage

(Subject to change at any time.)

Put `ds_debug.py` in your `sys.path`.

Run the program `ds-debug`. This puts you in a python interpreter with a server running in the background.

Now in a seperate process, import `ds_debug` and call its `debug` function with keyword arguments `name=data`. For example:

```python
>>> import ds_debug as ds
>>> ds.debug(foo=13, bar=['hello'], baz=dict(x=12, y=[]))
```

Return to the `ds-debug` process, and these variables will be available as properties of the object `v`.

```python
>>> v.foo
13
>>> v.bar
[u'hello']
>>> v.baz
{u'y': [], u'x': 12}
```

If you call `debug` again with some of the same variable names, the old values will be overwritten, but a history will be kept in object `h`:

```python
# Client process
>>> ds.debug(bar=13, baz=['hello'], quux=dict(x=12, y=[]))

# Server process
>>> (v.foo, v.bar, v.baz, v.quux)
(13, 13, [u'hello'], {u'y': [], u'x': 12})
>>> (h.foo, h.bar, h.baz, h.quux)
([13], [[u'hello'], 13], [{u'y': [], u'x': 12}, [u'hello']], [{u'y': [], u'x': 12}])
```

## Bugs

* Only JSON-serialisable objects can currently be sent.

* There's no graceful failure handling. E.g. if the server isn't running when you call `debug`, it throws an exception.

* Only one server thread runs at a time. If two processes are trying to debug at once, they'll step on each other's toes.


## Architecture

(Subject to change at any time.)

The server is a `ReaderThread` instance, which listens for connections on port 7575. It accepts data in the form

    length
    json

where `length` is an integer up to 19 decimal digits long, and `json` is a JSON string of `length` bytes, encoding a dict. The dict should have keys `name` and `val`, and other keys are ignored.

The client simply connects to this, sends one packet of data for each `name=val` pair it was passed. Clients for other languages would be easy to write.
