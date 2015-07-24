import hmac
import base64
import hashlib
import time
import urllib, urllib2
from urllib2 import BaseHandler, Request, HTTPError


ACCESS_KEY = ''
ACCESS_SECRET = ''

class AuthenticationError(Exception):

    error_code = 403

class BadRequest(Exception):

    error_code = 400

class InternalServerError(Exception):

    error_code = 500

class MethodNotAllowed(Exception):

    error_code = 405

class NotFound(Exception):

    error_code = 404

class UnknownError(Exception):
    pass

ERROR_MAPPINGS = {
    400: BadRequest,
    403: AuthenticationError,
    500: InternalServerError,
    405: MethodNotAllowed,
    404: NotFound,
    0:   UnknownError,
}

__all__ = ['configure', 'fetch_API'] + ERROR_MAPPINGS.values()

def configure(access_key, access_secret):
    """
    Configure the consts manually.
    """
    global ACCESS_KEY, ACCESS_SECRET

    ACCESS_KEY, ACCESS_SECRET = access_key, access_secret

import warnings

try:
    import sae.const
    ACCESS_KEY, ACCESS_SECRET = sae.const.ACCESS_KEY, sae.const.SECRET_KEY
except ImportError:
    raise warnings.ImportWarning(" The essential module `sae` was not present. You might set the consts later via `configure` method.")
APIBUS_URL_PREFIX = 'http://g.sae.sina.com.cn'

class SaeApibusAuthHandler(BaseHandler):
    
    handler_order = 100

    def _signature(self, secret, method, resource, headers):
        msgToSign = "\n".join([
            method, resource,
            "\n".join([(k + ":" + v) for k, v in sorted(headers)]),
        ])
        return "SAEV1_HMAC_SHA256 " + base64.b64encode(hmac.new(secret, msgToSign, hashlib.sha256).digest())

    def http_request(self, req):
        orig_url = req.get_full_url()

        if not orig_url.startswith(APIBUS_URL_PREFIX):
            return req

        timestamp = str(int(time.time()))
        headers = [
            ('x-sae-timestamp', timestamp),
            ('x-sae-accesskey', ACCESS_KEY),
        ]
        req.headers.update(headers)

        method = req.get_method()
        resource = urllib.unquote(req.get_full_url()[len(APIBUS_URL_PREFIX):])
        sae_headers = [
            (k.lower(), v.lower()) for k, v in req.headers.items() 
                if k.lower().startswith('x-sae-')
        ]
        req.add_header(
            'Authorization', 
            self._signature(ACCESS_SECRET, method, resource, sae_headers)
        )
        return req

    https_request = http_request

def fetch_API(url):
    """
    Notice that `url` is relative with a slash on the front.
    """

    url = APIBUS_URL_PREFIX + url
    apibus_handler = SaeApibusAuthHandler()
    opener = urllib2.build_opener(apibus_handler)
    try:
        response = opener.open(url)
        print response
        return (line for line in response.readlines())
    except HTTPError, e:

        error = ERROR_MAPPINGS.get(e.code, None)
        if error is not None:
            raise error
        else:
            raise UnknownError(e.code)