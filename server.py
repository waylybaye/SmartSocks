#!/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer


class Server(BaseHTTPRequestHandler):
    username = ""
    password = ""

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    # def handle(self):
        # print("handle")
        # super(BaseHTTPRequestHandler, self).handle()
        # super(Server).handle()
        # B.handle(self)
        # BaseHTTPRequestHandler.handle(self)
        # print("headers", self.headers)

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>hi!</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        print("headers", self.headers)
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")


def run(server_class=HTTPServer, handler_class=Server, port=80, username="", password=""):
    server_address = ('', port)
    handler_class.username = username
    handler_class.pasword = password
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]), username="admin", password="admin")
    else:
        run()
