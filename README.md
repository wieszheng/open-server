# Script Market API

FastAPI 后端服务，提供脚本市场、测试用例管理和工作流编排接口。

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
# 初始化目录数据
python seed_directories.py

# 初始化测试用例数据
python seed_test_cases.py

# 更新目录用例数量统计
python update_directory_counts.py
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

### 测试用例 API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/test-cases` | 获取测试用例列表 |
| GET | `/test-cases/{id}` | 获取单个测试用例 |
| POST | `/test-cases` | 创建测试用例 |
| PUT | `/test-cases/{id}` | 更新测试用例 |
| DELETE | `/test-cases/{id}` | 删除测试用例 |
| GET | `/test-cases/stats` | 获取用例统计数据 |

### 目录 API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/directories` | 获取目录列表 |
| GET | `/directories/{id}` | 获取单个目录 |
| POST | `/directories` | 创建目录 |
| PUT | `/directories/{id}` | 更新目录 |
| DELETE | `/directories/{id}` | 删除目录 |

### 工作流 API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/workflows` | 获取工作流列表 |
| GET | `/workflows/{test_case_id}` | 获取用例工作流（不存在返回 null） |
| POST | `/workflows/{test_case_id}` | 创建/更新工作流 |
| PUT | `/workflows/{workflow_id}` | 更新工作流 |
| DELETE | `/workflows/{workflow_id}` | 删除工作流 |

### 控制台 API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/console/stats` | 获取控制台统计数据 |
| GET | `/console/executions` | 获取测试执行记录列表 |
| POST | `/console/executions` | 创建测试执行记录 |

## 数据库

使用 SQLite，通过 SQLAlchemy 异步操作。

## 目录结构

```
backend/
├── main.py              # FastAPI 入口
├── config.py            # 配置
├── database.py          # 数据库连接
├── models_*.py          # SQLAlchemy 模型
├── schemas*.py          # Pydantic schemas
├── crud*.py             # CRUD 操作
├── routers/             # API 路由
└── seed*.py            # 示例数据初始化
```

## 更新日志

详见 [CHANGELOG.md](./CHANGELOG.md)
