from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from zoneinfo import ZoneInfo
from .config import settings
from .db import SessionLocal
from .models import Job
from .services.pipeline import run_generation

scheduler=BackgroundScheduler(timezone=settings.timezone)

def language_for(slot: int):
    langs=["English","Hindi","Hinglish"]
    day=datetime.now(ZoneInfo(settings.timezone)).timetuple().tm_yday
    return langs[(day+slot)%len(langs)]

def create_daily_jobs():
    db=SessionLocal()
    try:
        today=datetime.now(ZoneInfo(settings.timezone)).date()
        existing=db.query(Job).filter(Job.created_at >= datetime.combine(today, datetime.min.time())).count()
        if existing: return
        items=[]
        for i in range(settings.daily_long_videos):
            items.append(("long",language_for(i),settings.long_minutes,settings.long_scenes))
        for i in range(settings.daily_shorts):
            items.append(("short",language_for(i+2),settings.short_minutes,settings.short_scenes))
        for idx,(fmt,lang,dur,scenes) in enumerate(items):
            db.add(Job(title=f"Trending {fmt.title()} Video - {lang}",format=fmt,language=lang,
                       duration_minutes=dur,scenes=scenes,status="queued"))
        db.commit()
    finally: db.close()

def process_queued():
    db=SessionLocal()
    try: ids=[j.id for j in db.query(Job).filter(Job.status=="queued").order_by(Job.id).limit(1).all()]
    finally: db.close()
    for job_id in ids:
        db=SessionLocal()
        try:
            job=db.get(Job,job_id)
            if not job: continue
            try:
                run_generation(job); db.merge(job); db.commit()
            except Exception as e:
                job.status="failed"; job.error=str(e); job.log=(job.log or "")+f"\nERROR: {e}"
                db.merge(job); db.commit()
        finally: db.close()

def start_scheduler():
    if scheduler.running: return
    scheduler.add_job(create_daily_jobs,CronTrigger(hour=0,minute=5,timezone=settings.timezone),id="daily-jobs",replace_existing=True)
    scheduler.add_job(process_queued,"interval",minutes=1,id="job-worker",replace_existing=True)
    scheduler.start()
