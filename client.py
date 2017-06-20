#!/bin/env python
# encoding: utf8
from __future__ import unicode_literals, print_function

import copy
import os
import json
import tempfile
import time
import uuid
import atexit
import base64
import signal
import itertools
import subprocess
from collections import OrderedDict

LOCAL_PORT = 1117

import socks
import socket
# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", LOCAL_PORT)
# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 19870)
raw_socket = socket.socket
socket.socket = socks.socksocket

import httplib
import urllib2
import speedtest


try:
    from argparse import ArgumentParser as ArgParser
except ImportError:
    from optparse import OptionParser as ArgParser

__VERSION__ = '0.0.1'
LATEST_PROCESS = None
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
    "outboundDetour": [
        {
            "protocol": "freedom",
            "tag": "direct",
            "settings": {
            }
        }
    ],
    "inbound": {
        "listen": "127.0.0.1",
        "port": LOCAL_PORT,
        "protocol": "socks",
        "settings": {
            "ip": "127.0.0.1",
            "auth": "noauth"
        },
        "allowPassive": False
    },
    "routing": {
        "strategy": "rules",
        "settings": {
            "domainStrategy": "IPIfNonMatch",
            "rules": [
                {
                    "port": "1-52",
                    "type": "field",
                    "outboundTag": "direct"
                },
                {
                    "port": "54-79",
                    "type": "field",
                    "outboundTag": "direct"
                },
                {
                    "port": "81-442",
                    "type": "field",
                    "outboundTag": "direct"
                },
                {
                    "port": "444-65535",
                    "type": "field",
                    "outboundTag": "direct"
                },
                {
                    "type": "field",
                    "ip": [
                        "0.0.0.0/8",
                        "10.0.0.0/8",
                        "100.64.0.0/10",
                        "127.0.0.0/8",
                        "169.254.0.0/16",
                        "172.16.0.0/12",
                        "192.0.0.0/24",
                        "192.0.2.0/24",
                        "192.168.0.0/16",
                        "198.18.0.0/15",
                        "198.51.100.0/24",
                        "203.0.113.0/24",
                        "::1/128",
                        "fc00::/7",
                        "fe80::/10"
                    ],
                    "outboundTag": "direct"
                }
            ]
        }
    },
    "log": {
        "loglevel": "warning",
        "access": "/dev/stdout",
        "error": "/dev/stderr"
    },
    "outbound": {
        "protocol": "vmess",
        "streamSettings": {
            "network": "tcp",
            "tcpSettings": {
                "header": {
                    "type": "http"
                },
                "connectionReuse": True
            },
            # "kcpSettings": {
            #     "header": {
            #         "type": "none"
            #     },
            # },
            # "security": "tls",
            "security": "none",
            # "tlsSettings": {
            #     "allowInsecure": false
            # },
            "wsSettings": {
                "path": "",
                "connectionReuse": False
            }
        },
        "settings": {
            "vnext": [
                {
                    "address": "",
                    "port": 0,
                    "users": [
                        {
                            "id": "",
                            "alterId": 64,
                            "security": "aes-128-cfb"
                        }
                    ]
                }
            ]
        }
    }
}


suggested_plans = OrderedDict([
    ('shadowsocksr', [
        {
            'name': 'ShadowsocksR auth_chain_a + none * OBFS',
            'protocol': 'auth_chain_a',
            'encrypt': 'none',
            'obfs': ['plain', 'http_simple', 'tls1.2_ticket_auth']
        },
        {
            'name': 'ShadowsocksR [chacha20, rc4-md5] + auth_aes128_md5 * OBFS',
            'protocol': 'auth_aes128_md5',
            'encrypt': ['chacha20', 'rc4-md5'],
            'obfs': ['plain', 'http_simple', 'tls1.2_ticket_auth']
        }
    ]),
    ('v2ray', [
        {
            'name': 'V2Ray VMess tcp * [none, http] obfs',
            'uuid': str(uuid.uuid4()),
            'network': 'tcp',
            'obfs': ['none', 'http']
        },
        {
            'name': 'V2Ray VMess kcp',
            'uuid': str(uuid.uuid4()),
            'network': 'kcp',
            'obfs': 'none',
        }
    ])
])


