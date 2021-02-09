from mitmproxy import http
from mitmproxy import ctx
from mitmproxy.net.http.cookies import CookieAttrs
from mitmproxy.script import concurrent
import json
import codecs
import os
import gzip

is_logging = False
logging_domain = None
REQUESTS = {}

def b64_or_str(d):
    if isinstance(d, str):
        encoded = d
    else:
        encoded = codecs.encode(d, "base64").decode().strip()

    return encoded

def multi2dict(multi):
    data = {}
    for k,v in multi.items(multi=True):
        if not k in data:
            data[k] = []
        # Cookie handling
        if isinstance(v, tuple) and len(v) >= 2:
            if isinstance(v[1], CookieAttrs):
                v = [v[0]]
            elif isinstance(v[2], CookieAttrs):
                v = [v[0], v[1]]
        if isinstance(v, list):
            v = list(map(lambda x: b64_or_str(x), v))
        else:
            v = [b64_or_str(v)]
        data[k] += v

    return data

def req2dict(req):
    data = {
        'scheme': req.scheme,
        'host': req.host,
        'method': req.method,
        'port': req.port,
        'path': req.path,
        'content': b64_or_str(req.content),
        'url': req.url,
        'cookies': multi2dict(req.cookies),
        'query': multi2dict(req.query),
        'headers':multi2dict(req.headers),
        'multipart_form': multi2dict(req.multipart_form)
    }
    return data

def resp2dict(resp):
    return {
        'status_code': resp.status_code,
        'content': b64_or_str(resp.content),
        'cookies': multi2dict(resp.cookies),
        'headers': multi2dict(resp.headers)
    }

#@concurrent
def request(flow: http.HTTPFlow) -> None:
    global REQUESTS
    global is_logging
    global logging_domain

    if flow.request.pretty_host == "startlogging":
        REQUESTS = {}
        is_logging = True
        logging_domain = flow.request.path[1:]
        flow.response = http.HTTPResponse.make(
            200,
            b"Logging started",
            {"Content-Type": "text/plain"}
        )
        return
    if flow.request.pretty_host == "stoplogging":
        is_logging = False

        save_path = os.environ["FPNET_SAVE_PATH"] if 'FPNET_SAVE_PATH' in os.environ else None
        if save_path and REQUESTS:
            with gzip.open(os.path.join(save_path, "{}.json.gz".format(logging_domain)), 'wt') as fh:
                fh.write(json.dumps(REQUESTS))

        logging_domain = None
        REQUESTS = {}
        flow.response = http.HTTPResponse.make(
            200,
            b"Logging stopped",
            {"Content-Type": "text/plain"}
        )
        return

#@concurrent
def response(flow: http.HTTPFlow) -> None:
    global is_logging
    global REQUESTS

    if not is_logging or flow.request.pretty_host in ['startlogging', 'stoplogging']:
        return

    if not flow.id in REQUESTS:
        REQUESTS[flow.id] = {
            'request': req2dict(flow.request),
            'response': resp2dict(flow.response)
        }
