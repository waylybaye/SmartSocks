# coding: utf8
from __future__ import unicode_literal
from __future__ import print_function

import os
import subprocess
# import SimpleHTTPServer
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver


def start_server(server, port):
    pass


def main():
    supported_servers = ['ss', 'ssr', 'v2ray']
    ports = os.environ.get('PORTS')
    servers = os.environ.get('SERVERS', '').strip().split(',') or ['ss', 'ssr', ''] 

    if not ports:
        print("PORTS required")
        return

    elif not ''.join(ports.split(',')).isdigit():
        print("PORTS must be interger")
        return

    if set(servers) - set(supported_servers):
        print("Unsupported server: ", ','.join(set(servers) - set(supported_servers)))
        return

    ports = ports.split(',')

    for server in servers:
        for port in ports:
            start_server(server, port)

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler



if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

    main()

