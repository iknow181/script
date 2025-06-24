import pandas as pd
from rapidfuzz import fuzz

# === 1. 加载数据 ===
df = pd.read_excel('最终合并.xlsx')

# === 2. 字段名称（根据你实际表格字段名称调整）===
name_col = '数据安全事件'
addr_col = '获取地址'
count_col = '涉及数据量'

# === 3. 判断数据量是否一致 ===
def equal_data_amount(a, b):
    """判断数据量是否一致（忽略空格、大小写）"""
    return str(a).strip().replace(" ", "").upper() == str(b).strip().replace(" ", "").upper()

# === 4. 初始化 ===
visited = set()
unique_rows = []
duplicate_rows = []

# === 5. 主循环：比对每一行 ===
for i in range(len(df)):
    if i in visited:
        continue

    row_i = df.iloc[i]
    current_group = [i]

    for j in range(i + 1, len(df)):
        if j in visited:
            continue

        row_j = df.iloc[j]
        # 提取字段
        addr_i = str(row_i[addr_col]).strip() if pd.notna(row_i[addr_col]) else ''
        addr_j = str(row_j[addr_col]).strip() if pd.notna(row_j[addr_col]) else ''

        # 条件1：泄露地址一致 + 数据量一致
        if addr_i and addr_j and addr_i == addr_j:
            if equal_data_amount(row_i[count_col], row_j[count_col]):
                current_group.append(j)
                dup_type = '地址重复+数据量一致'
                dup_row = df.iloc[j].to_dict()
                dup_row.update({
                    '重复参考索引': i,
                    '重复事件名称': row_i[name_col],
                    '相似度': fuzz.token_set_ratio(str(row_i[name_col]), str(row_j[name_col])),
                    '重复类型': dup_type
                })
                duplicate_rows.append(dup_row)
                continue

        # 条件2：事件名称相似 + 数据量一致
        name_sim = fuzz.token_set_ratio(str(row_i[name_col]), str(row_j[name_col]))
        if name_sim >= 90 and equal_data_amount(row_i[count_col], row_j[count_col]):
            current_group.append(j)
            dup_type = '名称相似+数据量一致'
            dup_row = df.iloc[j].to_dict()
            dup_row.update({
                '重复参考索引': i,
                '重复事件名称': row_i[name_col],
                '相似度': name_sim,
                '重复类型': dup_type
            })
            duplicate_rows.append(dup_row)
            continue

    # === 保留主记录 ===
    unique_rows.append(df.iloc[i].to_dict())
    visited.update(current_group)

# === 6. 保存结果 ===
pd.DataFrame(unique_rows).to_excel("最终合并_去重后.xlsx", index=False)
pd.DataFrame(duplicate_rows).to_excel("最终合并_重复记录报告.xlsx", index=False)

print(f"✅ 去重完成：原始 {len(df)} 条 → 保留 {len(unique_rows)} 条，重复记录 {len(duplicate_rows)} 条")
