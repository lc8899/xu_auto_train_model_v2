import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.main import app
from fastapi.testclient import TestClient
import os

# 使用内存数据库进行测试
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine):
    """每个测试用例使用独立的数据库会话"""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """创建测试客户端"""
    app.dependency_overrides = {}  # 清除所有依赖覆盖
    with TestClient(app) as client:
        yield client 