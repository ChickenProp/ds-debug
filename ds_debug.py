import threading
from socket import *
import json

class Struct(object):
    pass

values = Struct()
values._hist = Struct()

status = ""

class ReaderThread(threading.Thread):
    def __init__(self):
        super(ReaderThread, self).__init__()
        self.daemon = True

    def run(self):
        global value, status

        status = "Initialising"

        sock = socket(AF_INET)

        # Without this, we have to wait to restart if we closed incorrectly.
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        sock.bind((gethostname(), 7575))
        sock.listen(1)

        while True:
            status = "Waiting for connection"
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

                js = json.loads(json_str)
                name = js['name']
                val = js['val']

                setattr(values, name, val)

                if not hasattr(values._hist, name):
                    setattr(values._hist, name, [val])
                else:
                    getattr(values._hist, name).append(val)


def debug(**kw):
    sock = socket(AF_INET)
    sock.connect((gethostname(), 7575))
    for name, val in kw.iteritems():
        json_str = json.dumps(dict(name=name, val=val))
        sock.send("%d\n%s" % (len(json_str), json_str))
    sock.close()
