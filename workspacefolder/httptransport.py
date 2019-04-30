from typing import Optional
import logging
logger = logging.getLogger(__name__)


def remove_utf8_bom(src: bytes) -> bytes:
    '''
    test for powershell
    '''
    if len(src) >= 3 and src[0:3] == b'\xEF\xBB\xBF':
        return src[3:]
    else:
        return src


def get_line(src: bytearray) -> Optional[bytes]:
    if len(src) >= 2:
        # CRLF
        if src[-2] == 13 and src[-1] == 10:
            return bytes(src[:-2])


class HttpTransport:
    '''
    split keep-alive http stream to http messages
    '''

    def __init__(self):
        self.buffer = bytearray()
        self.content_length = 0
        self.headers = []
        self.on_msg_callbacks = []

    def append_callback(self, cb) -> None:
        self.on_msg_callbacks.append(cb)

    def push(self, b: bytes) -> None:
        self.buffer += b
        if self.content_length == 0:
            # header
            line = get_line(self.buffer)
            if line is not None:  # may be empty
                self.buffer.clear()
                if len(line) == 0:
                    # found end of headers
                    # find Content-Length
                    for h in self.headers:
                        if h.startswith(b'Content-Length: '):
                            self.content_length = int(h[15:])
                            break
                else:
                    # add header
                    self.headers.append(remove_utf8_bom(line))

        else:
            # body
            if len(self.buffer) == self.content_length:
                body = bytes(self.buffer)
                for cb in self.on_msg_callbacks:
                    cb(self.headers, body)
                self.buffer.clear()
                self.headers.clear()
                self.content_length = 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt='%H:%M:%S',
        format='%(asctime)s[%(levelname)s][%(name)s.%(funcName)s] %(message)s')

    import unittest

    class HttpTransportTest(unittest.TestCase):
        def test_http_transport(self):
            ht = HttpTransport()
            self.success = False

            def callback(h, b):
                self.success = True

            ht.append_callback(callback)

            http = [
                b'Content-Length: 2\r\n'
                b'\r\n',
                b'{}',
            ]
            for line in http:
                for i in range(len(line)):
                    ht.push(line[i:i + 1])

            self.assertTrue(self.success)

    unittest.main()