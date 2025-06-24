
import pandas as pd

# 读取老数据工作表
old_data_df = pd.read_excel('合并.xlsx', sheet_name='老数据')

# 读取test1工作表
test1_df = pd.read_excel('合并.xlsx', sheet_name='test1')

# 获取老数据中的泄露地址集合（注意老数据中的列名是"获取地址"）
old_leak_urls = set(old_data_df['获取地址'].dropna().unique())

# 从test1中筛选出不重复的记录
unique_test1_df = test1_df[~test1_df['泄露地址'].isin(old_leak_urls)]

# 输出结果
print(f"原始test1记录数: {len(test1_df)}")
print(f"去重后test1记录数: {len(unique_test1_df)}")
print(f"删除的重复记录数: {len(test1_df) - len(unique_test1_df)}")

# 如果需要保存结果，可以取消下面的注释
unique_test1_df.to_excel('test1_去重后.xlsx', index=False)

