from flask import jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from config import Config
from db import db
from sqlalchemy import text
import os
import time
import csv
from db import check_table_exists, create_table_from_csv, insert_csv_data, get_all_databases, get_columns_of_table, get_table_data
import logging
from datetime import datetime
from decimal import Decimal
from flask import Blueprint
from bound_compute import TimeSeriesForecaster
import numpy as np

api_blueprint = Blueprint('api', __name__)
socketio = SocketIO(cors_allowed_origins="*")   # 初始化 SocketIO
UPLOAD_FOLDER = './uploads'


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

# 返回数据库中所有表的名称


@api_blueprint.route('/api/database/<table_name>/info', methods=['GET'])
def get_table_info(table_name):
    logging.info(f"backend: get table info: {table_name}")
    try:
        # 获取请求参数 start 和 end
        valid_table_name = f"table_{table_name}".replace(
            '.', '_').replace('-', '_')
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

        formatted_data = [tuple(custom_serializer(value)
                                for value in row) for row in data]

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
            valid_table_name = f"table_{file_name}".replace(
                '.', '_').replace('-', '_')
            create_table_from_csv(valid_table_name, headers)
            # 插入数据到新表格
            insert_csv_data(valid_table_name, headers, rows)

        return jsonify({'code': 0, 'message': '文件上传成功', 'file_path': file_path}), 200
    except Exception as e:
        return jsonify({'code': 1, 'message': f'文件上传失败: {str(e)}'}), 200


@socketio.on('connect')
def handle_connect():
    """ WebSocket 连接成功时触发的事件 """
    logging.info("Client connected.")
    emit('connected', {'message': 'Connection established'})


@socketio.on('start_prediction')
def handle_start_prediction(data):
    """
    处理前端请求，执行预测并通过 socket 发送结果
    输入:
    - data: 前端发送的数据，未使用
    """
    logging.info("Prediction started.")
    # 调用模型
    # data = 模型返回
    M, C, V = 30, 5, 3  # 设定数据集大小
    data = np.random.rand(M, C, V)  # 生成随机数据

    T, T_prime = 5, 3  # 设置历史窗口和预测步长
    current_index = 0  # 滑动窗口起始索引

    first_forecaster = TimeSeriesForecaster(
        data[current_index:current_index + T + T_prime], T, T_prime)
    history_weighted = first_forecaster.history_weighted()
    weighted_result, lower_bound, upper_bound = first_forecaster.forward()

    # 发送历史加权值 + 第一轮预测数据
    socketio.emit('inference_result', {
        'history_weighted': history_weighted.tolist()
    })
    time.sleep(0.5)
    # socketio.emit('inference_result', {
    #     'predicted_weighted': weighted_result.tolist(),
    #     'lower_bound': lower_bound.tolist(),
    #     'upper_bound': upper_bound.tolist()
    # })
    # logging.info(f"Predicted: {type(weighted_result)}")
    for t in range(T_prime):
        socketio.emit('inference_result', {
            'predicted_weighted': [weighted_result[t].tolist()],
            'lower_bound': [lower_bound[t].tolist()],
            'upper_bound': [upper_bound[t].tolist()]
        })
        # logging.info(f"Predicted: {type(weighted_result[t])}")
        time.sleep(0.5)

    current_index += T_prime  # 向右移动预测步长

    while current_index + T + T_prime <= M:
        forecaster = TimeSeriesForecaster(
            data[current_index:current_index + T + T_prime], T, T_prime)
        weighted_result, lower_bound, upper_bound = forecaster.forward()

        for t in range(T_prime):
            socketio.emit('inference_result', {
                'predicted_weighted': [weighted_result[t].tolist()],
                'lower_bound': [lower_bound[t].tolist()],
                'upper_bound': [upper_bound[t].tolist()]
            })
            time.sleep(0.5)

        time.sleep(1)
        current_index += T_prime

    logging.info("Prediction finished.")
