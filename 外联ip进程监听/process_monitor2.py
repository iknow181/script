import psutil
import argparse
import threading
import signal
import sys
from colorama import Fore, Back, Style, init

# 初始化颜色
init()

# 添加一个全局变量用于终止标志
terminate_flag = False


def signal_handler(sig, frame):
    global terminate_flag
    terminate_flag = True
    print("\n监控已终止")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def get_process_info(pid):
    """
    获取指定进程 ID 的进程名称、可执行路径和启动参数。
    :param pid: 进程 ID
    :return: 进程名称、可执行路径和启动参数
    """
    try:
        proc = psutil.Process(pid)
        name = proc.name()
        exe = proc.exe()
        cmdline = proc.cmdline()
        return name, exe, cmdline
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None, None, None


def list_children(pid):
    """
    列出指定进程的所有子进程 ID。
    :param pid: 进程 ID
    :return: 子进程 ID 列表
    """
    try:
        proc = psutil.Process(pid)
        children = proc.children(recursive=True)
        return [p.pid for p in children]
    except psutil.NoSuchProcess:
        return []


def list_parent(pid):
    """
    获取指定进程的父进程 ID。
    :param pid: 进程 ID
    :return: 父进程 ID
    """
    try:
        proc = psutil.Process(pid)
        return proc.ppid()
    except psutil.NoSuchProcess:
        return None


def format_name(name):
    """
    格式化进程名称，使其居中并用 || 填充。
    :param name: 进程名称
    :return: 格式化后的进程名称
    """
    return name if name else "未知"


def monitor(ip=None, port=None, all_ip=False):
    """
    监控指定 IP 地址、端口上的进程或所有与本机通信的进程。
    :param ip: 目标 IP 地址（可选）
    :param port: 目标端口（可选）
    :param all_ip: 是否列出所有与本机通信的 IP 的进程
    """
    global terminate_flag
    seen_processes = set()  # 用于跟踪已输出的进程 ID

    while not terminate_flag:
        for conn in psutil.net_connections(kind='inet'):
            # 检查 IP 或端口条件
            if (all_ip or (ip and conn.raddr and conn.raddr[0] == ip) or (port and conn.laddr.port == port)):
                pid = conn.pid
                if pid and pid not in seen_processes:
                    name, exe, cmdline = get_process_info(pid)
                    parent_pid = list_parent(pid)
                    children_pids = list_children(pid)

                    output = f"{Fore.BLUE + Back.GREEN + '[info]' + Style.RESET_ALL} 进程 PID: {pid}\n"
                    output += f"{Fore.BLUE + Back.GREEN + '[info]' + Style.RESET_ALL} 进程名称:   {Fore.RED + format_name(name) + Style.RESET_ALL}\n"
                    output += f"{Fore.BLUE + Back.GREEN + '[info]' + Style.RESET_ALL} 可执行路径: {exe}\n"
                    output += f"{Fore.BLUE + Back.GREEN + '[info]' + Style.RESET_ALL} 启动参数: {' '.join(cmdline) if cmdline else '无'}\n"

                    if parent_pid:
                        parent_name, parent_exe, parent_cmdline = get_process_info(parent_pid)
                        output += f"{Fore.BLUE + Back.GREEN + '[info]' + Style.RESET_ALL} 父进程 PID: {parent_pid}\n"
                        output += f"{Fore.BLUE + Back.GREEN + '[info]' + Style.RESET_ALL} 父进程名称: {Fore.RED + format_name(parent_name) + Style.RESET_ALL}\n"
                        output += f"{Fore.BLUE + Back.GREEN + '[info]' + Style.RESET_ALL} 父进程可执行路径: {parent_exe}\n"
                        output += f"{Fore.BLUE + Back.GREEN + '[info]' + Style.RESET_ALL} 父进程启动参数: {' '.join(parent_cmdline) if parent_cmdline else '无'}\n"

                    if children_pids:
                        output += f"{Fore.BLUE + Back.GREEN + '[info]' + Style.RESET_ALL} 子进程列表：\n"
                        for child_pid in children_pids:
                            child_name, child_exe, child_cmdline = get_process_info(child_pid)
                            output += f"{Fore.BLUE + Back.GREEN + '[info]' + Style.RESET_ALL}   子进程 PID: {child_pid}\n"
                            output += f"{Fore.BLUE + Back.GREEN + '[info]' + Style.RESET_ALL}   子进程名称: {Fore.RED + format_name(child_name) + Style.RESET_ALL}\n"
                            output += f"{Fore.BLUE + Back.GREEN + '[info]' + Style.RESET_ALL}   子进程可执行路径: {child_exe}\n"
                            output += f"{Fore.BLUE + Back.GREEN + '[info]' + Style.RESET_ALL}   子进程启动参数: {' '.join(child_cmdline) if child_cmdline else '无'}\n"

                    output += "--------------------------------------------------------------------------------------------------------\n"
                    print(output)
                    seen_processes.add(pid)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="根据 IP、端口或所有 IP 监控进程。")
    parser.add_argument('-ip', type=str, help="要监控的 IP 地址")
    parser.add_argument('-p', type=int, help="要监控的端口")
    parser.add_argument('-a', action='store_true', help="列出所有与本机通信的 IP 的进程")
    args = parser.parse_args()

    monitor_thread = threading.Thread(target=monitor, args=(args.ip, args.p, args.a))
    monitor_thread.daemon = True
    monitor_thread.start()

    # 保持主线程运行
    try:
        while True:
            pass
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
