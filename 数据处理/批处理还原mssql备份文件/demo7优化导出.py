import os
import glob
import pyodbc
import pandas as pd
import time
import urllib
import shutil
from sqlalchemy import create_engine, text

bak_dir = r"test"
restore_data_dir = r"restore\mssql_data"
restore_log_dir = r"restore\mssql_logs"
export_dir = r"export_csv"

sql_instance = "localhost"
windows_user = os.getenv('USERNAME')
windows_domain = os.getenv('USERDOMAIN')
windows_login = f"{windows_domain}\\{windows_user}"

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={sql_instance};"
    f"Trusted_Connection=yes;"
)

def get_logical_names(bak_path):
    with pyodbc.connect(conn_str, autocommit=True) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"RESTORE FILELISTONLY FROM DISK = '{bak_path}'")
            files = cursor.fetchall()
            if not files:
                # 备份文件没有文件列表，认为非法备份
                raise ValueError("备份文件无内容")
            return [f[0] for f in files]
        except Exception as e:
            # 抛出异常给调用者判断处理
            raise RuntimeError(f"非备份文件或格式异常: {e}")

def wait_for_db_online(db_name, timeout=60):
    with pyodbc.connect(conn_str, autocommit=True) as conn:
        cursor = conn.cursor()
        elapsed = 0
        interval = 2
        while elapsed < timeout:
            cursor.execute("SELECT state_desc FROM sys.databases WHERE name = ?", db_name)
            row = cursor.fetchone()
            if row and row[0] == "ONLINE":
                return True
            time.sleep(interval)
            elapsed += interval
        return False

def recover_restoring_databases():
    """检测并恢复处于 'RESTORING' 状态的数据库"""
    with pyodbc.connect(conn_str, autocommit=True) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, state_desc FROM sys.databases WHERE state_desc = 'RESTORING'")
        rows = cursor.fetchall()
        for db_name, _ in rows:
            try:
                print(f"检测到正在还原的数据库：{db_name}，执行恢复...")
                cursor.execute(f"RESTORE DATABASE [{db_name}] WITH RECOVERY")
                print(f"数据库 {db_name} 恢复完成")
            except Exception as e:
                print(f"恢复数据库 {db_name} 失败: {e}")

def restore_database(bak_path, db_name, logical_names):
    os.makedirs(restore_data_dir, exist_ok=True)
    os.makedirs(restore_log_dir, exist_ok=True)
    with pyodbc.connect(conn_str, autocommit=True) as conn:
        cursor = conn.cursor()
        move_clauses = []
        for logical in logical_names:
            # 判断是否为日志文件（一般逻辑名带log）
            if logical.lower().endswith('_log') or 'log' in logical.lower():
                # 给每个日志文件分配不同的ldf路径
                physical_path = os.path.join(restore_log_dir, f"{db_name}_{logical}.ldf")
            else:
                # 给每个数据文件分配不同的mdf路径
                physical_path = os.path.join(restore_data_dir, f"{db_name}_{logical}.mdf")
            move_clauses.append(f" MOVE '{logical}' TO '{physical_path}' ")
        move_clause_str = ",".join(move_clauses)

        restore_sql = f"""
            RESTORE DATABASE [{db_name}] FROM DISK = '{bak_path}'
            WITH REPLACE, RECOVERY, {move_clause_str}
        """
        print(f"开始还原数据库 {db_name} ...")
        cursor.execute(restore_sql)
        print(f"数据库 {db_name} 还原完成。")

    if wait_for_db_online(db_name):
        print(f"数据库 {db_name} 已上线，开始授权用户...")
        grant_user_permission(db_name, windows_login)
    else:
        print(f"数据库 {db_name} 等待上线超时，跳过授权。")

def grant_user_permission(db_name, windows_login):
    with pyodbc.connect(conn_str, autocommit=True) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
            USE [{db_name}];
            IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = N'{windows_login}')
            BEGIN
                CREATE USER [{windows_login}] FOR LOGIN [{windows_login}];
            END;
            ALTER ROLE db_owner ADD MEMBER [{windows_login}];
            """)
            print(f"已授权用户 {windows_login} 访问数据库 {db_name}")
        except Exception as e:
            print(f"授权失败: {e}")

def export_to_csv(db_name):
    db_export_dir = os.path.join(export_dir, db_name)
    os.makedirs(db_export_dir, exist_ok=True)

    conn_str_db = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={sql_instance};"
        f"DATABASE={db_name};"
        f"Trusted_Connection=yes;"
    )

    with pyodbc.connect(conn_str_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            try:
                df = pd.read_sql(f"SELECT * FROM [{table}]", conn)
                safe_name = table.replace(" ", "_").replace("/", "_").replace("\\", "_")
                csv_path = os.path.join(db_export_dir, f"{safe_name}.csv")
                df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            except Exception as e:
                print(f"[警告] 导出表 {table} 时失败：{e}")



def delete_database(db_name):
    # 先删除数据库实例中的数据库
    with pyodbc.connect(conn_str, autocommit=True) as conn:
        cursor = conn.cursor()
        try:
            # 设置单用户，立即回滚事务，避免连接阻塞
            cursor.execute(f"ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
            cursor.execute(f"DROP DATABASE [{db_name}]")
            print(f"数据库 {db_name} 已从实例删除。")
        except Exception as e:
            print(f"删除数据库 {db_name} 失败（可能不存在）: {e}")

    # 删除物理文件
    data_file = os.path.join(restore_data_dir, f"{db_name}_data1.mdf")
    log_file = os.path.join(restore_log_dir, f"{db_name}_log1.ldf")

    for file_path in [data_file, log_file]:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"已删除文件: {file_path}")
            except Exception as e:
                print(f"删除文件 {file_path} 失败: {e}")


def handle_non_backup_file(bak_path, db_name):
    """
    非备份文件处理：复制文件并改后缀到导出目录，源文件不动
    """
    target_dir = os.path.join(export_dir, db_name)
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, db_name + ".xlsx")
    shutil.copy2(bak_path, target_file)
    print(f"非备份文件 {db_name} 复制为 {target_file}")

def process_all_bak_files():
    """处理所有备份文件"""
    recover_restoring_databases()
    bak_files = glob.glob(os.path.join(bak_dir, "*.bak"))
    for bak_file in bak_files:
        db_name = os.path.splitext(os.path.basename(bak_file))[0]

        try:
            logical_names = get_logical_names(bak_file)
        except Exception as e:
            print(f"[警告] 文件 {db_name} 不是备份文件，准备特殊处理: {e}")
            handle_non_backup_file(bak_file, db_name)
            continue

        try:
            print(f"\n=== 开始处理 {db_name} ===")
            restore_database(bak_file, db_name, logical_names)
            export_to_csv(db_name)
            delete_database(db_name)
        except Exception as e:
            print(f"[错误] 处理 {db_name} 失败: {e}")

if __name__ == "__main__":
    process_all_bak_files()
