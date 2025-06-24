def fix_json_array_file(path):
  with open(path, 'rb+') as f:
    f.seek(-10, 2)  # 读取最后 10 字节
    end = f.read().strip()
    if not end.endswith(b']'):
      print("⚠️ JSON 结尾不完整，自动修复中...")
      f.seek(0, 2)
      f.write(b'\n]')
      print("✅ 修复完成！")
    else:
      print("✅ JSON 文件结构看起来没问题。")

fix_json_array_file("tickets2.json")