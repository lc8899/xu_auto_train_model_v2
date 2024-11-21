from sqlalchemy.orm import Session
from app.db.models import TrainingTask
from app.models.train import TrainingCreate, TrainingStatus
from app.core.config import settings
from pathlib import Path
import asyncio
from autogluon.tabular import TabularPredictor
import pandas as pd
from app.services.websocket import WebSocketManager

class TrainingService:
    def __init__(self, db: Session):
        self.db = db

    async def create_task(self, file_id: str, params: TrainingCreate) -> TrainingTask:
        """创建训练任务"""
        file_path = next(settings.UPLOAD_DIR.glob(f"{file_id}.*"))
        
        task = TrainingTask(
            file_path=str(file_path),
            feature_columns=params.feature_columns,
            target_column=params.target_column,
            preset=params.preset,
            time_limit=params.time_limit or settings.DEFAULT_TIME_LIMIT,
            eval_metric=params.eval_metric
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    async def run_training(self, task_id: str):
        """执行训练任务"""
        task = self.db.query(TrainingTask).filter(TrainingTask.id == task_id).first()
        if not task:
            return
        
        try:
            # 更新任务状态
            task.status = "running"
            self.db.commit()
            
            # 读取数据
            df = pd.read_excel(task.file_path)
            
            # 设置保存路径
            save_path = settings.MODEL_DIR / task_id
            
            # 创建预测器
            predictor = TabularPredictor(
                label=task.target_column,
                path=str(save_path),
                eval_metric=task.eval_metric
            )
            
            # 自定义回调函数来更新进度
            def update_progress(progress):
                task.progress = progress
                self.db.commit()
                # 通过 WebSocket 发送进度
                asyncio.create_task(
                    WebSocketManager().send_progress(
                        task_id, 
                        {"status": "running", "progress": progress}
                    )
                )
            
            # 添加回调到 AutoGluon
            predictor.fit(
                train_data=df,
                time_limit=task.time_limit,
                presets=[task.preset],
                # 添加进度回调
                fit_callback=update_progress
            )
            
            # 获取模型性能指标
            leaderboard = predictor.leaderboard()
            
            # 获取特征重要性
            feature_importance = predictor.feature_importance(df)
            
            # 更新任务状态
            task.status = "completed"
            task.model_path = str(save_path)
            task.metrics = {
                "leaderboard": leaderboard.to_dict(orient="records"),
                "feature_importance": feature_importance.to_dict()
            }
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
        
        finally:
            self.db.commit()

    async def get_task_status(self, task_id: str) -> TrainingStatus:
        """获取任务状态"""
        task = self.db.query(TrainingTask).filter(TrainingTask.id == task_id).first()
        if not task:
            return None
            
        return TrainingStatus(
            status=task.status,
            progress=task.progress,
            metrics=task.metrics,
            error_message=task.error_message
        ) 