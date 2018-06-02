# SmartSock


DEPRECATION WARNING: NO LONGER BEING MAINTAINED
----

helps you automatically setup and choose the fastest socks server.

SmartSocks 是一个服务端和客户端自动协商最快传输协议的工具。客户端会自动尝试 SSR/V2Ray 推荐的配置组合，然后使用 `speedtest` 来测速。


## 支持的应用

- [x] shadowsocksR
- [x] V2Ray (tcp & kcp)
- [ ] kcptun (TODO)

### TODO

- [x] 自动尝试各种加密/协议并测速
- [ ] 根据测速结果自动在本地开放一个 socks 端口


## 服务端

### 安装

在 `HyperApp → 商店 → 网络` 分组下面找到 `SmartSocks` 安装，配置时只要填入一个主控端口，和用户名密码即可。


## 客户端

### 支持的应用

### 安装 (Linux & macOS)

#### 下载依赖

`curl -sL https://raw.githubusercontent.com/waylybaye/SmartSocks/master/install_client.sh | bash`

#### 使用方法

```bash
cd smartsocks
python client.py -s 服务器地址 -p 主控端口 -u 用户名 -P 密码 -S socks端口
```

* `主控端口` 是指SmartSocks 服务端监听的端口
* `socks端口` 是指 SSR/V2ray 监听的端口

运行后客户端会自动尝试各种推荐的加密/协议组合，并测速。
