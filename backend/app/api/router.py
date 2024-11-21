from fastapi import APIRouter
from app.api.endpoints import train, predict

api_router = APIRouter()

api_router.include_router(train.router, prefix="/train", tags=["train"])
api_router.include_router(predict.router, prefix="/predict", tags=["predict"]) 