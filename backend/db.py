# db_setup.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import logging
from datetime import datetime

db = SQLAlchemy()

# /api/upload_csv
# 检查表格是否存在
def check_table_exists(table_name):
    # True : table exists
    try:
        valid_table_name = f"table_{table_name}"
        result = db.session.execute(text(f"SELECT to_regclass('{valid_table_name}');"))
        ans = result.scalar()
        if ans is None:
            logging.info(f"Table <{table_name}> does not exist. || database return: {ans}")
            return False
        else:
            logging.info(f"Table <{table_name}> exists. || database return: {ans}")
            return True
    except Exception as e:
        print(f"Error checking table existence: {e}")
        return False


def decide_type(header):
    """
    根据列名决定 PostgreSQL 数据类型。
    """
    if "编号" in header:
        return "TEXT"
    elif "经度" in header or "纬度" in header:
        return "FLOAT"
    elif "时间" in header:
        return "TIMESTAMP"
    elif "值" in header:
        return "NUMERIC(15, 10)"
    else:
        return "TEXT"

# 动态创建表格
def create_table_from_csv(file_name, headers):
    try:
        columns = ', '.join([f"{header} {decide_type(header)}" for header in headers])
        logging.info(columns)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {file_name} ({columns});"
        db.session.execute(text(create_table_sql))
        db.session.commit()
    except Exception as e:
        logging.error(f"Error creating table from csv: {e}")

# 插入 CSV 数据到新表
def insert_csv_data(file_name, headers, rows):

    insert_sql = f"INSERT INTO {file_name} ({', '.join(headers)}) VALUES ({', '.join([':value_' + str(i) for i in range(len(headers))])})"

    batch_size = 50
    try:
        for i in range(0, len(rows), batch_size):
            batch_rows = rows[i:i + batch_size]

            # 准备当前批次的数据
            cleaned_data = []
            for row in batch_rows:
                cleaned_row = []
                for header, value in zip(headers, row):
                    if header == "时间":
                        # 处理时间列的异常值
                        try:
                            if value.endswith("+08"):
                                value = value.replace("+08", "+0800")
                            cleaned_row.append(datetime.strptime(value, "%Y-%m-%d %H:%M:%S%z"))
                        except (ValueError, TypeError):
                            # 如果时间值无效，设置为 None 或默认时间
                            cleaned_row.append(None)
                    else:
                        # 对于非时间列，处理 'nan' 值为 None
                        cleaned_row.append(value if value != "nan" else None)
                cleaned_data.append(cleaned_row)

            data = [
                {f"value_{j}": cleaned_row[j] for j in range(len(headers))}
                for cleaned_row in cleaned_data
            ]

            # 插入当前批次
            db.session.execute(text(insert_sql), data)
            db.session.commit()

        logging.info("数据分批插入成功")
    except Exception as e:
        db.session.rollback()
        logging.error(f"插入数据失败: {e}")
        raise

# /api/get_databases
def get_all_databases():
    # 使用 db.session.execute 执行查询
    try:
        result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0][6:] if row[0].startswith('table_') else row[0] for row in result.fetchall()]
        return tables
    except Exception as e:
        print(f"Error getting all databases: {e}")



#
# 获取数据库的字段信息
def get_columns_of_table(database_name):
    try:
        # 查询表的所有字段，并按位置排序
        query = text(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = :table_name
            ORDER BY ordinal_position
        """)
        result = db.session.execute(query, {'table_name': database_name})
        columns = [row[0] for row in result.fetchall()]
        logging.info(columns)
        return columns
    except Exception as e:
        print(f"Error getting columns for table {database_name}: {e}")
        return None


# 获取表格的数据（分页处理）
def get_table_data(database_name, start, end):
    try:
        # 构建 SQL 查询，使用 LIMIT 和 OFFSET 来分页
        query = text(f"SELECT * FROM {database_name} LIMIT :limit OFFSET :offset")
        result = db.session.execute(query, {'limit': end - start, 'offset': start})
        # 获取查询结果并返回
        rows = result.fetchall()
        logging.info(rows)
        return rows
    except Exception as e:
        print(f"Error getting data for table {database_name}: {e}")
        return None
