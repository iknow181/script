def extract_valid_urls(input_file, output_file):
    valid_urls = set()

    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                fields = line.split(',')
                if len(fields) > 1:
                    status_code = fields[3].strip()
                    url = fields[1].strip()
                    if status_code == '301':
                        valid_urls.add(url)

        sorted_urls = sorted(valid_urls)

        with open(output_file, 'w', encoding='utf-8') as outfile:
            for url in sorted_urls:
                outfile.write(url + '\n')

        print(f"状态码为200的网站已写入到 {output_file} 文件中。")
    except Exception as e:
        print(f"处理文件时出错: {e}")

if __name__ == "__main__":
    input_file = "1.txt"  # 输入文件路径
    output_file = "valid_urls.txt"  # 输出文件路径
    extract_valid_urls(input_file, output_file)
