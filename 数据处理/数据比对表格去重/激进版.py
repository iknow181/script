import pandas as pd
from rapidfuzz import process, fuzz

# === 加载数据 ===
data_df = pd.read_excel('数据.xlsx')
old_df = pd.read_excel('老数据.xlsx')

# === 字段设置 ===
addr_col = '泄露地址'
name_col = '数据泄露事件名称'

# === 提取老数据中的事件名称和泄露地址列表（作为匹配库）===
old_names = old_df[name_col].dropna().astype(str).tolist()
old_addrs = old_df[addr_col].dropna().astype(str).tolist()

# === 模糊匹配函数（快速匹配 + 限定得分）===
def is_duplicate_fast(name, addr):
    # 地址中是否包含在已有地址中（简单子串判断）
    for old_addr in old_addrs:
        if str(addr) in old_addr or old_addr in str(addr):
            return True, '地址模糊匹配'

    # 快速模糊匹配（只找最相近的一个）
    best_match, score, _ = process.extractOne(
        str(name), old_names, scorer=fuzz.token_set_ratio
    )
    if score >= 75:
        return True, f'事件名称相似度 {score}'
    return False, ''

# === 加速处理 ===
deleted_rows = []
retained_rows = []

for idx, row in data_df.iterrows():
    is_dup, reason = is_duplicate_fast(row[name_col], row[addr_col])
    if is_dup:
        row_data = row.to_dict()
        row_data["删除原因"] = reason
        deleted_rows.append(row_data)
    else:
        retained_rows.append(row)

# === 保存结果 ===
pd.DataFrame(retained_rows).to_excel("去重后数据_快速版.xlsx", index=False)
pd.DataFrame(deleted_rows).to_excel("验证报告_快速版.xlsx", index=False)

print(f"✅ 完成：共 {len(data_df)} 条，删除 {len(deleted_rows)} 条，保留 {len(retained_rows)} 条。")
