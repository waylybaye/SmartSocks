V2RAY_VER="2.33.1"
DIRECTORY="smartsocks"

case "$(uname -s)" in
    Darwin)
        V2RAY_PLATFORM="macos"
     ;;

    Linux)
        V2RAY_PLATFORM="linux-64"
    ;;
esac

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
  curl -o v2ray.zip -L https://github.com/v2ray/v2ray-core/releases/download/v${V2RAY_VER}/v2ray-${V2RAY_PLATFORM}.zip || exit 1
  unzip v2ray.zip -d tmp
  mv tmp/v2ray-v${V2RAY_VER}-${V2RAY_PLATFORM}/v2ray v2ray
  chmod +x v2ray
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
