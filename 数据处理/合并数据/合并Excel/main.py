import pandas as pd
import os

# 设置要合并的 Excel 文件所在文件夹路径
folder_path = './excel'  # 你可以根据实际路径修改

# 获取文件夹中所有 .xlsx 文件
excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

# 初始化一个空的 DataFrame 用于合并
combined_df = pd.DataFrame()

# 遍历所有 Excel 文件
for file in excel_files:
    file_path = os.path.join(folder_path, file)

    # 读取 Excel 文件的第一个工作表
    try:
        df = pd.read_excel(file_path)
        # 合并到总表中，字段（列）一致会自动对齐
        combined_df = pd.concat([combined_df, df], ignore_index=True)
        print(f'合并成功：{file}')
    except Exception as e:
        print(f'读取失败：{file}，错误：{e}')

# 保存合并后的结果到新的 Excel 文件
output_path = os.path.join(folder_path, 'merged_result.xlsx')
combined_df.to_excel(output_path, index=False)
print(f'\n✅ 所有文件合并完成，结果保存至：{output_path}')
