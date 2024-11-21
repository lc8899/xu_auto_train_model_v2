from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
from app.services.websocket import WebSocketManager

router = APIRouter()
manager = WebSocketManager()

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await manager.connect(task_id, websocket)
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(task_id) 