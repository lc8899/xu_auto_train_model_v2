# AutoML Web 平台设计文档

## 项目概述
本项目是一个基于 Vue.js + FastAPI + AutoGluon 的自动机器学习 Web 平台，实现表格数据的自动化建模和预测。

## 技术栈
- 前端：Vue 3 + Element Plus+Echarts,端UI遵循Material Design 3设计规范
- 后端：FastAPI
- 机器学习：AutoGluon-Tabular
- 数据库：SQLite

## 系统架构

[前端] <-> [后端 API] <-> [AutoGluon 模型服务]
## 功能模块详细设计

### 1. 模型训练功能

#### 1.1 数据上传与预览
- Excel文件拖拽或点击上传
- 前端解析并展示Excel数据表格
- 显示数据基本信息（行数、列数、列类型）
- 支持大数据量分页显示

#### 1.2 数据可视化与特征选择
- 前端使用ECharts进行数据可视化
  - 数值型列：直方图、箱线图
  - 分类型列：饼图、柱状图
  - 缺失值统计展示
- 特征列多选功能
- 目标列单选功能（自动识别数值/分类任务）
- 实时显示已选择的特征数量

#### 1.3 训练参数配置
- 预设配置选择
  - best_quality (最佳质量：更长训练时间，更好效果)
  - high_quality (高质量：平衡训练时间和效果)
  - good_quality (良好质量：较短训练时间，合理效果)
- 时间限制设置（默认值：best_quality 3600s, high_quality 1800s, good_quality 600s）
- 评估指标选择
  - 分类任务：accuracy, f1, precision, recall
  - 回归任务：rmse, mae, r2

#### 1.4 训练过程监控
- 实时进度展示
- 当前训练阶段显示
- 已完成模型的性能指标实时更新
- 训练日志实时展示

#### 1.5 训练结果展示
- 所有模型性能指标对比表格
- 最佳模型详细指标
- 模型UUID和存储信息
- 结果导出功能

### 2. 模型推理功能

#### 2.1 模型加载
- UUID输入框（支持粘贴）
- 模型基本信息显示
- 特征列要求提示

#### 2.2 推理数据处理
- Excel文件上传
- 数据列匹配检查
- 数据预览
- 缺失值检查提示

#### 2.3 推理结果展示
- 推理进度实时展示
- 结果数据表格展示
- 结果统计信息
- Excel导出功能

## API 接口设计

### 1. 训练相关接口

#### 文件上传
```
POST /api/upload/excel
- 功能：上传训练数据Excel文件
- 入参：Excel文件（multipart/form-data）
- 出参：
  {
    "file_id": "string",
    "total_rows": int,
    "columns": [
      {
        "name": "string",
        "type": "numerical|categorical",
        "missing_count": int,
        "unique_count": int,
        "sample_values": [...]
      }
    ],
    "preview_data": {
      "headers": ["col1", "col2", ...],
      "rows": [[val1, val2, ...], ...],
      "total_pages": int,
      "current_page": int
    }
  }
```

#### 分页获取数据
```
GET /api/data/{file_id}
- 功能：分页获取数据
- 入参：
  - page: int
  - page_size: int
- 出参：
  {
    "total_rows": int,
    "total_pages": int,
    "current_page": int,
    "data": [[val1, val2, ...], ...]
  }
```

#### 开始训练
```
POST /api/model/train
- 功能：启动模型训练任务
- 入参：
  {
    "file_id": "string",
    "feature_columns": ["col1", "col2", ...],
    "target_column": "string",
    "task_type": "regression|classification",
    "training_params": {
      "time_limit": int,
      "preset": "best_quality|high_quality|good_quality",
      "eval_metric": "string"
    }
  }
- 出参：
  {
    "task_id": "string",
    "websocket_url": "string"
  }
```

#### 训练进度WebSocket
```
WS /ws/training/{task_id}
- 功能：实时获取训练进度
- 推送消息格式：
  {
    "status": "running|completed|failed",
    "progress": float,
    "current_stage": "string",
    "log_message": "string",
    "model_metrics": {
      "model_name": {
        "accuracy": float,
        "f1": float,
        "precision": float,
        "recall": float,
        "rmse": float,
        "mae": float,
        "r2": float,
        ...
      }
    },
    "best_model": {
      "name": "string",
      "metrics": {...},
      "feature_importance": {
        "col1": float,
        "col2": float,
        ...
      }
    },
    "model_uuid": "string"  // 训练完成时返回
  }
```

### 2. 推理相关接口

#### 获取模型信息
```
GET /api/model/{model_uuid}
- 功能：获取模型详细信息
- 出参：
  {
    "model_info": {
      "task_type": "regression|classification",
      "feature_columns": [
        {
          "name": "string",
          "type": "numerical|categorical",
          "required": boolean
        }
      ],
      "target_column": "string",
      "metrics": {...},
      "created_at": "datetime"
    }
  }
```

