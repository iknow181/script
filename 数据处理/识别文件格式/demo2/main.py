import os
import shutil
import magic
import time
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from collections import defaultdict

# MIME类型 → 扩展名映射表
MIME_TO_EXT = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "text/plain": ".txt",
    "application/zip": ".zip",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/octet-stream": ".bin",
}

# 全局状态统计
total_count = 0
success_count = 0
skip_count = 0
fail_count = 0
mime_counter = defaultdict(int)

def detect_and_rename_file(filepath, text_widget=None):
    global success_count, skip_count, fail_count, mime_counter

    try:
        # 临时文件处理中文路径兼容
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copy(filepath, temp_file.name)
            mime = magic.from_file(temp_file.name, mime=True)
            description = magic.from_file(temp_file.name)
        os.unlink(temp_file.name)

        mime_counter[mime] += 1
        recommended_ext = MIME_TO_EXT.get(mime)
        current_ext = os.path.splitext(filepath)[1]

        if not recommended_ext:
            skip_count += 1
            log_msg = f"⚠️ 跳过: 未知MIME类型 {mime} - {filepath}\n"
        elif current_ext.lower() == recommended_ext:
            skip_count += 1
            log_msg = f"✅ 跳过: 后缀已正确 - {filepath}\n"
        else:
            new_path = filepath + recommended_ext if not current_ext else filepath.replace(current_ext, recommended_ext)
            os.rename(filepath, new_path)
            success_count += 1
            log_msg = f"✅ 修改: {filepath} → {new_path}（{description}）\n"

    except Exception as e:
        fail_count += 1
        log_msg = f"❌ 错误: 无法处理 {filepath}: {e}\n"

    if text_widget:
        text_widget.insert(tk.END, log_msg)
        text_widget.see(tk.END)

def process_folder(folder_path, text_widget=None, root_widget=None):
    global total_count, success_count, skip_count, fail_count, mime_counter
    total_count = success_count = skip_count = fail_count = 0
    mime_counter.clear()

    file_list = []
    for root_dir, _, files in os.walk(folder_path):
        for file in files:
            file_list.append(os.path.join(root_dir, file))

    total_count = len(file_list)
    start_time = time.time()

    progress_bar["maximum"] = total_count
    progress_bar["value"] = 0

    for i, file_path in enumerate(file_list, 1):
        detect_and_rename_file(file_path, text_widget)
        progress_bar["value"] = i
        if root_widget:
            root_widget.update_idletasks()

    elapsed = time.time() - start_time

    # 输出 MIME 类型统计
    type_summary_text.delete(1.0, tk.END)
    for mime_type, count in sorted(mime_counter.items(), key=lambda x: -x[1]):
        type_summary_text.insert(tk.END, f"{mime_type}: {count} 个\n")

    # 总结信息
    summary = (
        f"\n处理完成 ✅\n"
        f"总文件数: {total_count}\n"
        f"成功修改: {success_count}\n"
        f"跳过文件: {skip_count}\n"
        f"失败处理: {fail_count}\n"
        f"耗时: {elapsed:.2f} 秒\n"
    )
    if text_widget:
        text_widget.insert(tk.END, summary)
        text_widget.see(tk.END)

    messagebox.showinfo("完成", summary)

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)

def start_processing():
    folder_path = folder_entry.get()
    if not folder_path:
        messagebox.showwarning("警告", "请选择文件夹路径！")
        return
    log_text.delete(1.0, tk.END)
    type_summary_text.delete(1.0, tk.END)
    process_folder(folder_path, log_text, root)

# ------------------- GUI 布局 -------------------
root = tk.Tk()
root.title("批量识别文件类型并修改扩展名")
root.geometry("900x650")

folder_label = tk.Label(root, text="选择文件夹：")
folder_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

folder_entry = tk.Entry(root, width=70)
folder_entry.grid(row=0, column=1, padx=10, pady=10)

folder_button = tk.Button(root, text="浏览", command=select_folder)
folder_button.grid(row=0, column=2, padx=10, pady=10)

start_button = tk.Button(root, text="开始识别并改名", command=start_processing, bg="green", fg="white")
start_button.grid(row=1, column=1, pady=10)

progress_bar = ttk.Progressbar(root, length=700, mode='determinate')
progress_bar.grid(row=2, column=0, columnspan=3, padx=10, pady=5)

log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=120, height=20)
log_text.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

type_summary_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=120, height=8, bg="#f0f0f0")
type_summary_text.grid(row=4, column=0, columnspan=3, padx=10, pady=5)
type_summary_text.insert(tk.END, "文件类型统计将在处理完成后显示...\n")

root.mainloop()
