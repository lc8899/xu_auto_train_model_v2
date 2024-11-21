from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from .base import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class TrainingTask(Base):
    __tablename__ = "training_tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    file_path = Column(String, nullable=False)
    feature_columns = Column(JSON, nullable=False)
    target_column = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    progress = Column(Float, default=0.0)
    preset = Column(String, nullable=False)
    time_limit = Column(Integer, nullable=False)
    eval_metric = Column(String)
    model_path = Column(String)
    metrics = Column(JSON)
    error_message = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class PredictionTask(Base):
    __tablename__ = "prediction_tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    training_task_id = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    result_path = Column(String)
    error_message = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now()) 