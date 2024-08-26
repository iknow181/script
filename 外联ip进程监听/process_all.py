import ctypes, sys
import subprocess
import re
import psutil

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_netstat_output():
    """运行 netstat -anob 命令并获取输出。"""
    result = subprocess.run(['netstat', '-anob'], capture_output=True, text=True)
    return result.stdout

def extract_external_connections(text):
    lines = text.splitlines()
    external_connections = []

    for i, line in enumerate(lines):
        if 'TCP' in line or 'UDP' in line:
            parts = line.split()
            if len(parts) >= 5:
                local_address = parts[1]
                remote_address = parts[2]
                state = parts[3] if 'TCP' in line else 'UDP'
                pid = parts[-1]

                # 检查是否为外联行为
                if not remote_address.startswith('127.0.0.1') and not remote_address.startswith('[::]:0') and not remote_address.startswith('0.0.0.0'):
                    try:
                        proc = psutil.Process(int(pid))
                        process_name = proc.name()
                        process_exe = proc.exe()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        process_name = "未知"
                        process_exe = "未知"
                    external_connections.append((local_address, remote_address, state, pid, process_name, process_exe))

    return external_connections

def main():
    # 获取 netstat 输出
    output = get_netstat_output()

    # 提取外联行为的进程信息
    external_connections = extract_external_connections(output)

    # 按进程名排序
    external_connections.sort(key=lambda x: x[4])

    # 合并相同进程名的行
    merged_connections = {}
    for local_address, remote_address, state, pid, process_name, process_exe in external_connections:
        if process_name not in merged_connections:
            merged_connections[process_name] = {
                'local_addresses': [],
                'remote_addresses': [],
                'states': [],
                'pids': [],
                'process_exe': process_exe,
                'remote_count': 0,
                'threat_level': 0
            }
        merged_connections[process_name]['local_addresses'].append(local_address)
        merged_connections[process_name]['remote_addresses'].append(remote_address)
        merged_connections[process_name]['states'].append(state)
        merged_connections[process_name]['pids'].append(pid)
        merged_connections[process_name]['remote_count'] += 1

    # 创建常见应用进程表单
    common_processes = ['360rp.exe', '360tray.exe', 'FlowUs.exe','TencentDocs.exe', 'WeChat.exe', 'msedge.exe','svchost.exe','wps.exe','wpscloudsvr.exe']  # 示例常见应用进程

    # 计算每个进程的威胁等级
    for process_name, info in merged_connections.items():
        if process_name not in common_processes:
            info['threat_level'] += 1
        if info['remote_count'] <= 3:
            info['threat_level'] += 1

    # 计算列宽
    max_local_address_len = max(len(conn[0]) for conn in external_connections)
    max_remote_address_len = max(len(conn[1]) for conn in external_connections)
    max_state_len = max(len(conn[2]) for conn in external_connections)
    max_pid_len = max(len(conn[3]) for conn in external_connections)
    max_process_name_len = max(len(conn[4]) for conn in external_connections)
    max_process_exe_len = max(len(conn[5]) for conn in external_connections)

    # 输出外联行为的进程信息
    print(f"{'进程名':<{max_process_name_len}} {'本地地址':<{max_local_address_len}} {'远程地址':<{max_remote_address_len}} {'状态':<{max_state_len}} {'PID':<{max_pid_len}} {'进程路径':<{max_process_exe_len}} {'威胁等级':<10}")
    print("=" * (max_process_name_len + max_local_address_len + max_remote_address_len + max_state_len + max_pid_len + max_process_exe_len + 20))
    for process_name, info in merged_connections.items():
        process_exe = info['process_exe']
        print(f"\n{process_exe:<{max_process_exe_len}}\n{process_name:<{max_process_name_len}}")
        for local_address, remote_address, state, pid in zip(info['local_addresses'], info['remote_addresses'], info['states'], info['pids']):
            print(f"{local_address:<{max_local_address_len}} {remote_address:<{max_remote_address_len}} {state:<{max_state_len}} {pid:<{max_pid_len}} {info['threat_level']:<10}")

    # 输出威胁等级和对应进程信息
    print("\n威胁等级和对应进程信息:")
    for process_name, info in merged_connections.items():
        print(f"进程名: {process_name}, 进程路径: {info['process_exe']}, 威胁等级: {info['threat_level']}")

if is_admin():
    main()
    input()
else:
    # 以管理员权限重新运行程序
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
