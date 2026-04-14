# 后端更新日志

## 2026-04-15

### 新增文件

| 文件 | 说明 |
|------|------|
| `seed_directories.py` | 目录示例数据初始化脚本 |
| `update_directory_counts.py` | 更新目录用例数量统计脚本 |
| `schemas_workflow.py` | 工作流 Pydantic Schemas |
| `crud_workflow.py` | 工作流 CRUD 操作 |

### 修改文件

#### `routers/workflows.py`
- 新增工作流 API 路由
- `GET /workflows/{test_case_id}` 不存在时返回 `null` 而非 404
- 支持创建、更新、删除工作流

#### `schemas_workflow.py`
- 定义 `WorkflowCreate`、`WorkflowUpdate`、`WorkflowResponse` 等 Schema

#### `crud_workflow.py`
- 实现工作流 CRUD 操作
- **创建/删除工作流时自动同步 `TestCase.is_automated` 状态**

#### `seed_test_cases.py`
- 修复无效参数 `project_id`（改为 `directory_id` 关联）
- 添加目录 ID 关联

### API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/workflows` | 获取工作流列表 |
| GET | `/workflows/{test_case_id}` | 获取用例工作流（不存在返回 null） |
| POST | `/workflows/{test_case_id}` | 创建/更新工作流 |
| PUT | `/workflows/{workflow_id}` | 更新工作流 |
| DELETE | `/workflows/{workflow_id}` | 删除工作流 |

### 数据库初始化

```bash
# 初始化目录数据
python seed_directories.py

# 初始化测试用例数据
python seed_test_cases.py

# 更新目录用例数量统计
python update_directory_counts.py
```

### 功能说明

#### 工作流与自动化状态同步
- 创建工作流后，对应测试用例的 `is_automated` 自动设为 `True`
- 删除工作流后，对应测试用例的 `is_automated` 自动设为 `False`
- 前端通过 `is_automated` 字段判断用例是否已编排
