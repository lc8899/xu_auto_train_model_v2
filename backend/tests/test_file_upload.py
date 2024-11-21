import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import pandas as pd
from app.main import app

client = TestClient(app)

@pytest.fixture
def sample_excel():
    """创建测试用的Excel文件"""
    df = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': ['a', 'b', 'c', 'd', 'e'],
        'target': [0, 1, 0, 1, 0]
    })
    file_path = Path("test_data.xlsx")
    df.to_excel(file_path, index=False)
    yield file_path
    file_path.unlink()  # 清理测试文件

def test_upload_file(sample_excel):
    """测试文件上传功能"""
    with open(sample_excel, "rb") as f:
        response = client.post(
            "/api/train/upload",
            files={"file": ("test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert "total_rows" in data
    assert "columns" in data
    assert data["total_rows"] == 5 