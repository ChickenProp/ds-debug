import threading
from socket import *
import json

value = None

class ReaderThread(threading.Thread):
    def __init__(self):
        super(ReaderThread, self).__init__()
        self.daemon = True

    def run(self):
        global value

        sock = socket(AF_INET)

        # Without this, we have to wait to restart if we closed incorrectly.
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        sock.bind((gethostname(), 7575))
        sock.listen(1)
        (sock2, address) = sock.accept()

        while True:
            header = sock2.recv(32)
            json_len, init_chunk = header.split("\n", 1)

            remaining = int(json_len) - len(init_chunk)
            json_str = init_chunk + sock2.recv(remaining, MSG_WAITALL)

            value = json.loads(json_str)
