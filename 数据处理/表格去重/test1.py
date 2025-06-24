import pandas as pd

# 读取 Excel 文件
file_path = "1.xlsx"  # 你的 Excel 文件路径
df = pd.read_excel(file_path)

# 去重，保留第一条出现的记录
df_unique = df.drop_duplicates()

# 保存去重后的数据
output_path = "../../ollamaApi/deduplicated_data.xlsx"
df_unique.to_excel(output_path, index=False)

print(f"去重后的数据已保存至 {output_path}")
