import os
import re
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

import docx
import PyPDF2
import openpyxl
import xlrd
from PIL import Image

def clean_text(text, max_len=30):
    return re.sub(r'[^\w\u4e00-\u9fff]+', '_', text).strip('_')[:max_len] or "摘要"

def read_txt(path):
    for enc in ['utf-8', 'gbk', 'utf-16', 'latin1']:
        try:
            with open(path, 'r', encoding=enc) as f:
                lines = f.readlines()[:3]
                return clean_text(' '.join(line.strip() for line in lines))
        except Exception:
            continue
    return None

def extract_summary(path: Path):
    suffix = path.suffix.lower()
    try:
        if suffix == '.pdf':
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ''.join((page.extract_text() or '') for page in reader.pages[:2])
                return clean_text(text)
        elif suffix == '.docx':
            doc = docx.Document(path)
            return clean_text(' '.join(p.text for p in doc.paragraphs[:3]))
        elif suffix == '.doc':
            return "doc文件"
        elif suffix == '.txt':
            return read_txt(path)
        elif suffix == '.csv':
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return clean_text(' '.join(next(f) for _ in range(3)))
        elif suffix == '.xlsx':
            wb = openpyxl.load_workbook(path, read_only=True)
            ws = wb.active
            cells = [str(cell.value) for row in ws.iter_rows(max_row=3, max_col=5) for cell in row if cell.value]
            return clean_text(' '.join(cells))
        elif suffix == '.xls':
            wb = xlrd.open_workbook(path)
            sheet = wb.sheet_by_index(0)
            cells = [str(sheet.cell_value(i, j)) for i in range(min(3, sheet.nrows)) for j in range(min(5, sheet.ncols))]
            return clean_text(' '.join(cells))
        elif suffix in ['.jpg', '.png']:
            with Image.open(path) as img:
                return f"{img.width}x{img.height}px"
    except Exception as e:
        print(f"[读取失败] {path}: {e}")
    return None

def rename_files_by_summary(root_dir, log_func):
    exts = ['.pdf', '.doc', '.docx', '.xlsx', '.xls', '.txt', '.csv', '.jpg', '.png']
    total = 0
    success = 0
    fail = 0

    for root, _, files in os.walk(root_dir):
        for fname in files:
            total += 1
            path = Path(root) / fname
            if path.suffix.lower() not in exts:
                continue

            try:
                summary = extract_summary(path)
                if not summary:
                    log_func(f"[跳过] {path.name}（内容为空或读取失败）")
                    fail += 1
                    continue

                new_base = summary
                new_path = path.with_name(f"{new_base}{path.suffix.lower()}")

                # 避免死循环，最多尝试 20 次
                for i in range(20):
                    if not new_path.exists():
                        break
                    new_path = path.with_name(f"{new_base}_{i+1}{path.suffix.lower()}")
                else:
                    log_func(f"[跳过] {path.name}（重命名冲突过多）")
                    fail += 1
                    continue

                path.rename(new_path)
                log_func(f"[重命名] {path.name} → {new_path.name}")
                success += 1

            except Exception as e:
                log_func(f"[异常] {path.name} 出错：{e}")
                fail += 1

    log_func(f"\n✅ 完成：总共处理 {total} 个文件，成功 {success}，失败 {fail}。\n")


# GUI构建
def start_gui():
    def select_folder():
        path = filedialog.askdirectory()
        if path:
            folder_var.set(path)

    def log(msg):
        output.insert(tk.END, msg + "\n")
        output.yview_moveto(1)

    def run_thread():
        path = folder_var.get()
        if not os.path.isdir(path):
            messagebox.showerror("错误", "请选择一个有效的文件夹")
            return
        run_btn.config(state=tk.DISABLED)
        threading.Thread(target=lambda: [rename_files_by_summary(path, log), run_btn.config(state=tk.NORMAL)]).start()

    win = tk.Tk()
    win.title("批量文件摘要重命名工具")
    win.geometry("700x500")

    tk.Label(win, text="选择待处理的文件夹:").pack(pady=5)
    frame = tk.Frame(win)
    frame.pack(pady=5)
    folder_var = tk.StringVar()
    tk.Entry(frame, textvariable=folder_var, width=60).pack(side=tk.LEFT, padx=5)
    tk.Button(frame, text="浏览", command=select_folder).pack(side=tk.LEFT)

    run_btn = tk.Button(win, text="开始重命名", command=run_thread, bg="#4CAF50", fg="white")
    run_btn.pack(pady=10)

    output = scrolledtext.ScrolledText(win, width=80, height=20)
    output.pack(pady=10)

    win.mainloop()

if __name__ == "__main__":
    start_gui()
