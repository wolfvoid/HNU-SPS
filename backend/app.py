from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config
from db import db
from sqlalchemy import text
import os
import csv
from db import check_table_exists,create_table_from_csv,insert_csv_data, get_all_databases, get_columns_of_table, get_table_data
import logging
from logging.handlers import RotatingFileHandler
# from predictions import run_prediction, calculate_score
# from models import Database, TimeSeriesData
from datetime import datetime
from decimal import Decimal
from flask import Blueprint
api_blueprint = Blueprint('api', __name__)
UPLOAD_FOLDER = './uploads'

# 日志配置函数
def setup_logging():
    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # 设置日志级别
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # 文件日志处理器
    file_handler = RotatingFileHandler(
        'app.log', maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    # 控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)   # 启用CORS处理跨域
    db.init_app(app)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.register_blueprint(api_blueprint)
    return app

def delimiter_detect(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        # 自动检测分隔符
        sample = csvfile.read(1024)  # 读取文件的前 1024 个字符作为样本
        csvfile.seek(0)  # 将文件指针重置到开头
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter  # 检测分隔符
        logging.info("333")
        return delimiter

def custom_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # 转换 Decimal 为浮点数
    elif isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return obj

# test
@api_blueprint.route('/')
def index():
    result = db.session.execute(text('SELECT 1'))
    return f"Database connection successful: {result}"

# 返回所有数据库名称
@api_blueprint.route('/api/get_databases', methods=['GET'])
def get_databases():
    logging.info("backend:get_databases")
    try:
        # 调用获取数据库名称的函数
        databases = get_all_databases()
        logging.info(databases)
        return jsonify({'code': 0, 'databases': databases})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#
@api_blueprint.route('/api/database/<table_name>/info', methods=['GET'])
def get_table_info(table_name):
    logging.info(f"backend: get table info: {table_name}")
    try:
        # 获取请求参数 start 和 end
        valid_table_name = f"table_{table_name}".replace('.', '_').replace('-', '_')
        start = int(request.args.get('start', 0))
        end = int(request.args.get('end', 50))  # 默认每次请求 50 行数据

        # 获取表的所有字段名
        columns = get_columns_of_table(valid_table_name)
        if columns is None:
            return jsonify({"code": 1, "message": "Error fetching columns."}), 200

        # 获取表的数据（分页）
        data = get_table_data(valid_table_name, start, end)
        if data is None:
            return jsonify({"code": 1, "message": "Error fetching data."}), 200

        formatted_data = [tuple(custom_serializer(value) for value in row) for row in data]

        logging.info(formatted_data)

        return jsonify({
            "code": 0,
            "fieldNames": columns,
            "data": formatted_data  # 每行是一个元组
        }), 200


    except Exception as e:
        print(f"Error in get_database_info: {e}")
        return jsonify({"code": 1, "message": "Internal server error."}), 200


# 接收csv并写入数据库
@api_blueprint.route('/api/upload_csv', methods=['POST'])
def upload_csv():
    logging.info("backend: upload_csv")
    if 'file' not in request.files:
        return jsonify({'code': 1, 'message': '没有检测到文件'}), 200
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 1, 'message': '文件名为空'}), 200
    if not file.filename.endswith('.csv'):
        return jsonify({'code': 1, 'message': '文件格式错误，只支持CSV'}), 200

    try:
        file_name = file.filename[:-4]  # 去掉 .csv 后缀
        logging.info(f"file_name: {file_name} ")
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # 检查表格是否已存在
        if check_table_exists(file_name):
            logging.info(f"file_exists: {file_name} ")
            return jsonify({'code': 1, 'message': f'表格 "{file_name}" 已存在'}), 200

        # 读取 CSV 文件
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            # delimiter = delimiter_detect(file_path)
            # logging.info(delimiter)
            csvreader = csv.reader(csvfile, delimiter='\t')
            headers = next(csvreader)  # 第一行是特征标签
            logging.info(headers)
            rows = [tuple(row) for row in csvreader]
            # 创建新表格
            valid_table_name = f"table_{file_name}".replace('.', '_').replace('-', '_')
            create_table_from_csv(valid_table_name, headers)
            # 插入数据到新表格
            insert_csv_data(valid_table_name, headers, rows)

        return jsonify({'code': 0, 'message': '文件上传成功', 'file_path': file_path}), 200
    except Exception as e:
        return jsonify({'code': 1, 'message': f'文件上传失败: {str(e)}'}), 200


@api_blueprint.route('/api/predict', methods=['POST'])
def predict():
    """接受前端预测请求，返回模型预测结果"""
    # data = request.get_json()
    # database_name = data['database_name']
    # model_name = data['model_name']
    # time_step = data['time_step']

    # prediction_result = run_prediction(database_name, model_name, time_step)
    # return jsonify({'prediction': prediction_result})
    return 0

@api_blueprint.route('/api/calculate_score', methods=['POST'])
def calculate():
    """根据加权特征计算综合评分，并检查预警"""
    # data = request.get_json()
    # score, alert = calculate_score(data)
    # return jsonify({'score': score, 'alert': alert})
    return 0

if __name__ == "__main__":
    setup_logging()
    app = create_app()
    app.logger.setLevel(logging.DEBUG)
    app.run(host="0.0.0.0", port=5000, debug=True)

