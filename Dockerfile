FROM breakwa/shadowsocksr
FROM v2ray/official

MAINTAINER HyperApp <hyperappcloud@gmail.com>

ENV SMART_PORT 8000
ENV USERNMAE admin
ENV PASSWORD smartsocks
EXPOSE $SMART_PORT

RUN ln -s /root/shadowsocksr-manyuser/shadowsocks/server.py /usr/local/bin/ss-server
ADD server.py /usr/local/bin/smart-server
ADD ss-server.sh /usr/local/bin/ss-server

CMD smart-server -p $SMART_PORT -u $USERNAME -P $PASSWORD
