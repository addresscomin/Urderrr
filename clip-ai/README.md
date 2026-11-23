# ZM Clip AI

A separate, web-based AI clipping service inside this repository. The existing GuardClear Android project is untouched.

## Current MVP
- Supabase email/password authentication.
- Per-user monthly quota reservation (20 clips).
- Authenticated video upload.
- Redis/RQ background processing.
- Faster-Whisper transcription, highlight-window ranking and FFmpeg vertical MP4 rendering.
- Clips and SRT captions uploaded to a private Supabase Storage bucket.
- User-scoped job history and signed download URLs.

## Source rights and YouTube
The app accepts video files that the user owns or is authorized to process. A pasted public YouTube URL is **not** downloaded: YouTube's API does not provide arbitrary source-file downloads, and platform terms/copyright restrictions apply. A creator can export their own livestream recording and upload it. A future creator-authorized integration can be added using the platform's supported OAuth/export flow.

## Run locally
1. Create a Supabase project.
2. Run `supabase/schema.sql` in Supabase SQL Editor.
3. Create a private Storage bucket named `clips` (the SQL attempts to create it too).
4. Copy `.env.example` to `.env` and fill Supabase URL, anon key and service-role key.
5. Run `docker compose up --build`.
6. Open http://localhost:5173 and register a user.

The API is at http://localhost:8000/health.

## Notes
- The 20-clip quota is per authenticated user per calendar month and is enforced atomically in Postgres.
- Video processing requires CPU/RAM and storage. Ten-hour livestream processing is supported as a target workflow, but a production deployment needs large upload limits, chunked audio transcription, durable object storage, and worker capacity sized for long recordings. The initial worker is a functional MVP, not a promise of unlimited free compute.
- Never expose the Supabase service-role key in frontend code.
