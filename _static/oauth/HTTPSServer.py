#!/bin/env python3
# -*- coding: utf-8 -*-

from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler

import os
import ssl

def generate_cert(cert_path):
    """
    Use OpenSSL to create a new Cert and Key
    """
    import random
    from OpenSSL import crypto
    if cert_path is not None and os.path.isfile(cert_path):
        return

    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)

    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "PY"
    cert.get_subject().ST = "Python HTTPSServer"
    cert.get_subject().OU = "Python HTTPSServer"
    cert.get_subject().CN = "172.29.141.55"
    # Use a unique serial number
    cert.set_serial_number(random.randint(1, 2147483647))
    cert.gmtime_adj_notBefore(0)
    # Expire cert after 1 year
    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, "sha256")

    cert_pem = crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode()
    key_pem = crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode()

    with open(cert_path, "w") as f:
        f.write(key_pem)
        f.write(cert_pem)

class HTTPSServer(HTTPServer):
    """
    HTTPServer Class, with its socket wrapped in TLS using ssl.wrap_socket
    """

    def __init__(self, cert_path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Wrap Socket using TLS cert
        self.cert_path = cert_path
        self.context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(self.cert_path)
        self.socket = self.context.wrap_socket(
            self.socket,
            server_side=True)

certfile_path = "server.pem"
generate_cert(certfile_path)

host= ''
port = 8443
http_handler = partial(SimpleHTTPRequestHandler, directory=os.getcwd())
with HTTPSServer(certfile_path, (host, port), http_handler) as httpd:
    [h, p] = httpd.socket.getsockname()
    print(f"Serving HTTPS on {h} port {p} (https://{h}:{p}/) ...")
    print(f"Using TLS Cert: {certfile_path}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
