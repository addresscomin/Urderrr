# Focus Guard Pro v8.0 (`com.me.focusguard`)

An uncompromising, modern phone discipline and habit enforcement system with a **Conversational Voice AI Assistant**, **Deep Focus Pomodoro Mode**, **Discipline Analytics**, **Prayer Guard**, **Routine Timetable**, and **Strict Device Protection**.

---

## 🌟 What's New in v8.0 Pro

### 1. 🎙️ Interactive Conversational Voice AI Assistant
- **Dedicated Voice AI Screen**: Featuring an animated pulsing voice orb (`VoiceOrbView`) that dynamically responds to your speech.
- **Natural Language Understanding (Hindi, Urdu, English)**:
  - *"Kitna screen time bacha hai?"* ➔ Instant status of minutes used vs remaining limit.
  - *"Agli namaz kab hai?"* ➔ Tells next prayer name, time, and remaining minutes.
  - *"Task mark done"* ➔ Automatically checks and marks your running routine task complete via voice!
  - *"Mujhe motivate karo"* ➔ Speaks powerful discipline and stoic mindset quotes.
  - *"Discipline score kya hai?"* ➔ Reports your real-time daily discipline percentage and streak.
  - *"Focus mode on karo"* ➔ Quickly opens and launches Deep Focus Mode.
- **One-Tap Suggestion Chips & Text Input**: Interact effortlessly without speaking if in a quiet library or meeting.
- **Passive Voice Guard & Lie Detection**: Still runs silently in the background; if a user claims a prayer or routine was done without proof, it issues warnings and progressive lock penalties.

### 2. 🎨 Ultra-Modern UI Design System
- **Deep Obsidian & Slate Dark Theme**: `#09090F` base with neon indigo (`#6366F1`) and emerald (`#10B981`) accents.
- **Hero Circular Screen Time Gauge**: Animated canvas progress meter showing live minutes used and remaining.
- **4-Tile Quick Stats Bar**: Real-time display of **Streak Days** (🔥), **Discipline Score** (⚡), **Prayers Done** (🕌), and **Tasks Completed** (📋).
- **Interactive Action Cards**: Quick access to Voice AI, Focus Timer, Prayer Guard, Timetable, and Analytics.
- **Dynamic Quotes Banner**: 40+ curated wisdom and discipline quotes rotating daily.

### 3. ⏱️ Deep Focus / Pomodoro Mode
- Distraction-free study and deep work sessions (15m, 25m, 45m, 60m).
- **Procedural Ambient Audio Synthesizer**: Generates **Gentle Rain 🌧️**, **White Noise 💨**, or **Zen 432Hz Pulse 🧘** directly on-device using `AudioTrack` with zero external audio files.

### 4. 📊 Discipline Analytics & Streaks
- **Daily Discipline Score (0–100%)**: Evaluated across 4 pillars:
  1. Screen time adherence (Max 30 pts)
  2. Prayer timeliness (Max 30 pts)
  3. Routine task completion (Max 30 pts)
  4. Honesty & Voice integrity (Max 10 pts)
- **7-Day Trend Bar Chart**: Custom canvas bar chart comparing weekly discipline consistency.
- **Streak Tracker**: Tracks consecutive days with high discipline scores.

### 5. ⚙️ In-App Rule Configuration (Before Activation)
- Customize your **Daily Screen Time Limit** (e.g. 120m, 180m, 240m, 300m) directly in the app before locking it down.
- Set custom **Sleep Schedule** hours (e.g. 10:00 PM to 6:00 AM).
- Once you tap **ACTIVATE (permanent)**, all settings become permanent and unchangeable.

---

## 🔒 Core Protection & Modules

1. **Daily Limit Lock**: When the daily screen time is exhausted, the phone completely locks until midnight (calls only).
2. **Sleep Lock**: Strict lockdown during bedtime hours.
3. **Prayer Guard**: Live solar calculations for all 5 prayers, adhan reminders, and camera photo proof verification.
4. **Daily Timetable**: Scheduled time blocks for study/work. Missed tasks enforce lock penalties.
5. **Anti-Tamper Hardening**: Blocks Android Settings and package installers. Supports Android Device Owner for uninstallation prevention without factory reset.

---

## 🚀 How to Build & Install

### Option A: GitHub Actions (Recommended)
1. Push this repository to your GitHub account.
2. Go to **Actions** > **Build APK** > Click **Run workflow**.
3. Once completed, download the signed APK from **Artifacts** (`DisciplineGuard-apk`).
4. Install on your Android phone (signed with fixed key `fixed-debug.keystore` for seamless updates).

### Option B: Local Android Studio / CLI
Run in terminal:
```bash
./gradlew assembleDebug
```
The APK will be generated at:
`app/build/outputs/apk/debug/app-debug.apk`

---

## 📱 Initial Setup Guide

1. Open **Focus Guard Pro** on your phone.
2. Grant the required permissions shown on the dashboard:
   - Microphone (for Voice AI Assistant & Voice Guard)
   - Accessibility Service (block engine)
   - Display Over Other Apps (overlay lock)
   - Device Admin (phone locking)
   - Battery Optimization Disabled & Exact Alarms
3. Configure your preferred daily limit, sleep hours, prayer times, and routine tasks.
4. (Optional for Device Owner):
   ```bash
   adb shell dpm set-device-owner com.me.focusguard/com.me.discipline.AdminReceiver
   ```
5. Tap **ACTIVATE (permanent)** and type `LOCK`.
