# HNU-SPS
HNU - Spatiotemporal Prediction System (National College Student Innovation Training Program 2023-2025 )



## 开发环境

- node -v 22.11.0
- npm -v 11.0.0
- vue/cli 5.0.8
- psql (PostgreSQL) 17.1



## 如何开始

### 前端

```bash
cd frontend
npm run serve
```

### 后端

```bash
cd backend

# 修改config.py中的postgresql地址
# 对于本地的postgresql，按照格式：
#'postgresql://your_user:your_password@localhost/your_database'

python app.py
```

