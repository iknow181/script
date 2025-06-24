import os
import shutil
import magic
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import tempfile

# MIME 类型到扩展名的映射
MIME_TO_EXT = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "text/plain": ".txt",
    "application/zip": ".zip",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/msword": ".doc",
    "application/vnd.ms-excel": ".xls",
    "application/octet-stream": ".bin",  # 默认二进制
}

def detect_and_rename_file(filepath, text_widget=None):
    try:
        # 拷贝到临时路径解决中文路径兼容问题
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copy(filepath, temp_file.name)
            mime = magic.from_file(temp_file.name, mime=True)
            description = magic.from_file(temp_file.name)
        os.unlink(temp_file.name)  # 删除临时文件

        recommended_ext = MIME_TO_EXT.get(mime)
        current_ext = os.path.splitext(filepath)[1]

        if not recommended_ext:
            log_msg = f"⚠️ 跳过: 未知MIME类型 {mime} - {filepath}\n"
        elif current_ext.lower() == recommended_ext:
            log_msg = f"✅ 跳过: 后缀已正确 - {filepath}\n"
        else:
            new_path = filepath + recommended_ext if not current_ext else filepath.replace(current_ext, recommended_ext)
            os.rename(filepath, new_path)
            log_msg = f"✅ 修改: {filepath} → {new_path}（{description}）\n"

    except Exception as e:
        log_msg = f"❌ 错误: 无法处理 {filepath}: {e}\n"

    if text_widget:
        text_widget.insert(tk.END, log_msg)
        text_widget.see(tk.END)

def process_folder(folder_path, text_widget=None):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            detect_and_rename_file(full_path, text_widget)

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
    process_folder(folder_path, log_text)
    messagebox.showinfo("完成", "批量识别并修改扩展名完成！")

# GUI 初始化
root = tk.Tk()
root.title("批量识别文件类型并添加扩展名")
root.geometry("800x500")

folder_label = tk.Label(root, text="选择文件夹：")
folder_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

folder_entry = tk.Entry(root, width=70)
folder_entry.grid(row=0, column=1, padx=10, pady=10)

folder_button = tk.Button(root, text="浏览", command=select_folder)
folder_button.grid(row=0, column=2, padx=10, pady=10)

start_button = tk.Button(root, text="开始识别并改名", command=start_processing, bg="green", fg="white")
start_button.grid(row=1, column=1, pady=10)

log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=25)
log_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()
