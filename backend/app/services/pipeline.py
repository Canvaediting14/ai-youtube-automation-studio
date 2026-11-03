from pathlib import Path
from ..config import settings
from .providers import generate_script, generate_voice, generate_visual
from .render import render_slideshow, create_thumbnail
from .youtube import upload_video

def run_generation(job):
    media=Path(settings.media_dir)/f"job-{job.id}"
    media.mkdir(parents=True,exist_ok=True)
    job.status="generating"; job.log=(job.log or "")+"\nGenerating script..."
    from ..db import SessionLocal
    with SessionLocal() as db:
        db.merge(job); db.commit()
    script=generate_script(job.title,job.language,job.duration_minutes,job.scenes)
    narration=script.get("narration","")
    if not narration: raise RuntimeError("Script provider returned no narration.")
    voice=generate_voice(narration,str(media/"narration.mp3"),job.language)
    aspect="portrait" if job.format=="short" else "landscape"
    images=[]
    scenes=script.get("scenes",[])
    if len(scenes)<1: raise RuntimeError("Script provider returned no visual scenes.")
    for idx, scene in enumerate(scenes[:job.scenes]):
        images.append(generate_visual(scene.get("visual_prompt",job.title),str(media/f"scene-{idx:03d}.jpg"),aspect))
    video=render_slideshow(images,voice,str(media/"final.mp4"),aspect)
    thumb=create_thumbnail(images[0],script.get("title",job.title),str(media/"thumbnail.jpg"))
    if settings.auto_publish:
        job.status="uploading"
        from ..db import SessionLocal
        with SessionLocal() as db:
            db.merge(job); db.commit()
        video_id=upload_video(video,script.get("title",job.title),script.get("description",""),settings.youtube_privacy_status,thumb)
        job.youtube_video_id=video_id
    job.output_path=video
    job.status="published" if job.youtube_video_id else "ready"
    job.log=(job.log or "")+"\nGeneration complete."
    return job
