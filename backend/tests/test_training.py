import pytest
from fastapi.testclient import TestClient
from app.main import app
import asyncio
import json

client = TestClient(app)

@pytest.fixture
def training_data():
    return {
        "feature_columns": ["feature1", "feature2"],
        "target_column": "target",
        "preset": "good_quality",
        "time_limit": 60
    }

def test_create_training_task(training_data):
    """测试创建训练任务"""
    # 先上传文件
    with open("test_data.xlsx", "rb") as f:
        response = client.post(
            "/api/train/upload",
            files={"file": ("test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
    
    file_id = response.json()["file_id"]
    
    # 创建训练任务
    response = client.post(
        "/api/train/train",
        json={
            "file_id": file_id,
            **training_data
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"

@pytest.mark.asyncio
async def test_websocket_connection():
    """测试WebSocket连接"""
    async with client.websocket_connect("/ws/test-task-id") as websocket:
        await websocket.send_text("ping")
        data = await websocket.receive_text()
        assert data == "pong" 