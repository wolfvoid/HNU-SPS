import csv
from app import db
from models import Database, TimeSeriesData

def handle_csv_upload(file):
    """处理CSV文件上传并将数据存储到数据库"""
    try:
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # 假设CSV第一行是表头
        database_name = header[0]  # 假设CSV中第一列是数据库名称

        # 创建新数据库条目
        database = Database(name=database_name)
        db.session.add(database)
        db.session.commit()

        # 解析CSV内容并存储
        for row in csv_reader:
            timestamp = row[0]
            value = float(row[1])
            time_series = TimeSeriesData(timestamp=timestamp, value=value, database_id=database.id)
            db.session.add(time_series)

        db.session.commit()
        return {'status': 'success'}
    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}
