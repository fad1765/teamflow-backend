from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# PostgreSQL 連線
DATABASE_URL = "postgresql://postgres:asdw4568@localhost:5432/teamflow_db"

# 建立 engine（資料庫連線核心）
engine = create_engine(DATABASE_URL)

# Session（每次 request 使用）
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 所有 Model 的 Base
Base = declarative_base()