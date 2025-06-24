import pandas as pd
from rapidfuzz import fuzz
import os

# === 加载数据 ===
data_df = pd.read_excel('数据.xlsx')
old_data_df = pd.read_excel('老数据.xlsx')

# === 字段名（请根据你表格实际列名调整）===
addr_col = '泄露地址'
count_col = '数据量'
name_col = '数据泄露事件名称'

# === 去重逻辑阶段一：泄露地址完全相同删除 ===
step1_df = data_df[~data_df[addr_col].isin(old_data_df[addr_col])].copy()

# === 存储匹配信息的临时列表 ===
matched_info = []

# === 去重逻辑阶段二：模糊匹配：事件名称 + 数据量 ===
def find_best_match(row, old_df):
    same_count_df = old_df[old_df[count_col] == row[count_col]]
    best_score = 0
    best_match = None

    for _, old_row in same_count_df.iterrows():
        score = fuzz.partial_ratio(str(row[name_col]), str(old_row[name_col]))
        if score > best_score:
            best_score = score
            best_match = old_row

    return best_match, best_score

# === 找出所有重复的记录并记录匹配情况 ===
final_rows = []
for _, row in step1_df.iterrows():
    match_row, score = find_best_match(row, old_data_df)
    if match_row is not None and score >= 80:
        matched_info.append({
            "原始事件名称": row[name_col],
            "原始数据量": row[count_col],
            "原始泄露地址": row[addr_col],
            "匹配事件名称": match_row[name_col],
            "匹配数据量": match_row[count_col],
            "匹配泄露地址": match_row[addr_col],
            "名称相似度": score,
        })
    else:
        final_rows.append(row)

# === 结果保存 ===
# 去重后数据
final_df = pd.DataFrame(final_rows)
final_df.to_excel('去重后数据2.xlsx', index=False)

# 被删除的数据验证报告
report_df = pd.DataFrame(matched_info)
report_df.to_excel('去重验证报告.xlsx', index=False)

print(f"✅ 去重完成：原始 {len(data_df)} 条，去重后 {len(final_df)} 条，删除 {len(matched_info)} 条")
print(f"📄 验证报告已生成：'去重验证报告.xlsx'")
