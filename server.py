#!/usr/bin/env python
from __future__ import unicode_literals
import os
import json
import atexit
import signal
import base64
import subprocess

try:
    from argparse import ArgumentParser as ArgParser
except ImportError:
    from optparse import OptionParser as ArgParser

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

__VERSION__ = '0.0.1'


def socks_command(payload):
    server = payload['server']
    port = payload['port']

    if server == 'shadowsocksr':
        path = "python /root/shadowsocksr-manyuser/shadowsocks/server.py "
        options = "-k '%(password)s' -m '%(encrypt)s' -p %(port)s -o %(obfs)s -O %(protocol)s" % payload
        command = path + options

    elif server == 'v2ray':
        command = "v2ray -c "

    else:
        raise ValueError("Unsupported socks server")

    print("COMMAND:", command)
    return command


class Server(BaseHTTPRequestHandler):
    username = ""
    password = ""
    latest_process = None

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

            if user != self.username or password != self.password:
                self.response(401, "Authentication Failed.")
                return

        except ValueError:
            self.response(401, "Invalid Authentication.")
            return

        content_length = int(self.headers.get('content-length', '0'))
        payload = self.rfile.read(content_length)
        if not payload:
            print("No Payload")
            self.response(406, "Payload required.")
            return

        try:
            payload = json.loads(payload)
        except ValueError:
            print("Payload invalid json")
            self.response(406, "Payload invalid.")
            return

        if Server.latest_process:
            print("[SmartSocks] closing previous socks")
            try:
                os.killpg(os.getpgid(Server.latest_process.pid), signal.SIGTERM)
            except OSError:
                pass

            Server.latest_process = None

        try:
            command = socks_command(payload)
        except ValueError:
            self.response(406, "Unsupported socks")
            return

        print("[SmartSocks] starting socks server")
        popen = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            shell=True, preexec_fn=os.setsid)

        atexit.register(popen.terminate)

        Server.latest_process = popen
        self.response(200, "Started")

        # self._set_headers()
        # self.wfile.write("<html><body><h1>POST!</h1></body></html>")


def run(server_class=HTTPServer, handler_class=Server, port=80, username="", password=""):
    server_address = ('', int(port))
    handler_class.username = username
    handler_class.password = password
    httpd = server_class(server_address, handler_class)
    # print 'Starting SmartSocks ...'
    print('[SmarkSocks] Waiting for clients ...')
    httpd.serve_forever()


def parse_args():
    description = "SmartSocks Server"
    parser = ArgParser(description=description)
    try:
        parser.add_argument = parser.add_option
    except AttributeError:
        pass

    parser.add_argument('-p', '--port', help='SmartSocks server port')
    parser.add_argument('-u', '--user', help='SmartSocks user',
                        default="admin")
    parser.add_argument('-P', '--password', help='SmartSocks password',
                        default="smartsocks")
    parser.add_argument('-V', '--version', action='store_true',
                        help='Show the version number and exit')

    options = parser.parse_args()
    if isinstance(options, tuple):
        args = options[0]
    else:
        args = options
    return args


def main():
    args = parse_args()
    run(port=args.port, username=args.user, password=args.password)


if __name__ == "__main__":
    main()
