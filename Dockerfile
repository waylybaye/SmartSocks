FROM v2ray/official
FROM breakwa11/shadowsocksr

MAINTAINER HyperApp <hyperappcloud@gmail.com>

ENV SMART_PORT 8000
ENV USERNMAE admin
ENV PASSWORD smartsocks
EXPOSE $SMART_PORT

ADD server.py /usr/local/bin/smart-server
ADD ss-server.sh /usr/local/bin/ss-server

CMD smart-server -p $SMART_PORT -u $USERNAME -P $PASSWORD
