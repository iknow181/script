import re

# 定义正则表达式模式
pattern = r'\b[a-zA-Z0-9]+\b'

# 打开输入文件
with open('test.xml', 'r', encoding='utf-8') as infile:
    # 读取文件内容
    content = infile.read()

# 使用正则表达式查找关键字
keywords = re.findall(pattern, content)

# 打开输出文件
with open('output.txt', 'w', encoding='utf-8') as outfile:
    # 将提取的关键字写入输出文件
    for keyword in keywords:
        outfile.write(keyword + '\n')

print("提取完成，结果已保存到 output.txt 文件中。")
