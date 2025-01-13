from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config
from db_setup import db
from sqlalchemy import text
import os
# from utils import handle_csv_upload
# from predictions import run_prediction, calculate_score
# from models import Database, TimeSeriesData

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(Config)
# 启用CORS处理跨域
CORS(app)
db.init_app(app)

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# test
@app.route('/')
def index():
    result = db.session.execute(text('SELECT 1'))
    return f"Database connection successful: {result}"

@app.route('/api/databases', methods=['GET'])
def get_databases():
    """返回所有数据库的名称"""
    # databases = Database.query.all()
    # return jsonify([db.name for db in databases])
    return 0

@app.route('/api/database/<database_name>/info', methods=['GET'])
def get_database_info(database_name):
    """返回选择数据库中的时间序列数据"""
    # database = Database.query.filter_by(name=database_name).first()
    # if not database:
    #     return jsonify({'error': 'Database not found'}), 404

    # time_series_data = TimeSeriesData.query.filter_by(database_id=database.id).all()
    # return jsonify([data.to_dict() for data in time_series_data])
    return 0

# 接收csv并写入数据库
@app.route('/api/upload_csv', methods=['POST'])
def upload_csv():
    print("get csv")
    if 'file' not in request.files:
        return jsonify({'code': 1, 'message': '没有检测到文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 1, 'message': '文件名为空'}), 400
    if not file.filename.endswith('.csv'):
        return jsonify({'code': 1, 'message': '文件格式错误，只支持CSV'}), 400

    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        return jsonify({'code': 0, 'message': '文件上传成功', 'file_path': file_path}), 200
    except Exception as e:
        return jsonify({'code': 1, 'message': f'文件上传失败: {str(e)}'}), 500


@app.route('/api/predict', methods=['POST'])
def predict():
    """接受前端预测请求，返回模型预测结果"""
    # data = request.get_json()
    # database_name = data['database_name']
    # model_name = data['model_name']
    # time_step = data['time_step']

    # prediction_result = run_prediction(database_name, model_name, time_step)
    # return jsonify({'prediction': prediction_result})
    return 0

@app.route('/api/calculate_score', methods=['POST'])
def calculate():
    """根据加权特征计算综合评分，并检查预警"""
    # data = request.get_json()
    # score, alert = calculate_score(data)
    # return jsonify({'score': score, 'alert': alert})
    return 0

if __name__ == '__main__':
    app.run(debug=True)
