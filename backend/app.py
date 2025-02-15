from flask import Flask
from flask_cors import CORS
from config import Config
from db import db
import os
import logging
from logging.handlers import RotatingFileHandler
from api_views import api_blueprint, socketio

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

setup_logging()
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)   # 启用CORS处理跨域
db.init_app(app)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
socketio.init_app(app)
app.register_blueprint(api_blueprint)
app.logger.setLevel(logging.DEBUG)
# app.run(host="0.0.0.0", port=5000, debug=True)
socketio.run(app, host="0.0.0.0", port=5000, debug=True)
