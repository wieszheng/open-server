# Script Market API

FastAPI 后端服务，提供脚本市场和控制台数据接口。

## 快速开始

### 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 启动服务

```bash
uvicorn main:app --reload --port 8000
```

### 初始化示例数据

```bash
python seed.py
```

## API 端点

### 脚本 API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/scripts` | 获取脚本列表 |
| GET | `/scripts/featured` | 获取精选脚本 |
| GET | `/scripts/{id}` | 获取单个脚本 |
| POST | `/scripts` | 创建脚本 |
| PUT | `/scripts/{id}` | 更新脚本 |
| DELETE | `/scripts/{id}` | 删除脚本 |
| POST | `/scripts/{id}/views` | 增加浏览量 |
| POST | `/scripts/{id}/downloads` | 增加下载量 |

### 控制台 API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/console/stats` | 获取控制台统计数据 |
| GET | `/console/executions` | 获取测试执行记录列表 |
| POST | `/console/executions` | 创建测试执行记录 |

## 数据库

使用 SQLite，通过 SQLAlchemy 异步操作。
