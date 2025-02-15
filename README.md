# HNU-SPS
HNU - Spatiotemporal Prediction System (National College Student Innovation Training Program 2023-2025 )



## 开发环境

- conda 24.11.3
- node -v 22.11.0
- npm -v 11.0.0
- vue/cli 5.0.8
- psql (PostgreSQL) 17.1
- python 3.13.1



## 如何开始

### 前端

```bash
cd frontend
npm run serve
```

### 后端

（这里还要安装requirements环境，这一步还没有导出）

```bash
cd backend

# 修改config.py中的postgresql地址
# 对于本地的postgresql，按照格式：
#'postgresql://your_user:your_password@localhost/your_database'

python app.py
```

### 数据库

```bash
# 命令行或navicat启动postgresql
```



## 项目细节

前端技术栈：

- Vue.js
- Socket.IO (客户端)
- ECharts

后端技术栈：

- Flask
- Flask-SocketIO
- Python
- Logging
