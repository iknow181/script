import re


def extract_domains_from_file(input_file, output_file):
    domains = set()
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as file:  # 使用UTF-8编码并忽略解码错误
        for line in file:
            # 使用正则表达式匹配域名
            matches = re.findall(
                r'(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}|(?:\d{1,3}\.){3}\d{1,3})', line)
            domains.update(matches)

    # 将提取到的域名写入到输出文件中
    with open(output_file, 'w') as out_file:
        for domain in domains:
            out_file.write(domain + '\n')


if __name__ == "__main__":
    input_file = "input.txt"  # 替换为你的输入文件路径
    output_file = "out.txt"  # 替换为输出文件路径
    extract_domains_from_file(input_file, output_file)
    print("提取的域名已写入到out.txt中。")
