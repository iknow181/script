def extract_insert_statements(sql_path, output_path=None, max_count=10):
    buffer = ''
    collected = []
    count = 0
    inside_insert = False

    with open(sql_path, 'r', encoding='utf-8', errors='ignore') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break

            buffer += chunk
            while True:
                semicolon_pos = buffer.find(';')
                if semicolon_pos == -1:
                    break

                statement = buffer[:semicolon_pos + 1]
                buffer = buffer[semicolon_pos + 1:]

                if 'INSERT INTO' in statement.upper():
                    collected.append(statement.strip())
                    count += 1
                    if count >= max_count:
                        break

            if count >= max_count:
                break

    # 打印或保存结果
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as out:
            for stmt in collected:
                out.write(stmt + '\n\n')
        print(f"✅ 已保存前 {count} 条 INSERT INTO 语句到 {output_path}")
    else:
        for i, stmt in enumerate(collected, 1):
            print(f"\n--- 第 {i} 条 ---\n{stmt[:500]}...\n")

# 示例：提取前 5 条 INSERT INTO 语句
extract_insert_statements(
    r"xxx.txt",
    output_path=r"insert_preview.sql",
    max_count=5
)
