import os
import json

def merge_json_files(input_dir, output_file):
    merged_data = []
    total_before_merge = 0
    file_count = 0

    print("📦 正在读取 JSON 文件...\n")

    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(input_dir, filename)
            file_count += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    if isinstance(data, list):
                        merged_data.extend(data)
                        count = len(data)
                    else:
                        merged_data.append(data)
                        count = 1

                    total_before_merge += count
                    print(f"✅ 读取 {filename}：{count} 项")
            except Exception as e:
                print(f"❌ 读取 {filename} 时出错: {e}")

    print("\n📊 统计信息：")
    print(f"读取文件总数：{file_count}")
    print(f"合并前总对象数：{total_before_merge}")
    print(f"合并后对象数：{len(merged_data)}")

    # 写入合并后的结果
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=4)
        print(f"\n💾 已保存合并结果到：{output_file}")
    except Exception as e:
        print(f"❌ 写入合并文件时出错: {e}")

# 示例用法
if __name__ == '__main__':
    input_directory = './xxx'  # JSON 文件夹路径
    output_json = './xxx.json'     # 输出路径
    merge_json_files(input_directory, output_json)
