import os, pathlib, subprocess
from datetime import datetime, timezone
from supabase import create_client
from faster_whisper import WhisperModel

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
DATA_DIR = pathlib.Path(os.getenv("DATA_DIR", "/data"))
db = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
_model = None

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def duration_seconds(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)], text=True)
    return float(out.strip())

def choose_windows(segments, total, limit=5):
    candidates = []
    cues = ("because", "secret", "important", "never", "always", "mistake", "amazing", "crazy", "why", "how", "best", "worst", "remember", "actually", "finally", "incredible", "problem", "solution", "listen")
    for seg in segments:
        start = max(0, float(seg.start) - 7)
        end = min(total, start + 35)
        if end - start < 20:
            continue
        text = (seg.text or "").strip()
        score = min(len(text) / 220, 1.0) + sum(0.22 for cue in cues if cue in text.lower())
        score += min(max(float(seg.end) - float(seg.start), 0) / 12, 0.4)
        candidates.append({"start": start, "end": end, "score": score, "text": text})
    candidates.sort(key=lambda x: x["score"], reverse=True)
    chosen = []
    for item in candidates:
        if all(item["end"] <= old["start"] or item["start"] >= old["end"] for old in chosen):
            chosen.append(item)
        if len(chosen) >= limit:
            break
    return sorted(chosen, key=lambda x: x["start"])

def make_srt(words, start, end, out_path):
    lines, idx, chunk = [], 1, []
    def stamp(value):
        ms = int(max(0, value) * 1000)
        h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    for word in words:
        t = float(word.start)
        if start <= t <= end:
            chunk.append(word)
            if len(chunk) >= 7 or word.word.strip().endswith((".", "?", "!", ",")):
                a, b = max(0, chunk[0].start - start), max(0.1, chunk[-1].end - start)
                text = " ".join(w.word.strip() for w in chunk).replace("--", "—")
                lines += [str(idx), f"{stamp(a)} --> {stamp(b)}", text, ""]
                idx += 1; chunk = []
    if chunk:
        a, b = max(0, chunk[0].start - start), max(0.1, chunk[-1].end - start)
        lines += [str(idx), f"{stamp(a)} --> {stamp(b)}", " ".join(w.word.strip() for w in chunk), ""]
    pathlib.Path(out_path).write_text("\n".join(lines), encoding="utf-8")

def process_job(job_id):
    global _model
    row = db.table("clip_jobs").select("*").eq("id", job_id).single().execute().data
    source = pathlib.Path(row["source_path"])
    out_dir = DATA_DIR / "outputs" / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    created = 0
    try:
        db.table("clip_jobs").update({"status": "processing"}).eq("id", job_id).execute()
        total = duration_seconds(source)
        if total < 20:
            raise ValueError("Video must be at least 20 seconds long")
        if _model is None:
            _model = WhisperModel("small", device="cpu", compute_type="int8")
        audio = out_dir / "audio.wav"
        run(["ffmpeg", "-y", "-i", str(source), "-vn", "-ac", "1", "-ar", "16000", str(audio)])
        segments, info = _model.transcribe(str(audio), word_timestamps=True, vad_filter=True)
        segments = list(segments)
        words = [w for seg in segments for w in (seg.words or [])]
        windows = choose_windows(segments, total)
        if not windows:
            windows = [{"start": s, "end": min(total, s + 30), "score": 0.1, "text": "Highlight"} for s in range(0, max(1, int(total - 20)), 45)][:5]
        for n, clip in enumerate(windows, 1):
            # Quota is charged per finished clip, not per source video.
            quota = db.rpc("claim_monthly_clip_quota", {"p_user_id": row["user_id"]}).execute()
            if quota.data is not True:
                break
            start, end = clip["start"], min(clip["end"], total)
            mp4 = out_dir / f"clip-{n:02}.mp4"
            srt = out_dir / f"clip-{n:02}.srt"
            make_srt(words, start, end, srt)
            subtitle_filter = f"subtitles={srt}:force_style='FontName=DejaVu Sans,FontSize=18,Bold=1,Outline=3,Shadow=1,Alignment=2,MarginV=220'"
            run(["ffmpeg", "-y", "-ss", str(start), "-i", str(source), "-t", str(end-start),
                 "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,{subtitle_filter}",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(mp4)])
            storage_path = f"{row['user_id']}/{job_id}/clip-{n:02}.mp4"
            db.storage.from_("clips").upload(storage_path, mp4.read_bytes(), {"content-type": "video/mp4", "upsert": "true"})
            srt_path = f"{row['user_id']}/{job_id}/clip-{n:02}.srt"
            db.storage.from_("clips").upload(srt_path, srt.read_bytes(), {"content-type": "application/x-subrip", "upsert": "true"})
            db.table("clips").insert({"job_id": job_id, "user_id": row["user_id"], "title": f"AI Highlight {n}", "duration_seconds": round(end-start, 2), "storage_path": storage_path, "captions_path": srt_path, "score": round(clip["score"], 3)}).execute()
            created += 1
        if created == 0:
            raise ValueError("No clip quota remaining or no suitable highlights were found")
        db.table("clip_jobs").update({"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}).eq("id", job_id).execute()
    except Exception as exc:
        db.table("clip_jobs").update({"status": "failed", "error": str(exc)[:500]}).eq("id", job_id).execute()
        raise
