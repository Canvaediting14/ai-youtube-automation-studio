from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from .db import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    format = Column(String(20), nullable=False)
    language = Column(String(20), nullable=False)
    status = Column(String(30), default="queued", index=True)
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_minutes = Column(Float, default=1.5)
    scenes = Column(Integer, default=18)
    output_path = Column(String(600), nullable=True)
    youtube_video_id = Column(String(100), nullable=True)
    error = Column(Text, nullable=True)
    log = Column(Text, default="")

class AppSetting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
