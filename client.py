# encoding: utf8
import os
import subprocess
import speedtest

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
            name: 'ShadowsocksR auth_chain_a + none * OBFS',
            protocol: 'auth_chain_a',
            encrypt: 'none',
            obfs: ['plain', 'http_simple', 'tls1.2_ticket_auth', 'http_post']
        },
    ]
}


def main():
    for server, plans in suggested_plans.items():
        print("服务器: ", server)
        for plan in plans:
            print("测试配置：")

            os.system('python speedtest.py --simple')


if __name__ == '__main__':
    main()
