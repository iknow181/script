import os
import csv
import pandas as pd
import ijson

def sanitize_excel_value(value):
    """去除非法字符"""
    if isinstance(value, str):
        # 去除 Excel 不允许的非法字符
        value = ''.join([c if ord(c) >= 32 and ord(c) <= 127 else '' for c in value])
    return value

def write_chunk(chunk, fieldnames, output_dir, file_index):
    """
    将 CSV 切块写入 Excel 格式，并清理非法字符
    """
    filename = os.path.join(output_dir, f'chunk_{file_index}.csv')
    excel_path = filename.replace('.csv', '.xlsx')

    # 写入 CSV 文件
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for item in chunk:
            try:
                writer.writerow(item)
            except Exception as e:
                print(f"⚠️ 跳过一条记录写入 CSV：{e}")

    # 读入 CSV，清理非法字符并写入 Excel
    try:
        df = pd.read_csv(filename, low_memory=False)
        # 使用 map 替代 applymap 来清理字符
        df = df.apply(lambda col: col.map(sanitize_excel_value) if col.dtype == 'object' else col)
        df.to_excel(excel_path, index=False)
        print(f"📄 成功写入：{excel_path}")
    except Exception as e:
        print(f"❌ 写入 Excel 失败：{excel_path}，错误信息：{e}")

def json_to_csv_chunks(json_path, output_dir, batch_size=10000, progress_step=1000):
    """
    将 JSON 文件分块写入多个 CSV 文件，并最终转换为 Excel 文件
    """
    fieldnames = set()
    batch = []
    total = 0
    file_index = 0

    # 第一次扫描，收集所有字段名
    print("📋 正在扫描字段...")
    with open(json_path, 'rb') as f:
        for idx, item in enumerate(ijson.items(f, 'item')):
            if isinstance(item, dict):
                fieldnames.update(item.keys())
            if idx >= 1000:  # 扫描前1000条就够了
                break

    fieldnames = list(fieldnames)
    print(f"✅ 检测到字段数：{len(fieldnames)}")

    # 第二次正式写入 CSV
    print("📂 正在处理数据并写入 CSV 文件...")
    with open(json_path, 'rb') as f:
        for idx, item in enumerate(ijson.items(f, 'item')):
            batch.append(item)
            total += 1

            if total % batch_size == 0:
                print(f"✅ 已处理 {total} 条记录...")
                write_chunk(batch, fieldnames, output_dir, file_index)
                file_index += 1
                batch.clear()

            if total % progress_step == 0:
                print(f"⚙️ 进度：已处理 {total} 条记录...")

        # 处理剩余数据
        if batch:
            write_chunk(batch, fieldnames, output_dir, file_index)

    print(f"🎉 总共成功写入 {total} 条记录到 CSV 并分块为多个文件：{output_dir}")

# 示例用法
json_file = "tickets1.json"        # 替换为你的 JSON 路径
output_dir = "output"              # 输出目录

os.makedirs(output_dir, exist_ok=True)
json_to_csv_chunks(json_file, output_dir, batch_size=50000, progress_step=10000)
