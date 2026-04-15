# 目录 API 响应格式修复

## ✅ 问题已解决

API 现在返回**扁平列表**而不是树形结构，与前端代码完美匹配！

---

## 🔧 修复内容

### **问题原因**

之前的 `get_all_directories()` 方法：
```python
# ❌ 错误：只返回根目录，并使用 selectinload 加载子目录
.where(Directory.parent_id.is_(None))  # 只获取根目录
.options(selectinload(Directory.children))  # 嵌套子目录
```

这导致返回的数据结构是：
```json
[
  {
    "id": 1,
    "name": "根目录",
    "children": [
      {"id": 2, "name": "子目录1"},
      {"id": 3, "name": "子目录2"}
    ]
  }
]
```

但前端代码期望的是**扁平列表**：
```javascript
const topLevelDirs = directories.filter((d) => !d.parent_id)
const childDirs = directories.filter((d) => d.parent_id)
```

### **修复方案**

修改 `app/repositories/directory_repo.py`:

```python
# ✅ 正确：返回所有目录的扁平列表
async def get_all_directories(self) -> List[Directory]:
    result = await self.db.execute(
        select(Directory)
        .order_by(Directory.sort_order.asc(), Directory.name)
    )
    return list(result.scalars().all())
```

现在返回的数据结构：
```json
[
  {"id": 1, "name": "根目录", "parent_id": null},
  {"id": 2, "name": "子目录1", "parent_id": 1},
  {"id": 3, "name": "子目录2", "parent_id": 1}
]
```

---

## 📋 API 响应示例

### **GET /directories**

```json
[
  {
    "id": 1,
    "name": "测试项目",
    "description": "主目录",
    "icon": "folder",
    "color": "blue",
    "sort_order": 1,
    "parent_id": null,
    "case_count": 10,
    "is_default": false,
    "created_at": "2026-04-15T10:00:00",
    "updated_at": "2026-04-15T10:00:00"
  },
  {
    "id": 2,
    "name": "API 测试",
    "description": "API 测试用例",
    "icon": "folder-open",
    "color": "green",
    "sort_order": 1,
    "parent_id": 1,
    "case_count": 5,
    "is_default": false,
    "created_at": "2026-04-15T10:05:00",
    "updated_at": "2026-04-15T10:05:00"
  },
  {
    "id": 3,
    "name": "UI 测试",
    "description": "UI 测试用例",
    "icon": "monitor",
    "color": "purple",
    "sort_order": 2,
    "parent_id": 1,
    "case_count": 5,
    "is_default": false,
    "created_at": "2026-04-15T10:10:00",
    "updated_at": "2026-04-15T10:10:00"
  }
]
```

---

## 🎯 前端代码兼容性

你的前端代码现在可以正常工作：

```typescript
// ✅ 这会正常工作
const topLevelDirs = directories.filter((d) => !d.parent_id)
const childDirs = directories.filter((d) => d.parent_id)

// ✅ 获取子目录
const getChildren = (parentId: number) => {
  return childDirs.filter((d) => d.parent_id === parentId)
}
```

---

## 📊 两种获取方式

### **1. 扁平列表**（前端自行构建树）
```
GET /directories
```
返回所有目录的扁平列表，前端使用 `parent_id` 自行构建树形结构。

**适用场景**：你的前端代码使用这种方式 ✅

### **2. 树形结构**（后端构建）
```
GET /directories/{id}
```
返回单个目录及其子目录的嵌套结构。

**适用场景**：需要单个目录的完整树形信息

---

## ✅ 验证步骤

1. **重启应用**
```bash
uvicorn app.main:app --reload
```

2. **测试 API**
```bash
curl http://localhost:8000/directories
```

3. **检查响应**
确保返回的是扁平列表，每个目录都有 `parent_id` 字段

4. **前端测试**
刷新前端页面，子目录应该正常显示

---

## 🎉 完成！

现在后端 API 返回的数据格式与你的前端代码完全匹配，层级目录应该可以正常显示了！

前端会根据 `parent_id` 自动：
- 筛选出顶层目录（`parent_id === null`）
- 筛选出子目录（`parent_id !== null`）
- 递归渲染子目录到对应的父目录下
