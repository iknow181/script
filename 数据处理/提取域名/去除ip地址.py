import re

def remove_ips_and_sort_domains(input_file, output_file):
    domains = set()
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            # 使用正则表达式匹配域名，并去除IP地址
            matches = re.findall(r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.[a-zA-Z]{2,})', line)
            domains.update(matches)

    # 将域名排序后写入到输出文件中
    with open(output_file, 'w') as out_file:
        for domain in sorted(domains):
            out_file.write(domain + '\n')

if __name__ == "__main__":
    input_file = "out.txt"  # 替换为你的输入文件路径
    output_file = "out_sorted_unique_domains.txt"  # 替换为输出文件路径
    remove_ips_and_sort_domains(input_file, output_file)
    print("去除重复并排序后的域名已写入到out_sorted_unique_domains.txt中。")
