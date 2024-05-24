import requests
import json
from concurrent.futures import ThreadPoolExecutor


def get_c(ip):
    print(f"正在收集 {ip}")
    url = f"http://api.webscan.cc/?action=query&ip={ip}"
    try:
        req = requests.get(url=url)
        req.raise_for_status()
        data = req.json()
        if data:
            results = [f"{ip}\n"]
            for entry in data:
                result_line = f"\t{entry['domain']} {entry['title']}\n"
                results.append(result_line)
                print(f"     [+] {entry['domain']} {entry['title']} [+]")
            return results
    except requests.RequestException as e:
        print(f"请求失败 {ip}: {e}")
    except json.JSONDecodeError:
        print(f"解析响应失败 {ip}")
    return []


def get_ips(ip):
    iplist = []
    ips_str = ip[:ip.rfind('.')]
    for i in range(1, 256):
        ipadd = f"{ips_str}.{i}"
        iplist.append(ipadd)
    return iplist


def main():
    ip = input("请你输入要查询的ip: ")
    ips = get_ips(ip)

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(get_c, ips))

    with open("resulit.txt", 'a', encoding='utf-8') as f:
        for result in results:
            if result:
                f.writelines(result)


if __name__ == "__main__":
    main()
