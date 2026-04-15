# 快速开始指南

## 🚀 5 分钟启动应用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或使用 Poetry（推荐）：

```bash
poetry install
```

### 2. 配置环境变量

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件（可选，已有默认值）
DATABASE_URL=sqlite+aiosqlite:///./scripts.db
APP_NAME=Script Market API
DEBUG=True
```

### 3. 启动应用

```bash
# 方式 1: 使用 uvicorn
uvicorn app.main:app --reload

# 方式 2: 使用启动脚本
python run.py
```

### 4. 访问应用

- **API 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

---

## 📝 常用命令

### 运行测试

```bash
pytest
pytest -v  # 详细输出
pytest --cov=app  # 覆盖率报告
```

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 代码格式化

```bash
black app/ tests/
isort app/ tests/
ruff check app/ tests/
```

---

## 📂 项目结构速览

```
app/
├── main.py           # 应用入口
├── models/           # 数据模型
├── schemas/          # 数据验证
├── repositories/     # 数据访问
├── services/         # 业务逻辑
└── routers/          # API 路由
```

---

## 🔧 开发新特性

### 添加新的 API 端点

1. **创建模型** (如需要): `app/models/your_model.py`
2. **创建 Schema**: `app/schemas/your_schema.py`
3. **创建 Repository**: `app/repositories/your_repo.py`
4. **创建 Service**: `app/services/your_service.py`
5. **创建 Router**: `app/routers/your_router.py`
6. **注册依赖**: `app/dependencies.py`
7. **注册路由**: `app/main.py`

### 示例：添加新功能

```python
# app/models/example.py
from app.database import Base

class Example(Base):
    __tablename__ = "examples"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

# app/services/example_service.py
class ExampleService:
    def __init__(self, repo: ExampleRepository):
        self.repo = repo
    
    async def get_examples(self):
        return await self.repo.get_all()

# app/routers/example.py
@router.get("/examples")
async def list_examples(service: ExampleService = Depends(get_example_service)):
    return await service.get_examples()
```

---

## ❓ 常见问题

**Q: 数据库连接失败？**  
A: 检查 `.env` 中的 `DATABASE_URL` 是否正确。

**Q: 导入错误？**  
A: 确保在项目根目录运行，或使用 `python -m app.main`。

**Q: 测试失败？**  
A: 确保安装了测试依赖：`pip install pytest pytest-asyncio httpx`。

---

## 📚 更多文档

- [重构完成报告](REFACTORING_COMPLETE.md)
- [原始 README](README.md)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [开发规范](https://wieszheng.github.io/python/fastapi)
