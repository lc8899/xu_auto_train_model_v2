backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── train.py      # 训练相关接口
│   │   │   └── predict.py    # 预测相关接口
│   │   └── router.py         # API路由注册
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # 配置加载
│   │   └── errors.py         # 错误处理
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py          # 数据库基础设置
│   │   └── models.py        # SQLAlchemy模型
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train.py         # 训练相关的Pydantic模型
│   │   └── predict.py       # 预测相关的Pydantic模型
│   ├── services/
│   │   ├── __init__.py
│   │   ├── train.py         # 训练业务逻辑
│   │   └── predict.py       # 预测业务逻辑
│   └── utils/
│       ├── __init__.py
│       └── file_handler.py  # 文件处理工具
├── storage/
│   ├── models/             # 模型存储
│   ├── uploads/            # 上传文件
│   └── results/            # 预测结果
├── .env
├── .env.example
├── main.py
└── requirements.txt 