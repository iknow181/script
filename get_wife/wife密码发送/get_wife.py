import subprocess
import re

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
    with open(filename, 'w') as file:
        for profile in profiles:
            password = get_wifi_password(profile)
            file.write(f"Wife名称: {profile}\nWife密码: {password}\n\n")

if __name__ == "__main__":
    profiles = get_wifi_profiles()
    if profiles:
        save_passwords_to_file(profiles, "1.txt")
        print("密码已保存到1.txt")
        print("End of script by iknow")
    else:
        print("未找到WiFi配置文件。")

