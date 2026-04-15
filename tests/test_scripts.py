"""脚本 API 测试"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_script(client: AsyncClient):
    """测试创建脚本"""
    script_data = {
        "name": "测试脚本",
        "description": "这是一个测试脚本",
        "code": "print('Hello World')",
        "category": "api",
        "author": "测试者",
        "tags": ["test", "demo"],
    }

    response = await client.post("/scripts", json=script_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == script_data["name"]
    assert data["description"] == script_data["description"]
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_get_scripts(client: AsyncClient):
    """测试获取脚本列表"""
    response = await client.get("/scripts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_featured_scripts(client: AsyncClient):
    """测试获取精选脚本"""
    response = await client.get("/scripts/featured")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_script_not_found(client: AsyncClient):
    """测试获取不存在的脚本"""
    response = await client.get("/scripts/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """测试健康检查端点"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
