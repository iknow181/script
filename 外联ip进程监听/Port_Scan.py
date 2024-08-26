import ctypes
import subprocess
import psutil
import sys

def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_open_ports():
    """使用 netstat 获取开放端口和对应的进程 ID"""
    open_ports = []
    result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    for line in lines:
        if 'LISTENING' in line:
            parts = line.split()
            port = int(parts[1].split(':')[-1])
            pid = int(parts[-1])
            open_ports.append((port, pid))
    return open_ports

def get_process_info(pid):
    """通过进程 ID 获取进程名称和路径"""
    try:
        process = psutil.Process(pid)
        return process.name(), process.exe()
    except psutil.NoSuchProcess:
        return None, None

def main():
    """主程序入口"""
    open_ports = get_open_ports()
    print(f"{'Port':<10} {'Process Name':<25} {'Process Path':<50}")
    print("="*85)
    for port, pid in open_ports:
        process_name, process_path = get_process_info(pid)
        if process_name and process_path:
            print(f"{port:<10} {process_name:<25} {process_path:<50}")

if __name__ == "__main__":
    if is_admin():
        main()
        input()
    else:
        # 以管理员权限重新运行程序
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
