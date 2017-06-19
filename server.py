#!/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import base64
import subprocess


class Server(BaseHTTPRequestHandler):
    username = ""
    password = ""

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self.send_response(405)

    def do_HEAD(self):
        self._set_headers()

    def response(self, status, content):
        self.send_response(status)
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        if self.path != '/socks':
            self.send_response(404)
            return

        authentication = self.headers.get('authorization')
        if not authentication:
            self.response(401, "Authentication required.")
            return

        if not authentication.startswith('Basic '):
            self.response(401, "Unsupported Authentication.")
            return

        try:
            auth = base64.decodestring(authentication.split(' ')[1])
            tuples = auth.split(':')
            user = tuples[0]
            password = tuples[1] if len(tuples) > 1 else ''
            print auth, self.username, self.password

            if user != self.username or password != self.password:
                self.response(401, "Authentication Failed.")
                return

        except ValueError:
            self.response(401, "Invalid Authentication.")
            return

        print("headers", self.headers.items())
        # Doesn't do anything with posted data
        print("path", self.path)
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")


def run(server_class=HTTPServer, handler_class=Server, port=80, username="", password=""):
    server_address = ('', port)
    handler_class.username = username
    handler_class.password = password
    httpd = server_class(server_address, handler_class)
    # print 'Starting SmartSocks ...'
    print '[SmarkSocks] Waiting for clients ...'
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]), username="admin", password="admin")
    else:
        run()
