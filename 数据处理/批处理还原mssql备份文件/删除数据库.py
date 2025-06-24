import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import pyodbc

# 获取本地 SQL Server 实例（使用 sqlcmd）
def get_local_instances():
    try:
        result = subprocess.run(["sqlcmd", "-L"], capture_output=True, text=True, timeout=10)
        lines = result.stdout.splitlines()
        instances = []
        found = False
        for line in lines:
            line = line.strip()
            if found and line:
                instances.append(line)
            if "Available Servers" in line:
                found = True
        return instances if instances else ["(localdb)\\MSSQLLocalDB"]
    except Exception as e:
        print(f"无法获取实例列表: {e}")
        return ["(localdb)\\MSSQLLocalDB"]

# 获取实例下所有数据库
def get_databases(instance_name):
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={instance_name};"
            f"Trusted_Connection=yes;",
            timeout=5
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, state_desc,
                (SELECT SUM(size)*8/1024 FROM sys.master_files WHERE db_name(database_id) = name) AS size_MB
            FROM sys.databases
            WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')
        """)
        return cursor.fetchall()
    except Exception as e:
        messagebox.showerror("连接错误", f"无法连接实例 {instance_name}\n错误信息: {e}")
        return []

# 删除数据库
def delete_database(instance, db_name):
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={instance};"
            f"Trusted_Connection=yes;",
            autocommit=True
        )
        cursor = conn.cursor()

        # 强制 SINGLE_USER 模式
        cursor.execute(f"ALTER DATABASE [{db_name}] SET OFFLINE WITH ROLLBACK IMMEDIATE")
        cursor.execute(f"ALTER DATABASE [{db_name}] SET ONLINE")  # 必须在线才能 DROP
        cursor.execute(f"DROP DATABASE [{db_name}]")
        return True
    except Exception as e:
        # 尝试执行 sp_detach_db 作为备选方案
        try:
            cursor.execute(f"EXEC sp_detach_db '{db_name}', 'true'")
            return True
        except:
            print(f"彻底删除 {db_name} 失败: {e}")
            return False


# GUI 构建
class DatabaseManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Server 数据库管理器")

        # 实例列表手动写入避免超时
        self.instances = ["localhost", "(localdb)\\MSSQLLocalDB", ".\\SQLEXPRESS"]

        ttk.Label(root, text="选择 SQL 实例：").pack(pady=5)
        self.instance_var = tk.StringVar()
        self.instance_combo = ttk.Combobox(root, values=self.instances, textvariable=self.instance_var, width=50)
        self.instance_combo.pack()
        self.instance_combo.current(0)

        ttk.Button(root, text="加载数据库", command=self.load_databases).pack(pady=5)

        self.tree = ttk.Treeview(root, columns=("名称", "状态", "大小(MB)"), show="headings", selectmode="extended", height=15)
        for col in ("名称", "状态", "大小(MB)"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)
        self.tree.pack(padx=10, pady=5)

        ttk.Button(root, text="删除选中数据库", command=self.delete_selected).pack(pady=10)

    def load_databases(self):
        self.tree.delete(*self.tree.get_children())
        instance = self.instance_var.get().strip()
        dbs = get_databases(instance)
        for db in dbs:
            name, state, size = db
            self.tree.insert("", tk.END, values=(name, state, size if size else 0))

    def delete_selected(self):
        instance = self.instance_var.get().strip()
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("未选择", "请选择要删除的数据库")
            return

        confirm = messagebox.askyesno("确认删除", "确定要删除选中的数据库吗？此操作不可恢复！")
        if not confirm:
            return

        success = []
        fail = []

        for item in selected_items:
            db_name = self.tree.item(item, "values")[0]
            if delete_database(instance, db_name):
                success.append(db_name)
            else:
                fail.append(db_name)

        self.load_databases()
        message = ""
        if success:
            message += f"✅ 成功删除: {', '.join(success)}\n"
        if fail:
            message += f"❌ 删除失败: {', '.join(fail)}"
        messagebox.showinfo("结果", message)

# 运行 GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseManagerApp(root)
    root.mainloop()
