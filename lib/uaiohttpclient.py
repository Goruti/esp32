import uasyncio as asyncio


class ClientResponse:

    def __init__(self, reader):
        self.content = reader

    def read(self, sz=-1):
        return (yield from self.content.read(sz))

    def aclose(self):
        yield from self.content.aclose()

    def __repr__(self):
        return "<ClientResponse %d %s>" % (self.status, self.headers)


class ChunkedClientResponse(ClientResponse):

    def __init__(self, reader):
        self.content = reader
        self.chunk_size = 0

    def read(self, sz=4*1024*1024):
        if self.chunk_size == 0:
            l = yield from self.content.readline()
            #print("chunk line:", l)
            l = l.split(b";", 1)[0]
            self.chunk_size = int(l, 16)
            #print("chunk size:", self.chunk_size)
            if self.chunk_size == 0:
                # End of message
                sep = yield from self.content.read(2)
                assert sep == b"\r\n"
                return b''
        data = yield from self.content.read(min(sz, self.chunk_size))
        self.chunk_size -= len(data)
        if self.chunk_size == 0:
            sep = yield from self.content.read(2)
            assert sep == b"\r\n"
        return data

    def __repr__(self):
        return "<ChunkedClientResponse %d %s>" % (self.status, self.headers)


def request_raw(method, url, data, json, headers):
    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    if proto == "http:":
        port = 80
    elif proto == "https:":
        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    if proto == "http:":
        reader, writer = yield from asyncio.open_connection(host=host, port=port)
    else:
        reader, writer = yield from asyncio.open_connection(host=host, port=port, ssl=True)
    try:
        # Use protocol 1.0, because 1.1 always allows to use chunked transfer-encoding
        # But explicitly set Connection: close, even though this should be default for 1.0,
        # because some servers misbehave w/o it.
        yield from writer.awrite(("%s /%s HTTP/1.0\r\nUser-Agent: compat\r\n" % (method, path)).encode('latin-1'))

        if "Host" not in headers:
            yield from writer.awrite(("Host: %s\r\n" % host).encode('latin-1'))

        for k in headers:
            yield from writer.awrite((k).encode('latin-1'))
            yield from writer.awrite((": ").encode('latin-1'))
            yield from writer.awrite((headers[k]).encode('latin-1'))
            yield from writer.awrite(("\r\n").encode('latin-1'))

        if json is not None:
            assert data is None
            import ujson
            data = ujson.dumps(json)
            yield from writer.awrite(("Content-Type: application/json\r\n").encode('latin-1'))
        if data:
            yield from writer.awrite(("Content-Length: %d\r\n" % len(data)).encode('latin-1'))

        yield from writer.awrite(("Connection: close\r\n\r\n").encode('latin-1'))

        if data:
            yield from writer.awrite(data)
    except:
        yield from writer.aclose()
        raise

    return reader


def request(method, url, data=None, json=None, headers={}):
    redir_cnt = 0
    while redir_cnt < 2:
        reader = yield from request_raw(method, url, data, json, headers)
        headers = []
        chunked = False
        try:
            sline = yield from reader.readline()
            sline = sline.split(None, 2)
            status = int(sline[1])
            while True:
                line = yield from reader.readline()
                if not line or line == b"\r\n":
                    break
                headers.append(line)
                if line.startswith(b"Transfer-Encoding:"):
                    if b"chunked" in line:
                        chunked = True
                elif line.startswith(b"Location:"):
                    url = line.rstrip().split(None, 1)[1].decode("latin-1")
        except:
            yield from reader.aclose()
            raise

        if 301 <= status <= 303:
            redir_cnt += 1
            yield from reader.aclose()
            continue
        break

    if chunked:
        resp = ChunkedClientResponse(reader)
    else:
        resp = ClientResponse(reader)
    resp.status = status
    resp.headers = headers
    return resp