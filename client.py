#!/bin/env python
# encoding: utf8
from __future__ import unicode_literals, print_function

import base64
import json
import os
import socket
import subprocess
import urllib
import urllib2

import socks
import speedtest


try:
    from argparse import ArgumentParser as ArgParser
except ImportError:
    from optparse import OptionParser as ArgParser

# servers = []
# s = speedtest.Speedtest()
# s.get_servers(servers)
# s.get_best_server()
#
# for i in xrange(3):
#     s.download()
#     print s.results.dict()
# s.upload()
# s.share()


suggested_plans = {
    'shadowsocksr': [
        {
            'name': 'ShadowsocksR auth_chain_a + none * OBFS',
            'protocol': 'auth_chain_a',
            'encrypt': 'none',
            'obfs': ['plain', 'http_simple', 'tls1.2_ticket_auth', 'http_post']
        },
    ]
}


def start_socks(server, port, username, password, socks, params):
    query = {
        'server': socks,
    }
    query.update(params)
    request = urllib2.Request('http://%s:%s/socks' % (server, port), json.dumps(query))
    if username and password:
        auth = base64.encodestring('%s:%s' % (username, password))
        request.add_header('Authorization', 'Basic %s' % auth.strip())
    request.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(request)
    print(response.read())


def main():
    args = parse_args()
    socket.socket = socks.socksocket

    servers = []
    # If you want to test against a specific server
    # servers = [1234]

    start_socks(args.server, args.port, args.user, args.password, 'shadowsocksr', {'protocol': 'auth_chain_a'})

    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1987)
    s = speedtest.Speedtest()
    print("Fetch servers ...")
    s.get_servers(servers)
    print("Test closest server ...")
    s.get_best_server()
    print('Hosted by %(sponsor)s (%(name)s) [%(d)0.2f km]: %(latency)s ms' % s.results.server)

    for x in range(3):
        s.download()

        results = s.results
        # results_dict = s.results.dict()
        print('Ping: %s ms\nDownload: %0.2f Mbps\nUpload: %0.2f Mbps' %
               (results.ping,
                (results.download / 1000.0 / 1000.0),
                (results.upload / 1000.0 / 1000.0),
                ))
    return

    for server, plans in suggested_plans.items():
        print("服务器: ", server)
        for plan in plans:
            print("测试配置：")

            os.system('python speedtest.py --simple')


def parse_args():
    description = "SmartSocks"
    parser = ArgParser(description=description)
    # Give optparse.OptionParser an `add_argument` method for
    # compatibility with argparse.ArgumentParser
    try:
        parser.add_argument = parser.add_option
    except AttributeError:
        pass

    parser.add_argument('-s', '--server', help='SmartSocks server', required=True)
    parser.add_argument('-p', '--port', help='SmartSocks port')
    parser.add_argument('-u', '--user', help='SmartSocks user')
    parser.add_argument('-P', '--password', help='SmartSocks password')
    parser.add_argument('-S', '--socks-port', help='SmartSocks port')
    # parser.add_argument('--version', action='store_true',
                        # help='Show the version number and exit')
    # parser.add_argument('--debug', action='store_true',
                        # help=ARG_SUPPRESS, default=ARG_SUPPRESS)

    options = parser.parse_args()
    if isinstance(options, tuple):
        args = options[0]
    else:
        args = options
    return args


if __name__ == '__main__':
    main()