#### 推理数据上传
```
POST /api/predict/upload
- 功能：上传推理数据
- 入参：
  {
    "model_uuid": "string",
    "file": Excel文件
  }
- 出参：
  {
    "prediction_id": "string",
    "columns_check": {
      "is_valid": boolean,
      "missing_columns": ["col1", ...],
      "extra_columns": ["col2", ...]
    }
  }
```

#### 执行推理
```
POST /api/predict/{prediction_id}
- 功能：执行模型推理
- 出参：
  {
    "task_id": "string",
    "websocket_url": "string"
  }
```

#### 推理进度WebSocket
```
WS /ws/prediction/{task_id}
- 功能：实时获取推理进度
- 推送消息格式：
  {
    "status": "running|completed|failed",
    "progress": float,
    "results": [
      {
        "input_features": {...},
        "prediction": "value"
      },
      ...
    ]
  }
```

#### 下载推理结果
```
GET /api/predict/download/{prediction_id}
- 功能：下载推理结果Excel文件
- 出参：Excel文件流
```

### 3. 数据库表设计

```sql
-- 训练任务表
CREATE TABLE training_tasks (
    task_id UUID PRIMARY KEY,
    file_path TEXT NOT NULL,
    feature_columns JSONB NOT NULL,
    target_column TEXT NOT NULL,
    training_params JSONB NOT NULL,
    status TEXT NOT NULL,
    progress FLOAT DEFAULT 0,
    model_uuid UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 模型表
CREATE TABLE models (
    model_uuid UUID PRIMARY KEY,
    model_path TEXT NOT NULL,
    feature_columns JSONB NOT NULL,
    target_column TEXT NOT NULL,
    metrics JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 推理任务表
CREATE TABLE prediction_tasks (
    prediction_id UUID PRIMARY KEY,
    model_uuid UUID REFERENCES models(model_uuid),
    file_path TEXT NOT NULL,
    status TEXT NOT NULL,
    result_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 目录结构
```
project/
├── frontend/                # Vue前端项目
│   ├── src/
│   │   ├── assets/         # 静态资源
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── router/         # 路由配置
│   │   ├── store/          # 状态管理
│   │   ├── utils/          # 工具函数
│   │   └── App.vue         # 根组件
│   ├── public/             # 公共资源
│   └── package.json        # 项目依赖
│
├── backend/                 # FastAPI后端项目
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── db/             # 数据库模型和工具
│   │   ├── models/         # Pydantic模型
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── tests/              # 测试文件
│   ├── alembic/            # 数据库迁移
│   ├── requirements.txt    # Python依赖
│   └── main.py            # 应用入口
│
├── storage/                # 数据存储目录
│   ├── models/            # 训练模型存储
│   ├── uploads/           # 上传文件临时存储
│   └── results/           # 预测结果存储
│
├── docker/                 # Docker配置
│   ├── frontend/          # 前端Docker配置
│   ├── backend/           # 后端Docker配置
│   └── docker-compose.yml # Docker编排配置
│
└── README.md              # 项目文档
```

## 部署说明

### 1. 环境要求
- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- Docker & Docker Compose (可选)

### 2. 开发环境设置

#### 2.1 后端设置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
cd backend
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库等参数

# 初始化数据库
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

#### 2.2 前端设置
```bash
# 安装依赖
cd frontend
npm install

# 配置环境变量
cp .env.example .env.local
# 编辑 .env.local 文件配置API地址等

# 启动开发服务器
npm run dev
```

### 3. Docker部署

#### 3.1 使用Docker Compose
```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 3.2 单独服务部署
```bash
# 构建并运行后端
cd docker/backend
docker build -t automl-backend .
docker run -d -p 8000:8000 automl-backend

# 构建并运行前端
cd docker/frontend
docker build -t automl-frontend .
docker run -d -p 80:80 automl-frontend
```

### 4. 生产环境注意事项

#### 4.1 性能优化
- 配置 PostgreSQL 性能参数
- 使用 Nginx 作为前端静态文件服务器
- 配置适当的 worker 进程数

#### 4.2 安全配置
- 启用 HTTPS
- 配置跨域策略
- 设置适当的文件上传限制
- 配置数据库访问权限

#### 4.3 监控
- 配置日志收集
- 设置性能监控
- 配置告警机制

### 5. 常见问题排查
1. 数据库连接问题
   - 检查数据库配置参数
   - 确认数据库服务状态
   - 验证网络连接

2. 文件上传问题
   - 检查存储目录权限
   - 确认文件大小限制配置
   - 验证临时文件清理机制

3. 模型训练问题
   - 检查 GPU 可用性
   - 确认内存使用情况
   - 验证模型存储空间

## 参考资料
- AutoGluon文档: https://auto.gluon.ai/stable/tutorials/tabular/tabular-quick-start.html
- FastAPI文档: https://fastapi.tiangolo.com/
- Vue.js文档: https://vuejs.org/