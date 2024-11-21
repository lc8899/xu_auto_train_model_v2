import pytest
from fastapi.testclient import TestClient
from app.main import app
from pathlib import Path
import pandas as pd

client = TestClient(app)

@pytest.fixture
def prediction_data():
    """创建预测用的Excel文件"""
    df = pd.DataFrame({
        'feature1': [6, 7, 8],
        'feature2': ['f', 'g', 'h']
    })
    file_path = Path("test_predict.xlsx")
    df.to_excel(file_path, index=False)
    yield file_path
    file_path.unlink()

def test_create_prediction_task(prediction_data):
    """测试创建预测任务"""
    # 假设我们已经有了一个训练好的模型
    training_task_id = "existing-model-id"
    
    with open(prediction_data, "rb") as f:
        response = client.post(
            "/api/predict/upload",
            params={"training_task_id": training_task_id},
            files={"file": ("test_predict.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"

def test_get_prediction_status():
    """测试获取预测状态"""
    response = client.get("/api/predict/status/test-task-id")
    assert response.status_code == 404  # 因为任务ID不存在 