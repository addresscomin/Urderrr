import os, uuid, pathlib
from datetime import datetime, timezone
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from redis import Redis
from rq import Queue

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
DATA_DIR = pathlib.Path(os.getenv("DATA_DIR", "/data"))
MAX_UPLOAD_GB = int(os.getenv("MAX_UPLOAD_GB", "8"))
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
queue = Queue("clips", connection=redis)
app = FastAPI(title="ZM Clip AI API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

def current_user(authorization: str | None):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Sign in required")
    token = authorization.split(" ", 1)[1].strip()
    try:
        result = supabase.auth.get_user(token)
        if not result or not result.user:
            raise ValueError("No user")
        return result.user
    except Exception:
        raise HTTPException(401, "Invalid or expired session")

@app.get("/health")
def health():
    return {"ok": True, "service": "zm-clip-ai-api"}

@app.post("/api/jobs")
async def create_job(file: UploadFile = File(...), authorization: str | None = Header(default=None)):
    user = current_user(authorization)
    suffix = pathlib.Path(file.filename or "source.mp4").suffix.lower()
    if suffix not in {".mp4", ".mov", ".mkv", ".webm", ".m4v"}:
        raise HTTPException(415, "Upload MP4, MOV, MKV, WEBM or M4V")
    job_id = str(uuid.uuid4())
    upload_dir = DATA_DIR / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    target = upload_dir / f"{job_id}{suffix}"
    max_bytes = MAX_UPLOAD_GB * 1024 * 1024 * 1024
    size = 0
    try:
        with target.open("wb") as out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(413, f"Maximum upload size is {MAX_UPLOAD_GB} GB")
                out.write(chunk)
        if size == 0:
            raise HTTPException(400, "The uploaded file is empty")
        quota = supabase.rpc("claim_monthly_clip_quota", {"p_user_id": str(user.id)}).execute()
        if quota.data is not True:
            target.unlink(missing_ok=True)
            raise HTTPException(429, "Monthly free quota reached (20 clips). Try next month.")
        supabase.table("clip_jobs").insert({
            "id": job_id, "user_id": str(user.id), "status": "queued",
            "source_name": file.filename or "video", "source_path": str(target),
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        queue.enqueue("worker.process_job", job_id, job_timeout=60 * 60 * 12, result_ttl=3600, failure_ttl=86400)
        return {"job_id": job_id, "status": "queued", "quota_reserved": 1}
    except HTTPException:
        target.unlink(missing_ok=True)
        raise
    except Exception as exc:
        target.unlink(missing_ok=True)
        raise HTTPException(500, f"Could not queue video: {str(exc)[:180]}")

@app.get("/api/jobs")
def list_jobs(authorization: str | None = Header(default=None)):
    user = current_user(authorization)
    result = supabase.table("clip_jobs").select("id,status,source_name,error,created_at").eq("user_id", str(user.id)).order("created_at", desc=True).limit(30).execute()
    jobs = result.data or []
    for job in jobs:
        clips = supabase.table("clips").select("id,title,duration_seconds,storage_path,created_at").eq("job_id", job["id"]).order("created_at").execute()
        job["clips"] = []
        for clip in clips.data or []:
            signed = supabase.storage.from_("clips").create_signed_url(clip["storage_path"], 3600)
            job["clips"].append({**clip, "download_url": signed.get("signedURL") or signed.get("signedUrl")})
    return {"jobs": jobs}
