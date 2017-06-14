# SmartSock

helps you automatically setup and choose the fastest socks server.


## Included Candidates

* shadowsocks-libev
* shadowsocksR
* V2Ray
* kcptun

## Usage

### Server

`docker run -d -p 8080:8080 -p 80 -p 443 -p 8848 -e PORTS=80,443,8848 -e CANDIDATES=ss,ssr,v2ray,kcptun hyperapp/smartsock`


### Mac Client

`curl -sL https://github.com/waylybaye/xxxxx/client.py | bash`

It will automatically download the clients of softwares above and try all encrypt method and obfs method and tcp/mkp protocal to find the fastest config.


