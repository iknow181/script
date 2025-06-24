import pandas as pd
from rapidfuzz import fuzz, process

# 读取两个 Excel 文件
data_df = pd.read_excel('数据.xlsx')
old_data_df = pd.read_excel('老数据.xlsx')

# 标准化字段名（确保一致）
data_df.columns = data_df.columns.str.strip()
old_data_df.columns = old_data_df.columns.str.strip()

# 字段名如下
addr_col = '泄露地址'
count_col = '数据量'
name_col = '数据泄露事件名称'

# 第一阶段：根据泄露地址精确匹配删除
filtered_df = data_df[~data_df[addr_col].isin(old_data_df[addr_col])].copy()

# 第二阶段：模糊匹配：事件名称 + 数据量
def is_duplicate(row, old_df):
    # 过滤数据量相同的记录
    same_count_df = old_df[old_df[count_col] == row[count_col]]
    for _, old_row in same_count_df.iterrows():
        name_similarity = fuzz.partial_ratio(str(row[name_col]), str(old_row[name_col]))
        if name_similarity >= 85:  # 设置相似度阈值
            return True
    return False

# 对每一行判断是否重复（模糊匹配）
final_df = filtered_df[~filtered_df.apply(lambda row: is_duplicate(row, old_data_df), axis=1)]

# 保存去重后的结果
final_df.to_excel('去重后数据.xlsx', index=False)
print(f"原始数据共 {len(data_df)} 条，去重后剩余 {len(final_df)} 条。")
