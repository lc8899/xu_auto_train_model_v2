from sqlalchemy.orm import Session
from app.db.models import PredictionTask, TrainingTask
from app.models.predict import PredictionStatus
from app.core.config import settings
from pathlib import Path
from autogluon.tabular import TabularPredictor
import pandas as pd
from typing import Dict

class PredictionService:
    def __init__(self, db: Session):
        self.db = db

    async def create_task(self, training_task_id: str, file_path: Path) -> PredictionTask:
        """创建预测任务"""
        # 检查训练任务是否存在且完成
        training_task = self.db.query(TrainingTask).filter(
            TrainingTask.id == training_task_id,
            TrainingTask.status == "completed"
        ).first()
        
        if not training_task:
            raise ValueError("Training task not found or not completed")
        
        task = PredictionTask(
            training_task_id=training_task_id,
            file_path=str(file_path)
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    async def validate_prediction_data(self, df: pd.DataFrame, training_task: TrainingTask) -> Dict:
        """验证预测数据的列是否匹配"""
        required_columns = training_task.feature_columns
        df_columns = df.columns.tolist()
        
        missing_columns = [col for col in required_columns if col not in df_columns]
        extra_columns = [col for col in df_columns if col not in required_columns]
        
        # 检查缺失值
        missing_values = {
            col: int(df[col].isnull().sum())
            for col in required_columns
            if col in df_columns and df[col].isnull().any()
        }
        
        return {
            "is_valid": len(missing_columns) == 0,
            "missing_columns": missing_columns,
            "extra_columns": extra_columns,
            "missing_values": missing_values
        }

    async def run_prediction(self, task_id: str):
        """执行预测任务"""
        task = self.db.query(PredictionTask).filter(PredictionTask.id == task_id).first()
        if not task:
            return
            
        try:
            # 更新任务状态
            task.status = "running"
            self.db.commit()
            
            # 获取训练任务信息
            training_task = self.db.query(TrainingTask).filter(
                TrainingTask.id == task.training_task_id
            ).first()
            
            # 读取预测数据
            df = pd.read_excel(task.file_path)
            
            # 验证数据
            validation_result = await self.validate_prediction_data(df, training_task)
            if not validation_result["is_valid"]:
                raise ValueError(f"Missing required columns: {validation_result['missing_columns']}")
            
            # 加载预测器
            predictor = TabularPredictor.load(training_task.model_path)
            
            # 执行预测
            predictions = predictor.predict(df)
            
            # 将预测结果添加到数据框
            df['predictions'] = predictions
            
            # 保存结果
            result_path = settings.RESULT_DIR / f"{task_id}.xlsx"
            df.to_excel(result_path, index=False)
            
            # 更新任务状态
            task.status = "completed"
            task.result_path = str(result_path)
            
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
        
        finally:
            self.db.commit()

    async def get_task_status(self, task_id: str) -> PredictionStatus:
        """获取任务状态"""
        task = self.db.query(PredictionTask).filter(PredictionTask.id == task_id).first()
        if not task:
            return None
            
        return PredictionStatus(
            status=task.status,
            result_path=task.result_path,
            error_message=task.error_message
        )

    async def get_result_file(self, task_id: str) -> Path:
        """获取结果文件路径"""
        task = self.db.query(PredictionTask).filter(
            PredictionTask.id == task_id,
            PredictionTask.status == "completed"
        ).first()
        
        if not task or not task.result_path:
            return None
            
        return Path(task.result_path) 