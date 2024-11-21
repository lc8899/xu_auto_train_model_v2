from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.utils.file_handler import FileHandler
from app.models.predict import PredictionCreate, PredictionResponse, PredictionStatus
from app.services.predict import PredictionService
from app.models.train import TrainingTask
import pandas as pd

router = APIRouter()

@router.post("/upload", response_model=PredictionResponse)
async def create_prediction_task(
    training_task_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """上传预测数据并创建预测任务"""
    # 验证文件格式
    if not FileHandler.validate_file(file):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    try:
        # 保存文件
        file_id, file_path = await FileHandler.save_upload_file(file)
        
        # 创建预测任务
        prediction_service = PredictionService(db)
        task = await prediction_service.create_task(training_task_id, file_path)
        
        # 在后台开始预测
        background_tasks.add_task(
            prediction_service.run_prediction,
            task.id
        )
        
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{task_id}", response_model=PredictionStatus)
async def get_prediction_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """获取预测任务状态"""
    prediction_service = PredictionService(db)
    task = await prediction_service.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/download/{task_id}")
async def download_prediction_results(
    task_id: str,
    db: Session = Depends(get_db)
):
    """下载预测结果"""
    prediction_service = PredictionService(db)
    file_path = await prediction_service.get_result_file(task_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Result file not found")
    return FileResponse(file_path)

@router.get("/model/{model_uuid}")
async def get_model_info(
    model_uuid: str,
    db: Session = Depends(get_db)
):
    """获取模型详细信息"""
    task = db.query(TrainingTask).filter(TrainingTask.id == model_uuid).first()
    if not task:
        raise HTTPException(status_code=404, detail="Model not found")
        
    return {
        "model_info": {
            "task_type": "regression" if task.eval_metric in ["rmse", "mae", "r2"] else "classification",
            "feature_columns": [
                {
                    "name": col,
                    "type": "numerical" if pd.api.types.is_numeric_dtype(pd.read_excel(task.file_path)[col]) else "categorical",
                    "required": True
                }
                for col in task.feature_columns
            ],
            "target_column": task.target_column,
            "metrics": task.metrics,
            "created_at": task.created_at
        }
    } 