V2RAY_VER = "2.33.1"

if ! [ -d shadowsocksr ]; then
  echo "Downloading ShadowsocksR ..."
  git clone https://github.com/shadowsocksr/shadowsocksr.git || exit 1
fi

if ! [ -f v2ray/v2ray ]; then
  echo "Downloading V2Ray ..."
  curl -o v2ray.zip -L https://github.com/v2ray/v2ray-core/releases/download/v${V2RAY_VER}/v2ray-macos.zip || exit 1
  unzip v2ray.zip -d v2ray
fi

echo "Downloading SmarkSocks client ..."
curl https://raw.githubusercontent.com/waylybaye/SmartSocks/master/LICENSE > smart_socks.py
