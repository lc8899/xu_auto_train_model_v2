import pandas as pd
from pathlib import Path
from fastapi import UploadFile
import uuid
from typing import Tuple, List, Dict, Any
from app.core.config import settings

class FileHandler:
    @staticmethod
    async def save_upload_file(file: UploadFile) -> Tuple[str, Path]:
        """保存上传的文件并返回文件ID和路径"""
        file_id = str(uuid.uuid4())
        # 使用原始文件扩展名
        extension = Path(file.filename).suffix
        file_path = settings.UPLOAD_DIR / f"{file_id}{extension}"
        
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
            
        return file_id, file_path

    @staticmethod
    def get_excel_info(file_path: Path) -> Dict[str, Any]:
        """读取Excel文件信息"""
        df = pd.read_excel(file_path)
        
        # 获取列信息
        columns_info = []
        for col in df.columns:
            col_type = "numerical" if pd.api.types.is_numeric_dtype(df[col]) else "categorical"
            missing_count = df[col].isnull().sum()
            unique_count = df[col].nunique()
            
            columns_info.append({
                "name": col,
                "type": col_type,
                "missing_count": int(missing_count),
                "unique_count": int(unique_count)
            })
        
        return {
            "total_rows": len(df),
            "columns": columns_info,
            "preview_data": df.head(5).to_dict(orient="records")
        }

    @staticmethod
    def validate_file(file: UploadFile) -> bool:
        """验证文件格式"""
        allowed_extensions = {".xlsx", ".xls"}
        return Path(file.filename).suffix.lower() in allowed_extensions 

    @staticmethod
    def read_excel_in_chunks(file_path: Path, chunk_size: int = 1000):
        """分块读取Excel文件"""
        return pd.read_excel(file_path, chunksize=chunk_size)