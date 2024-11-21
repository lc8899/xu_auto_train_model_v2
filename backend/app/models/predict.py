from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class PredictionCreate(BaseModel):
    training_task_id: str

class PredictionResponse(BaseModel):
    id: str
    status: str
    result_path: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class PredictionStatus(BaseModel):
    status: str
    result_path: Optional[str]
    error_message: Optional[str] 