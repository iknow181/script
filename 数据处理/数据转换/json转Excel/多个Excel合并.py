import os
import pandas as pd


def merge_excel_files_in_batches(input_dir, output_file, batch_size=100000):
    # 获取输入目录下的所有 Excel 文件
    excel_files = [f for f in os.listdir(input_dir) if f.endswith('.xlsx')]
    excel_files.sort()  # 按照文件名排序，确保合并顺序正确

    # 设定 Excel writer
    writer = pd.ExcelWriter(output_file, engine='openpyxl')

    # 记录当前行数
    current_row = 0
    sheet_index = 0

    # 遍历所有文件
    for file in excel_files:
        file_path = os.path.join(input_dir, file)
        try:
            print(f"📂 正在读取文件：{file}")
            # 读取数据
            df = pd.read_excel(file_path)

            # 如果当前批次超过了预设的大小，将当前数据保存为新的工作表
            if current_row + len(df) > batch_size:
                sheet_index += 1
                current_row = 0  # 重置当前行数
                print(f"💾 新工作表：sheet_{sheet_index}")

            # 将数据写入当前工作表
            df.to_excel(writer, sheet_name=f"sheet_{sheet_index}", index=False, startrow=current_row)
            current_row += len(df)
        except Exception as e:
            print(f"❌ 无法读取文件 {file}，错误信息：{e}")

    # 保存到最终文件
    writer.save()
    print(f"🎉 合并完成，文件保存为：{output_file}")


# 示例用法
input_dir = "output1"  # 输入文件夹，包含多个小的 Excel 文件
output_file = "output1\combined_final.xlsx"  # 最终合并后的 Excel 文件路径

merge_excel_files_in_batches(input_dir, output_file, batch_size=100000)
