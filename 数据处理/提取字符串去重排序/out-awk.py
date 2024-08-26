# 打开文件并读取内容
with open('output.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 去重并按长度排序
lines = sorted(set(lines), key=lambda x: (len(x), x))

# 写入结果到文件
with open('output.txt', 'w', encoding='utf-8') as file:
    file.writelines(lines)

print("文本去重并按长度排序完成，并已更新到output.txt文件中。")
