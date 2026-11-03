from pydantic import BaseModel, Field
from typing import Optional, Literal

class JobCreate(BaseModel):
    title: str = Field(min_length=4, max_length=300)
    format: Literal["long", "short"]
    language: Literal["English", "Hindi", "Hinglish"]
    duration_minutes: float = Field(ge=0.5, le=30)
    scenes: int = Field(ge=3, le=100)

class SettingsUpdate(BaseModel):
    auto_publish: Optional[bool] = None
    daily_long_videos: Optional[int] = Field(default=None, ge=0, le=10)
    daily_shorts: Optional[int] = Field(default=None, ge=0, le=20)
    timezone: Optional[str] = None
    youtube_privacy_status: Optional[Literal["private", "unlisted", "public"]] = None