def start_socks(server, port, socks_port, username, password, socks_server, params):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    global LATEST_PROCESS
    query = {
        'port': socks_port,
        'server': socks_server,
        'password': password,
    }
    query.update(params)
    request = urllib2.Request('http://%s:%s/socks' % (server, port), json.dumps(query))
    if username and password:
        auth = base64.encodestring('%s:%s' % (username, password))
        request.add_header('Authorization', 'Basic %s' % auth.strip())

    print(darkgrey + '[SERVER]', query, reset)
    request.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(request)
    response.read()

    if LATEST_PROCESS:
        try:
            os.killpg(os.getpgid(LATEST_PROCESS.pid), signal.SIGTERM)
        except OSError:
            pass

    print(darkgrey + "Starting %s client:" % socks_server)
    if socks_server == 'shadowsocksr':
        path = os.path.join(BASE_DIR, 'shadowsocksr/shadowsocks/local.py')
        command = 'python %s -s %s -p %s -k %s -m %s -O %s -o %s -l %s' % (
            path, server, socks_port, password, params['encrypt'], params['protocol'], params['obfs'], LOCAL_PORT
        )

    elif socks_server == 'v2ray':
        config_path = tempfile.mktemp('.json')
        config_file = open(config_path, 'w')
        config = copy.deepcopy(V2Ray_CONFIG)
        config['outbound']['settings']['vnext'][0]['address'] = server
        config['outbound']['settings']['vnext'][0]['port'] = int(socks_port)
        config['outbound']['settings']['vnext'][0]['users'][0]['id'] = params['uuid']
        config['outbound']['streamSettings']['network'] = params['network']
        config['outbound']['streamSettings']['tcpSettings']['header']['type'] = params['obfs']

        config_file.write(json.dumps(config, indent=2))
        command = os.path.join(BASE_DIR, 'v2ray') + ' -config ' + config_path
        print(darkgrey + "[CLIENT]", command, reset)
    else:
        raise ValueError('')

    print(darkgrey + command + reset)
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
        shell=True,
        preexec_fn=os.setsid
    )

    atexit.register(process.terminate)

    LATEST_PROCESS = process


def main():
    args = parse_args()
    if args.version:
        print(__VERSION__)
        return

    if not args.server or not args.port:
        print(red + "server and port is required", reset)
        return

    speed = None
    speedtest_servers = []

    for socks_server, plans in suggested_plans.items():
        print("代理软件:", green, socks_server, reset)
        for plan in plans:
            print("测试配置:", green, plan['name'], reset)
            print(darkgrey + '=' * 80, reset)
            data = dict(plan.items())
            data.pop('name')

            params = []
            choices = []
            for param, values in data.items():
                params.append(param)
                choices.append(values if isinstance(values, (tuple, list)) else [values])

            for choice in itertools.product(*choices):
                payload = dict(zip(params, choice))
                print("子配置:", orange, payload, reset)

                try:
                    socks.setdefaultproxy()
                    start_socks(
                        args.server,
                        args.port,
                        args.socks_port,
                        args.user,
                        args.password,
                        socks_server,
                        payload,
                    )
                except urllib2.HTTPError as e:
                    if e.code == 401:
                        print(red + 'ERROR: Invalid username or password', reset)
                        return

                    print(red + 'ERROR: Failed to start socks on server', reset)
                    print(darkgrey + '-' * 80, reset)
                    # print(e.code, e.reason)
                    # print(dir(e))
                    return

                for x in range(20):
                    sock = raw_socket()
                    try:
                        sock.connect(('localhost', LOCAL_PORT))
                        sock.close()
                        print(green + 'Local port started ...', reset)
                        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", LOCAL_PORT)
                        time.sleep(0.2)
                        break
                    except socket.error:
                        time.sleep(0.1)
                        continue
                else:
                    print(red + 'Client no response, skip ...', reset)
                    continue

                try:
                    if not speed:
                        speed = speedtest.Speedtest()
                        print(darkgrey + "[SPEEDTEST] Fetch servers ...", reset)
                        speed.get_servers(speedtest_servers)
                        print(darkgrey + "[SPEEDTEST] Choose closest server ...", reset)
                        speed.get_best_server()
                        print(darkgrey + '[SPEEDTEST] Hosted by %(sponsor)s (%(name)s) [%(d)0.2f km]: %(latency)s ms' % speed.results.server, reset)

                    print(darkgrey + "[SPEEDTEST] Downloading ...", reset)
                    speed.download()
                    results = speed.results
                    print(green + '[SPEEDTEST] Ping: %s ms\tDownload: %0.2f Mbps\tUpload: %0.2f Mbps' %
                          (results.ping,
                           (results.download / 1000.0 / 1000.0),
                           (results.upload / 1000.0 / 1000.0),
                           ), reset)

                except (speedtest.SpeedtestException, httplib.HTTPException):
                    print(darkgrey + "[SPEEDTEST]", red + 'ERROR: Failed to connect', reset)

                print(darkgrey + '-' * 80, reset)

    return


def parse_args():
    description = "SmartSocks"
    parser = ArgParser(description=description)
    try:
        parser.add_argument = parser.add_option
    except AttributeError:
        pass

    parser.add_argument('-s', '--server', help='SmartSocks server')
    parser.add_argument('-p', '--port', help='SmartSocks port')
    parser.add_argument('-u', '--user', help='SmartSocks user',
                        default='admin')
    parser.add_argument('-P', '--password', help='SmartSocks password',
                        default='smartsocks')
    parser.add_argument('-S', '--socks-port', help='SmartSocks port', default=8848)
    parser.add_argument('-V', '--version', action='store_true',
                        help='Show the version number and exit')

    options = parser.parse_args()
    if isinstance(options, tuple):
        args = options[0]
    else:
        args = options
    return args


if __name__ == '__main__':
    main()
