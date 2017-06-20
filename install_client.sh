V2RAY_VER="2.33.1"
DIRECTORY="smartsocks"

if ! [ -d $DIRECTORY ]; then
  echo "[SmartSocks] Make directory ./$DIRECTORY"
  mkdir $DIRECTORY
fi

cd $DIRECTORY

if ! [ -d shadowsocksr ]; then
  echo "[SmartSocks] Downloading ShadowsocksR ..."
  git clone https://github.com/shadowsocksr/shadowsocksr.git || exit 1
fi

if ! [ -f v2ray ]; then
  echo "[SmartSocks] Downloading V2Ray ${V2RAY_VER} ..."
  curl -o v2ray.zip -L https://github.com/v2ray/v2ray-core/releases/download/v${V2RAY_VER}/v2ray-macos.zip || exit 1
  unzip v2ray.zip -d tmp
  mv tmp/v2ray-v${V2RAY_VER}-macos/v2ray v2ray
  rm -rf tmp
  rm v2ray.zip
fi

echo "[SmartSocks] Downloading SmartSocks client ..."
curl -s https://raw.githubusercontent.com/waylybaye/SmartSocks/master/client.py > client.py
curl -s https://raw.githubusercontent.com/waylybaye/SmartSocks/master/socks.py > socks.py
curl -s https://raw.githubusercontent.com/waylybaye/SmartSocks/master/speedtest.py > speedtest.py

echo "========================"
echo "Usage: python client.py"
python client.py -h
