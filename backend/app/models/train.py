from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TrainingCreate(BaseModel):
    feature_columns: List[str]
    target_column: str
    preset: str = Field(..., description="best_quality, high_quality, good_quality")
    time_limit: Optional[int] = None
    eval_metric: Optional[str] = None

class TrainingResponse(BaseModel):
    id: str
    status: str
    progress: float
    model_path: Optional[str]
    metrics: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class TrainingStatus(BaseModel):
    status: str
    progress: float
    current_stage: Optional[str]
    metrics: Optional[Dict[str, Any]]
    error_message: Optional[str] 