import magic
import sys
import os

def detect_file_type(filepath):
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return

    try:
        # 获取 MIME 类型（如 image/png、application/pdf）
        mime = magic.from_file(filepath, mime=True)

        # 获取详细类型描述（如 PNG image data, 1024 x 768, 8-bit/color）
        description = magic.from_file(filepath)

        print(f"📄 文件: {filepath}")
        print(f"📦 MIME类型: {mime}")
        print(f"🔍 类型描述: {description}")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python detect_file_type.py <文件路径>")
    else:
        detect_file_type(sys.argv[1])
