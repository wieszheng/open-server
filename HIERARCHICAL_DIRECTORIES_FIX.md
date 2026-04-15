# 层级目录结构修复完成

## ✅ 问题已解决

层级目录结构（父子目录）现在已完全支持！

---

## 🔧 修复内容

### 1. **模型层更新** (`app/models/directory.py`)

添加了 `parent_id` 字段和自关联关系：

```python
# 层级结构
parent_id: Mapped[Optional[int]] = mapped_column(
    Integer, ForeignKey("directories.id"), nullable=True, comment="父目录ID"
)

# 关联关系
children: Mapped[List["Directory"]] = relationship(
    "Directory", backref="parent", remote_side=[id], lazy="select"
)
```

### 2. **Schema 层更新** (`app/schemas/directory.py`)

恢复了 `parent_id` 字段：

```python
class DirectoryBase(BaseModel):
    parent_id: Optional[int] = Field(None, description="父目录ID")

class DirectoryUpdate(BaseModel):
    parent_id: Optional[int] = Field(None, description="父目录ID")
```

### 3. **Repository 层增强** (`app/repositories/directory_repo.py`)

新增方法：
- `get_all_directories()` - 获取所有根目录（包含子目录）
- `get_directory_with_children()` - 获取目录及其子目录
- `get_children()` - 获取指定父目录的所有子目录
- `delete_with_children()` - 递归删除目录及其所有子目录

### 4. **Service 层更新** (`app/services/directory_service.py`)

新增方法：
- `get_children(parent_id)` - 获取子目录列表

### 5. **Router 层新增端点** (`app/routers/directories.py`)

新增 API 端点：
```
GET /directories/{directory_id}/children
```
获取指定目录的所有子目录。

### 6. **数据库迁移**

运行迁移脚本添加 `parent_id` 列：
```bash
python add_parent_id_migration.py
```

---

## 📋 使用示例

### 创建根目录

```json
POST /directories
{
  "name": "测试项目",
  "description": "主目录",
  "icon": "folder",
  "color": "blue",
  "sort_order": 1
}
```

### 创建子目录

```json
POST /directories
{
  "name": "API 测试",
  "description": "API 测试用例",
  "parent_id": 1,  // 父目录 ID
  "icon": "folder-open",
  "color": "green",
  "sort_order": 1
}
```

### 获取所有根目录（包含子目录）

```
GET /directories
```

响应示例：
```json
[
  {
    "id": 1,
    "name": "测试项目",
    "parent_id": null,
    "case_count": 10,
    "children": [
      {
        "id": 2,
        "name": "API 测试",
        "parent_id": 1,
        "case_count": 5
      },
      {
        "id": 3,
        "name": "UI 测试",
        "parent_id": 1,
        "case_count": 5
      }
    ]
  }
]
```

### 获取指定目录的子目录

```
GET /directories/1/children
```

### 更新目录的父级关系

```json
PUT /directories/2
{
  "parent_id": 3  // 移动到另一个父目录
}
```

### 删除目录（级联删除子目录）

```
DELETE /directories/1
```

这将：
1. 递归删除目录 1 及其所有子目录
2. 将所有子目录下的测试用例移至无目录（`directory_id = NULL`）

---

## 🌳 层级结构示例

```
测试项目 (id=1, parent_id=null)
├── API 测试 (id=2, parent_id=1)
│   ├── 用户模块 (id=4, parent_id=2)
│   └── 订单模块 (id=5, parent_id=2)
├── UI 测试 (id=3, parent_id=1)
│   └── 页面测试 (id=6, parent_id=3)
└── 性能测试 (id=7, parent_id=1)
```

---

## 🎯 关键特性

✅ **无限层级** - 支持任意深度的目录嵌套  
✅ **级联删除** - 删除父目录自动删除所有子目录  
✅ **用例保护** - 删除目录时，用例移至无目录而非删除  
✅ **懒加载** - 使用 SQLAlchemy 的 `selectinload` 优化查询  
✅ **递归查询** - 自动获取所有层级的子目录  

---

## 🚀 下一步

重启应用以使用新的层级目录功能：

```bash
uvicorn app.main:app --reload
```

访问 API 文档测试：
- http://localhost:8000/docs

---

## 📝 数据库变更

**表**: `directories`  
**新增列**: `parent_id INTEGER REFERENCES directories(id)`  

迁移脚本: `add_parent_id_migration.py`

---

## ⚠️ 注意事项

1. **循环引用检测** - 当前未实现，避免将目录的父级设置为其自身或后代
2. **性能优化** - 深层级目录可能影响性能，建议不超过 5 层
3. **前端支持** - 前端需要使用树形组件展示层级结构

---

**层级目录功能现已完全可用！** 🎉
