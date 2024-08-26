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

def get_process_info_alternative(port):
    """通过 PowerShell 获取进程名称和路径"""
    try:
        result = subprocess.run(['powershell', '-Command', f"Get-Process -Id (Get-NetTCPConnection -LocalPort {port}).OwningProcess | Select-Object -Property ProcessName, Path"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        print(f"PowerShell output for port {port}: {lines}")  # 添加调试信息
        if len(lines) > 3:
            process_name = lines[3].strip()
            process_path = lines[4].strip()
            return process_name, process_path
    except Exception as e:
        print(f"Error retrieving process info for port {port}: {e}")  # 添加调试信息
        return None, None

def main():
    """主程序入口"""
    open_ports = get_open_ports()
    print(f"{'Port':<10} {'Process Name':<25} {'Process Path':<50}")
    print("="*85)
    remaining_ports = []
    for port, pid in open_ports:
        process_name, process_path = get_process_info(pid)
        if not process_name and not process_path:
            remaining_ports.append(port)
        else:
            print(f"{port:<10} {process_name or '未知':<25} {process_path or '未知':<50}")

    if remaining_ports:
        print("\n剩余数据尝试再次查找\n")
        for port in remaining_ports:
            process_name, process_path = get_process_info_alternative(port)
            if not process_name and not process_path:
                process_name = "未知"
                process_path = "未知"
            print(f"{port:<10} {process_name:<25} {process_path:<50}")

if __name__ == "__main__":
    if is_admin():
        main()
        input()
    else:
        # 以管理员权限重新运行程序
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
