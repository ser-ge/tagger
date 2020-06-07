from thrift.transport import THttpClient

try:
    import urllib.parse

    quote = urllib.parse.quote
    urlparse = urllib.parse.urlparse
except:
    from urllib.parse import quote, urlparse

from io import BytesIO

def fixed_flush(self):
    if self.isOpen():
        self.close()
    self.open()

    # Pull data out of buffer
    data = self._THttpClient__wbuf.getvalue()
    self._THttpClient__wbuf = BytesIO()

    # HTTP request
    self._THttpClient__http.putrequest('POST', self.path, skip_host=True) # Don't duplicate Host header

    # Write headers
    self._THttpClient__http.putheader('Host', self.host)
    self._THttpClient__http.putheader('Content-Type', 'application/x-thrift')
    self._THttpClient__http.putheader('Content-Length', str(len(data)))

    if not self._THttpClient__custom_headers or 'User-Agent' not in self._THttpClient__custom_headers:
        user_agent = 'Python/THttpClient'
        script = os.path.basename(sys.argv[0])
        if script:
            user_agent = '%s (%s)' % (user_agent, quote(script))
        self._THttpClient__http.putheader('User-Agent', user_agent)

    if self._THttpClient__custom_headers:
        for key, val in self._THttpClient__custom_headers.items():
            self._THttpClient__http.putheader(key, val)

    self._THttpClient__http.endheaders()

    # Write payload
    self._THttpClient__http.send(data)

    # Get reply to flush the request
    self.response = self._THttpClient__http.getresponse()
THttpClient.THttpClient.flush = fixed_flush
