from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pathlib import Path
from .config import settings
from .db import Base, engine, get_db
from .models import Job
from .schemas import JobCreate, SettingsUpdate
from .scheduler import start_scheduler
from .services.youtube import oauth_flow, save_credentials
import json, os

Path(settings.media_dir).mkdir(parents=True,exist_ok=True)
Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.app_name,version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_origin],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.on_event("startup")
def startup(): start_scheduler()

@app.get("/api/health")
def health(): return {"ok":True,"app":settings.app_name}

@app.get("/api/dashboard")
def dashboard(db:Session=Depends(get_db)):
    jobs=db.query(Job).order_by(Job.id.desc()).limit(20).all()
    return {"counts":{s:db.query(Job).filter(Job.status==s).count() for s in ["queued","generating","uploading","ready","published","failed"]},
            "jobs":[serialize(j) for j in jobs],"auto_publish":settings.auto_publish}

def serialize(j):
    return {"id":j.id,"title":j.title,"format":j.format,"language":j.language,"status":j.status,
            "duration_minutes":j.duration_minutes,"scenes":j.scenes,"output_path":j.output_path,
            "youtube_video_id":j.youtube_video_id,"error":j.error,"log":j.log,"created_at":str(j.created_at)}

@app.get("/api/jobs")
def list_jobs(db:Session=Depends(get_db)):
    return [serialize(j) for j in db.query(Job).order_by(Job.id.desc()).limit(100).all()]

@app.post("/api/jobs")
def create_job(payload:JobCreate,db:Session=Depends(get_db)):
    job=Job(**payload.model_dump(),status="queued")
    db.add(job); db.commit(); db.refresh(job)
    return serialize(job)

@app.post("/api/jobs/{job_id}/retry")
def retry_job(job_id:int,db:Session=Depends(get_db)):
    job=db.get(Job,job_id)
    if not job: raise HTTPException(404,"Job not found")
    job.status="queued"; job.error=None; db.commit()
    return serialize(job)

@app.get("/api/settings")
def get_settings():
    return {"auto_publish":settings.auto_publish,"daily_long_videos":settings.daily_long_videos,
            "daily_shorts":settings.daily_shorts,"timezone":settings.timezone,
            "youtube_privacy_status":settings.youtube_privacy_status,
            "google_oauth_configured":bool(settings.google_client_id and settings.google_client_secret)}

@app.put("/api/settings")
def update_settings(payload:SettingsUpdate):
    # Runtime config is immutable by design; persist changes through deployment environment.
    raise HTTPException(501,"Edit deployment environment variables and restart the service to change settings.")

@app.get("/api/youtube/status")
def youtube_status():
    return {"connected":Path(settings.google_token_file).exists(),
            "oauth_configured":bool(settings.google_client_id and settings.google_client_secret)}

@app.get("/api/youtube/connect")
def youtube_connect():
    try:
        flow=oauth_flow()
        url,state=flow.authorization_url(access_type="offline",include_granted_scopes="true",prompt="consent")
        return RedirectResponse(url)
    except Exception as e: raise HTTPException(400,str(e))

@app.get("/api/youtube/callback")
def youtube_callback(request:Request):
    try:
        flow=oauth_flow()
        flow.fetch_token(authorization_response=str(request.url))
        save_credentials(flow.credentials)
        return {"connected":True,"message":"YouTube account connected. You may close this tab."}
    except Exception as e: raise HTTPException(400,str(e))
