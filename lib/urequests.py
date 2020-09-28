import usocket as socket
import uselect
import uerrno
import gc
import logging

_logger = logging.getLogger("urequest")


class Response:

    def __init__(self, f):
        self.raw = f
        self.encoding = "utf-8"
        self._cached = None

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.raw.read()
            finally:
                self.raw.close()
                self.raw = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson
        return ujson.loads(self.content)


def request(method, url, data=None, json=None, headers={}, stream=None):
    socket_timeout = 1000  # milliseconds
    gc.collect()
    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""

    if proto == "http:":
        port = 80
    elif proto == "https:":
        import ussl
        port = 443
    else:
        raise ValueError("urequest - Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        #s.setblocking(False)
    except Exception as e:
        _logger.exc(e, "urequest - Could not create a socket object")
        raise

    #  ATTEMPT TO CONNECT
    try:
        s.connect((host, port))
    except OSError as e:
        if e.args[0] not in [uerrno.EINPROGRESS, uerrno.ETIMEDOUT]:
            _logger.exc(e, "urequest - Error 'OSError' while trying to connect")
            s.close()
            raise
    except Exception as e:
        _logger.exc(e, "urequest - General Error while trying to connect")
        s.close()
        raise

    #  SEND DATA
    try:
        if proto == "https:":
            s = ussl.wrap_socket(s, server_hostname=host)
        s.write(b"%s /%s HTTP/1.0\r\n" % (method, path))
        if "Host" not in headers:
            s.write(b"Host: %s\r\n" % host)
        # Iterate over keys to avoid tuple alloc
        for k in headers:
            s.write(k)
            s.write(b": ")
            s.write(headers[k])
            s.write(b"\r\n")
        if json is not None:
            assert data is None
            import ujson
            data = ujson.dumps(json)
            s.write(b"Content-Type: application/json\r\n")
        if data:
            s.write(b"Content-Length: %d\r\n" % len(data))
        s.write(b"\r\n")
        if data:
            s.write(data)
    except OSError as e:
        if e.args[0] not in [uerrno.EINPROGRESS, uerrno.ETIMEDOUT]:
            _logger.exc(e, "urequest - ERROR 'OSError' while trying to write")
            s.close()
            raise
    except Exception as e:
        _logger.exc(e, "urequest - General ERROR while trying to write.")
        s.close()
        raise

    #  WAITING FOR A RESPONSE
    #s.settimeout(socket_timeout)
    try:
        # utime.sleep_ms(20)
        poller = uselect.poll()
        poller.register(s, uselect.POLLIN)
        res = poller.poll(socket_timeout)  # time in milliseconds
        poller.unregister(s)

        if res:
            l = s.readline()
            if len(l) == 0:
                _logger.info("Didn't receive 'l' data!")
                #s.close()
                raise RuntimeError("Didn't receive 'l' data!")

            l = l.split(None, 2)
            status = int(l[1])
            reason = ""
            if len(l) > 2:
                reason = l[2].rstrip()

            while True:
                l = s.readline()
                if not l or l == b"\r\n":
                    break
                if l.startswith(b"Transfer-Encoding:"):
                    if b"chunked" in l:
                        #s.close()
                        raise ValueError("Unsupported " + l)
                elif l.startswith(b"Location:") and not 200 <= status <= 299:
                    #s.close()
                    raise NotImplementedError("Redirects not yet supported")
        else:
            #s.close()
            _logger.info("Didn't receive data! [Timeout {}s]".format(socket_timeout/1000))
            raise RuntimeError("Didn't receive data! [Timeout {}s]".format(socket_timeout/1000))

    #except socket.timeout:
    #    print("Didn't receive data! [Timeout {}s]".format(socket_timeout))
    #    s.close()
    #    raise
    except Exception as e:
        _logger.exc(e, "urequest - ERROR waiting for a response")
        s.close()
        raise
    else:
        resp = Response(s)
        resp.status_code = status
        resp.reason = reason
        return resp


def head(url, **kw):
    return request("HEAD", url, **kw)


def get(url, **kw):
    return request("GET", url, **kw)


def post(url, **kw):
    return request("POST", url, **kw)


def put(url, **kw):
    return request("PUT", url, **kw)


def patch(url, **kw):
    return request("PATCH", url, **kw)


def delete(url, **kw):
    return request("DELETE", url, **kw)
