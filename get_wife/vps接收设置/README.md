# WiFi 数据收集服务的 VPS 设置指南

本指南将帮助你在一台新的 Linux VPS 上设置一个基于 Flask 的服务，用于通过 HTTP POST 请求接收 WiFi 配置文件数据。

## 前提条件

- 拥有一台 Linux VPS，并具有 root 权限。
- 具备基本的 SSH 和命令行操作知识。

## 设置步骤

### 步骤 1：将脚本上传到 VPS

首先，将 `linux_setup_vps.sh` 脚本保存到本地机器上，然后使用 `scp` 或其他文件传输方法将其上传到你的 VPS。

```bash
scp linux_setup_vps.sh your_username@your_vps_ip:/path/to/destination
```

### 步骤 2：赋予脚本执行权限

在 VPS 上，使用以下命令为脚本赋予

```
chmod +x linux_setup_vps.sh
```

### 步骤 3：运行脚本

使用以下命令在 VPS 上运行脚本：

```
sudo ./linux_setup_vps.sh
```

### 步骤 4：验证服务

脚本运行完成后，Flask 应用将会在端口 80 上启动并监听来自客户端的 POST 请求。接收的数据将被保存到 `/opt/flask_app/received_data.txt` 文件中。

你可以使用以下命令查看服务状态：

```
systemctl status flask_app.service
```

## 脚本说明

`linux_setup_vps.sh` 脚本会执行以下操作：

1. **系统更新**：更新系统包，确保系统处于最新状态。
2. **安装 Python 3 和 pip3**：安装 Python 3 和 `pip3`，为 Flask 框架提供运行环境。
3. **安装 Flask**：通过 `pip` 安装 Flask 框架。
4. **创建 Flask 应用**：创建一个 Flask 应用，监听 HTTP POST 请求并保存接收到的 WiFi 数据。
5. **配置系统服务**：将 Flask 应用配置为系统服务，设置为开机自启并在后台运行。

## 注意事项

- 如果你希望通过 HTTPS 传输数据，需进一步配置 SSL 证书。
- 你可以根据需求修改 Flask 应用，以增加例如身份验证等安全措施。

setup_vps.sh是我在Windows上写的，直接复制到Linux上发生了错误。建议直接使用linux_setup_vps.sh









