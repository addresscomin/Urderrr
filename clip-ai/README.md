# ZM Clip AI

A separate web AI clipping service in this repository. The existing GuardClear Android project remains untouched.

## Features in this build
- Supabase email/password signup and login.
- Per-account allowance: 20 finished clips per calendar month.
- Authenticated uploads and background Redis/RQ processing.
- Faster-Whisper transcription in 30-minute audio chunks.
- Automatic candidate scoring and non-overlapping highlight selection.
- 9:16 vertical MP4 output (20–50 second target) with selectable burned-in captions.
- Three caption looks: bold yellow, clean white and creator pink.
- Private Supabase Storage, signed downloads, job history and live quota display.

## Run locally
1. Use a Supabase project and apply the migrations in supabase/schema.sql (or run the already-applied project migrations).
2. In Supabase Dashboard → Project Settings → API Keys, copy the publishable/anon key and the server-only service-role/secret key. Never put the server key in Vite or expose it publicly.
3. Copy .env.example to .env; set SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.
4. Keep VITE_API_BASE=http://localhost:8000 for local use.
5. Run docker compose up --build.
6. Open http://localhost:5173. API health: http://localhost:8000/health.

## YouTube and source rights
This build accepts uploaded files that the user owns or is authorized to process. It does not download arbitrary public YouTube URLs or other people's livestreams. A creator can export their own stream recording and upload it. A future integration must use an official, creator-authorized export/OAuth flow.

## Deployment
- The frontend is a static Nginx container built from Vite. Set the three VITE_* values at build time.
- Deploy the API and worker as separate long-running Docker services with a shared persistent volume and Redis. Set SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, REDIS_URL, DATA_DIR and MAX_UPLOAD_GB as server-side environment variables.
- Set VITE_API_BASE to the public API HTTPS origin before building the frontend.
- Configure API CORS to the exact frontend origin before public launch.
- A free web host generally sleeps, limits disk/CPU, or restricts long jobs. A 10-hour stream needs a persistent worker, substantial RAM/CPU, disk space and bandwidth; no service can honestly promise unlimited free 10-hour processing.

## Quota
The Postgres quota claim is atomic and caps completed-clip reservations at 20 per user per calendar month. The frontend displays the current remaining count. A failed job can consume a reservation if it fails after claiming one; production billing should add a reservation-release/refund path.

## Security
- Service-role credentials are backend-only.
- User job history is filtered by authenticated user ID.
- Clips are stored in a private bucket and served using expiring signed URLs.
- Do not upload recordings unless you own them or have permission.