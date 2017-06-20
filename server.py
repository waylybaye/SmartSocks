#!/usr/bin/env python
from __future__ import unicode_literals, print_function
import os
import copy
import json
import atexit
import signal
import base64
import subprocess
import tempfile

try:
    from argparse import ArgumentParser as ArgParser
except ImportError:
    from optparse import OptionParser as ArgParser

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

__VERSION__ = '0.0.1'
reset = '\033[0m'
red = '\033[31m'
black = '\033[30m'
green = '\033[32m'
orange = '\033[33m'
blue = '\033[34m'
purple = '\033[35m'
cyan = '\033[36m'
lightgrey = '\033[37m'
darkgrey = '\033[90m'

V2Ray_CONFIG = {
    "log": {
        "access": "/dev/stdout",
        "error": "/dev/stderr",
        "loglevel": "warning"
    },
    "inbound": {
        "port": '',
        "protocol": "vmess",
        "settings": {
            "clients": [
                {
                    "id": '',
                    "level": 1,
                    "alterId": 64,
                }
            ],
            "default": {
                "level": 1,
                "alterId": 32
            },
        },
        "streamSettings": {
            "network": '',
            "security": "none",
        }
    },
    "outbound": {
        "protocol": "freedom",
        "settings": {}
    }
}

V2Ray_TCP = {
    "connectionReuse": True,
    "header": {
        "type": "http",
        "request": {
            "version": "1.1",
            "method": "GET",
            "path": [
                "/"
            ],
            "headers": {
                "Host": [
                    "www.bing.com"
                ],
                "User-Agent": [
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_2 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/53.0.2785.109 Mobile/14A456 Safari/601.1.46"
                ],
                "Accept-Encoding": [
                    "gzip, deflate"
                ],
                "Connection": [
                    "keep-alive"
                ],
                "Pragma": "no-cache"
            }
        },
        "response": {
            "version": "1.1",
            "status": "200",
            "reason": "OK",
            "headers": {
                "Content-Type": [
                    "application/octet-stream",
                    "video/mpeg"
                ],
                "Transfer-Encoding": [
                    "chunked"
                ],
                "Connection": [
                    "keep-alive"
                ],
                "Pragma": "no-cache"
            }
        }
    }
}


def socks_command(payload):
    server = payload['server']
    port = payload['port']

    if server == 'shadowsocksr':
        path = "python /root/shadowsocksr-manyuser/shadowsocks/server.py "
        options = "-k '%(password)s' -m '%(encrypt)s' -p %(port)s -o %(obfs)s -O %(protocol)s" % payload
        command = path + options

    elif server == 'v2ray':
        config_path = tempfile.mktemp('.json')
        config_file = open(config_path, 'w')
        config = copy.deepcopy(V2Ray_CONFIG)
        config['inbound']['port'] = payload['port']
        config['inbound']['settings']['clients'][0]['id'] = payload['uuid']
        config['inbound']['streamSettings']['network'] = payload['network']

        if payload['obfs'] == 'http':
            config['inbound']['streamSettings']['tcpSettings'] = copy.deepcopy(V2Ray_TCP)

        config_file.write(json.dumps(config, indent=2))
        config_file.close()
        command = "v2ray -config " + config_path

    else:
        raise ValueError("Unsupported socks server")

    print(orange + "COMMAND:", command, reset)
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
            print(red + "No Payload", reset)
            self.response(406, "Payload required.")
            return

        try:
            payload = json.loads(payload)
        except ValueError:
            print(red + "Payload invalid json", reset)
            self.response(406, "Payload invalid.")
            return

        if Server.latest_process:
            print(orange + "[SmartSocks] closing previous socks", reset)
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

        print(green + "[SmartSocks] starting socks server", reset)
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
    print(green + '[SmarkSocks] Waiting for clients ...', reset)
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
