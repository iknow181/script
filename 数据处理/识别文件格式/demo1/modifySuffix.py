import os
import tkinter as tk
from tkinter import filedialog, messagebox

def modify_file_extension(path, old_ext, new_ext):
    # 规范一下 old_ext 和 new_ext，保证都是小写且带点或者空字符串
    old_ext = old_ext.lower()
    new_ext = new_ext if new_ext.startswith('.') else '.' + new_ext

    for root, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            name, ext = os.path.splitext(file)
            ext = ext.lower()

            # 判断条件：
            # 1. 如果 old_ext 为空字符串，匹配无后缀文件（ext == ""）
            # 2. 否则匹配 ext == old_ext
            if (old_ext == "" and ext == "") or (ext == old_ext):
                new_file = os.path.join(root, name + new_ext)
                try:
                    os.rename(full_path, new_file)
                    print(f"重命名: {full_path} -> {new_file}")
                except Exception as e:
                    print(f"重命名失败: {full_path}，错误: {e}")
    messagebox.showinfo("成功", "文件扩展名修改成功！")

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)

def start_modification():
    folder_path = folder_entry.get()
    old_ext = old_ext_entry.get().strip().lower()
    new_ext = new_ext_entry.get().strip()

    if not folder_path or new_ext == "":
        messagebox.showwarning("警告", "文件夹和新扩展名必须填写")
        return

    # old_ext可以为空，代表匹配无后缀文件，new_ext必须有
    if old_ext and not old_ext.startswith("."):
        old_ext = "." + old_ext
    if not new_ext.startswith("."):
        new_ext = "." + new_ext

    modify_file_extension(folder_path, old_ext, new_ext)

root = tk.Tk()
root.title("批量修改文件扩展名")

folder_label = tk.Label(root, text="选择文件夹：")
folder_label.grid(row=0, column=0, padx=10, pady=10)
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=0, column=1, padx=10, pady=10)
folder_button = tk.Button(root, text="浏览", command=select_folder)
folder_button.grid(row=0, column=2, padx=10, pady=10)

old_ext_label = tk.Label(root, text="当前扩展名（无后缀留空）：")
old_ext_label.grid(row=1, column=0, padx=10, pady=10)
old_ext_entry = tk.Entry(root, width=20)
old_ext_entry.grid(row=1, column=1, padx=10, pady=10)

new_ext_label = tk.Label(root, text="新扩展名（例如：.pdf）：")
new_ext_label.grid(row=2, column=0, padx=10, pady=10)
new_ext_entry = tk.Entry(root, width=20)
new_ext_entry.grid(row=2, column=1, padx=10, pady=10)

start_button = tk.Button(root, text="开始修改", command=start_modification)
start_button.grid(row=3, column=1, padx=10, pady=10)

root.mainloop()
