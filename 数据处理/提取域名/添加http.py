def add_https_www(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
            for line in infile:
                domain = line.strip()
                if domain:
                    url = f"https://www.{domain}"
                    outfile.write(url + '\n')
        print(f"已将域名处理后写入到 {output_file} 文件中。")
    except Exception as e:
        print(f"处理文件时出错: {e}")

if __name__ == "__main__":
    input_file = "out.txt"  # 输入文件路径
    output_file = "outurl.txt"  # 输出文件路径
    add_https_www(input_file, output_file)
