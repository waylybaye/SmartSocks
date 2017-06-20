#!/bin/env python
# encoding: utf8
from __future__ import unicode_literals, print_function

import os
import json
import time
import atexit
import base64
import signal
import itertools
import subprocess

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

suggested_plans = {
    'shadowsocksr': [
        {
            'name': 'ShadowsocksR auth_chain_a + none * OBFS',
            'protocol': 'auth_chain_a',
            'encrypt': 'none',
            'obfs': ['plain', 'http_simple', 'tls1.2_ticket_auth']
        },
    ]
}


def start_socks(server, port, socks_port, username, password, socks_server, params):
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

    print('[DEBUG]', query)
    request.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(request)
    response.read()

    if LATEST_PROCESS:
        try:
            os.killpg(os.getpgid(LATEST_PROCESS.pid), signal.SIGTERM)
        except OSError:
            pass

    print("Starting %s client" % socks_server)
    if socks_server == 'shadowsocksr':
        command = 'python ../../code/shadowsocksr/shadowsocks/local.py -v -s %s -p %s -k %s -m %s -O %s -o %s -l %s' % (
            server, socks_port, password, params['encrypt'], params['protocol'], params['obfs'], LOCAL_PORT
        )
        # print("客户端:", orange, command, reset)
        print("客户端:", command)

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
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



    speed = None
    speedtest_servers = []

    for socks_server, plans in suggested_plans.items():
        print("代理软件:", green, socks_server, reset)
        for plan in plans:
            print("测试配置:", green, plan['name'], reset)
            print('=' * 80)
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
                except urllib2.HTTPError:
                    print(red + 'ERROR: Failed to start socks on server', reset)
                    print('-' * 80)
                    continue

                for x in range(20):
                    sock = raw_socket()
                    try:
                        sock.connect(('127.0.0.1', LOCAL_PORT))
                        sock.close()
                        print(green + 'Client started ...', reset)
                        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", LOCAL_PORT)
                        time.sleep(0.2)
                        break
                    except socket.error:
                        time.sleep(0.1)
                        continue
                else:
                    print(red + 'Client no response ...', reset)

                # print('get ip')
                # url = 'http://ifconfig.me/ip'
                # request = urllib2.Request(url)
                # request.add_header('Cache-Control', 'max-age=0')
                # response = urllib2.urlopen(request)
                # print(response.read())

                try:
                    if not speedtest_servers:
                        speed = speedtest.Speedtest()
                        print("[SPEEDTEST] Fetch servers ...")
                        speed.get_servers(speedtest_servers)
                        print("[SPEEDTEST] Choose closest server ...")
                        speed.get_best_server()
                        print('[SPEEDTEST] Hosted by %(sponsor)s (%(name)s) [%(d)0.2f km]: %(latency)s ms' % speed.results.server)

                    speed.download()
                    results = speed.results
                    print('[SPEEDTEST] Ping: %s ms\nDownload: %0.2f Mbps\nUpload: %0.2f Mbps' %
                          (results.ping,
                           (results.download / 1000.0 / 1000.0),
                           (results.upload / 1000.0 / 1000.0),
                           ))

                except (speedtest.SpeedtestException, httplib.HTTPException):
                    print("[SPEEDTEST]", red, 'ERROR: Failed to connect', reset)

                print('-' * 80)

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
    parser.add_argument('-u', '--user', help='SmartSocks user')
    parser.add_argument('-P', '--password', help='SmartSocks password')
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
