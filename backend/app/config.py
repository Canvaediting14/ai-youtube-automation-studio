from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AI YouTube Automation Studio"
    environment: str = "development"
    secret_key: str = "change-me"
    database_url: str = "sqlite:///./data/studio.db"
    frontend_origin: str = "http://localhost:5173"
    backend_origin: str = "http://localhost:8000"
    auto_publish: bool = False
    timezone: str = "Asia/Kolkata"
    daily_long_videos: int = 2
    daily_shorts: int = 3
    long_minutes: float = 6.5
    long_scenes: int = 42
    short_minutes: float = 1.5
    short_scenes: int = 18
    publish_hour: int = 10
    publish_minute: int = 0
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/youtube/callback"
    google_token_file: str = "/data/youtube-token.json"
    youtube_privacy_status: str = "private"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    fal_key: str = ""
    elevenlabs_api_key: str = ""
    tts_provider: str = "elevenlabs"
    script_provider: str = "openai"
    visual_provider: str = "fal"
    music_provider: str = "none"
    ffmpeg_path: str = "ffmpeg"
    media_dir: str = "/media"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
