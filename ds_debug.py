import threading
from socket import *
import json

# This is web.py's storage, except with an easier-to-read __repr__.
# Note that dict methods shadow element lookup, so e.g. when x=storage(keys=1),
# we have x.keys() == ['keys'] rather than x.keys == 1.
class storage(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k

    def __repr__(self):
        kvs = [ k + '=' + repr(v) for k,v in dict(self).iteritems() ]
        return 'storage(%s)' % ", ".join(kvs)

class ReaderThread(threading.Thread):
    def __init__(self):
        super(ReaderThread, self).__init__()
        self.daemon = True

        self.values = storage()
        self.hist = storage()
        self.status = "Uninitialised"

    def run(self):
        self.status = "Initialising"

        sock = socket(AF_INET)

        # Without this, we have to wait to restart if we closed incorrectly.
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        sock.bind((gethostname(), 7575))
        sock.listen(1)

        while True:
            self.status = "Waiting for connection"
            (sock2, address) = sock.accept()

            while True:
                status = "Waiting for header"

                # If we read too many bytes here, our first read might collect
                # the entire JSON string and the following header, if they're
                # sent in quick enough succession. The somewhat hacky solution
                # is that the JSON won't fit in 20 bytes (at least with the
                # current schema), and 10^19 - 1 is more than long enough for
                # any sane purposes (it's almost 2^64).
                header = sock2.recv(20)

                if len(header) == 0:
                    break

                json_len, init_chunk = header.split("\n", 1)
                json_len = int(json_len)

                status = "Waiting for %d bytes of JSON" % (json_len)
                remaining = json_len - len(init_chunk)
                json_str = init_chunk + sock2.recv(remaining, MSG_WAITALL)

                js = json.loads(json_str, object_hook=lambda d: storage(**d))
                name = js.name
                val = js.val

                self.values[name] = val

                if name not in self.hist:
                    self.hist[name] = [val]
                else:
                    self.hist[name].append(val)


def debug(**kw):
    sock = socket(AF_INET)
    try:
        sock.connect((gethostname(), 7575))
        for name, val in kw.iteritems():
            json_str = json.dumps(dict(name=name, val=val))
            sock.send("%d\n%s" % (len(json_str), json_str))
        sock.close()
    except:
        pass
