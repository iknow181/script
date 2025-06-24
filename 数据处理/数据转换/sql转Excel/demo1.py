import re
import pandas as pd
from collections import defaultdict
import ast
import os

def parse_create_table_blocks(sql_text):
    pattern = re.compile(r"CREATE TABLE\s+`(\w+)`\s*\((.*?)\);", re.DOTALL)
    table_fields = {}
    for table_name, body in pattern.findall(sql_text):
        fields = re.findall(r"`(\w+)`", body)
        table_fields[table_name] = fields
    return table_fields

def parse_insert_statements(sql_path):
    buffer = ''
    table_inserts = defaultdict(list)
    with open(sql_path, 'r', encoding='utf-8', errors='ignore') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            buffer += chunk
            while True:
                match = re.search(r"INSERT INTO\s+`?(\w+)`?\s+VALUES\s*(\(.*?\));", buffer, re.DOTALL)
                if not match:
                    break
                table, values_block = match.groups()
                full_stmt = match.group(0)
                buffer = buffer[len(full_stmt):]
                table_inserts[table].append(values_block)
    return table_inserts

def clean_values_block(block_text):
    text = block_text.strip()
    if not text.startswith('('):
        return []
    try:
        values = ast.literal_eval(f"[{text}]")
        return values
    except Exception as e:
        print(f"❌ 解析失败：{str(e)}\n原始内容片段：{text[:100]}...\n")
        return []

def convert_sql_to_separate_excels(sql_path, output_dir):
    print(f"📥 开始处理 SQL 文件：{sql_path}")
    with open(sql_path, 'r', encoding='utf-8', errors='ignore') as f:
        sql_text = f.read()

    print("🔍 正在提取表结构...")
    table_fields = parse_create_table_blocks(sql_text)

    print("📦 正在解析 INSERT INTO 数据...")
    table_inserts = parse_insert_statements(sql_path)

    os.makedirs(output_dir, exist_ok=True)

    for table, values_list in table_inserts.items():
        print(f"  📄 正在处理表 {table}，共 {len(values_list)} 条语句...")
        all_rows = []
        for raw_block in values_list:
            rows = clean_values_block(raw_block)
            all_rows.extend(rows)

        columns = table_fields.get(table)
        if not columns:
            print(f"⚠️ 警告：未找到表 `{table}` 的字段定义，跳过导出。")
            continue

        if all_rows:
            fixed_rows = [row if isinstance(row, tuple) else tuple([row]) for row in all_rows]
            df = pd.DataFrame(fixed_rows, columns=columns[:len(fixed_rows[0])])
            output_path = os.path.join(output_dir, f"{table}.xlsx")
            df.to_excel(output_path, index=False)
            print(f"    ✔️ 表 `{table}` 数据已保存至：{output_path}")
        else:
            print(f"⚠️ 表 `{table}` 无有效数据，跳过。")

    print(f"\n✅ 全部表导出完成，文件保存至目录：{output_dir}")

# 使用示例，替换为你实际路径
convert_sql_to_separate_excels(
    r"test.txt",
    r"sql_tables_output"
)
