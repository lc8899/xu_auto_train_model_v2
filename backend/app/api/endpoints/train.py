from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.utils.file_handler import FileHandler
from app.models.train import TrainingCreate, TrainingResponse, TrainingStatus
from app.services.train import TrainingService
from typing import Dict, Any
import pandas as pd
from pathlib import Path
from app.config import settings

router = APIRouter()

@router.post("/upload", response_model=Dict[str, Any])
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传训练数据文件"""
    # 验证文件格式
    if not FileHandler.validate_file(file):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    # 保存文件
    file_id, file_path = await FileHandler.save_upload_file(file)
    
    # 获取文件信息
    try:
        file_info = FileHandler.get_excel_info(file_path)
        return {
            "file_id": file_id,
            **file_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/train", response_model=TrainingResponse)
async def create_training_task(
    file_id: str,
    training_params: TrainingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """创建训练任务"""
    try:
        training_service = TrainingService(db)
        task = await training_service.create_task(file_id, training_params)
        
        # 在后台开始训练
        background_tasks.add_task(
            training_service.run_training,
            task.id
        )
        
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{task_id}", response_model=TrainingStatus)
async def get_training_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """获取训练任务状态"""
    training_service = TrainingService(db)
    task = await training_service.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/data/{file_id}")
async def get_data(
    file_id: str,
    page: int = 1,
    page_size: int = 100,
    db: Session = Depends(get_db)
):
    """分页获取数据"""
    try:
        file_path = next(settings.UPLOAD_DIR.glob(f"{file_id}.*"))
        df = pd.read_excel(file_path)
        
        total_rows = len(df)
        total_pages = (total_rows + page_size - 1) // page_size
        
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)
        
        page_data = df.iloc[start_idx:end_idx].values.tolist()
        
        return {
            "total_rows": total_rows,
            "total_pages": total_pages,
            "current_page": page,
            "data": page_data,
            "columns": df.columns.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 