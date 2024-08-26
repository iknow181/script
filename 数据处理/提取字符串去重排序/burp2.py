import re

# 读取包含请求包和响应包的文件
with open('test.xml', 'r', encoding='utf-8') as file:
    packets = file.read()

# 定义正则表达式模式来匹配关键字
pattern = r'\b[\w-]+\b'

# 使用正则表达式匹配关键字
keywords = re.findall(pattern, packets)

# 去除重复的关键字
keywords = list(set(keywords))

# 将关键字写入爆破字典文件
with open('wordlist.txt', 'w', encoding='utf-8') as file:
    for keyword in keywords:
        file.write(keyword + '\n')
