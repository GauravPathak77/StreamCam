# StreamCam — USB Webcam to RTSP (with bore tunnel)

A lightweight Python script that streams a Windows USB webcam to a local RTSP server (MediaMTX) and optionally exposes it globally via a free `bore.pub` tunnel.

---

## ✅ What this project does

- Uses **FFmpeg** to capture a Windows DirectShow webcam and stream it to RTSP.
- Uses **MediaMTX** as the local RTSP server (listens on `rtsp://localhost:8554/webcam`).
- Optionally uses **bore.pub** to tunnel the RTSP stream to the public internet (global URL like `rtsp://bore.pub:<port>/webcam`).

---

## 📁 Directory structure

```
StreamCam/
├── main.py               # Main streaming script
├── requirements.txt      # List of Python dependencies (none required)
├── README.md             # This file
├── .gitignore            # Recommended git ignore patterns
├── mediamtx_v1.15.5_windows_amd64/  # (optional) bundled MediaMTX binary folder
└── bore-v0.6.0-i686-pc-windows-msvc/ # (optional) bundled bore binary folder
```

> ✅ If you don’t want to commit the binaries, keep them locally and they’ll still be detected at runtime.

---

## 🛠 Prerequisites

### Required tools (not Python packages)

- **FFmpeg** (needed to stream from your webcam)
  - Download (Windows): https://www.gyan.dev/ffmpeg/builds/

- **MediaMTX** (RTSP server)
  - Download: https://github.com/bluenviron/mediamtx/releases
  - Place `mediamtx.exe` in this project folder, or keep the extracted folder `mediamtx_v1.15.5_windows_amd64/` next to `main.py`.

- **bore** (optional, for global access)
  - Download: https://github.com/ekzhang/bore/releases
  - Place `bore.exe` in this project folder, or keep the extracted folder `bore-v0.6.0-i686-pc-windows-msvc/` next to `main.py`.

### Optional Python environment

This script uses only the Python standard library, so there are no pip requirements.
However, it is best practice to run it inside a virtual environment:

```powershell
python -m venv cam_env
& .\cam_env\Scripts\Activate.ps1
```

---

## ▶️ Running the script

From this folder, run:

```powershell
python main.py
```

The script will:
1. Check that **FFmpeg** is installed.
2. Optionally start **MediaMTX** (if not already running).
3. Offer to start a **bore.pub tunnel** for global access.
4. Start streaming the webcam to `rtsp://localhost:8554/webcam`.

---

## 🌐 Local and Global RTSP URLs

- **Local RTSP (LAN/local machine):**
  - `rtsp://localhost:8554/webcam`
  - `rtsp://<your-local-ip>:8554/webcam`

- **Global RTSP (via bore.pub tunnel):**
  - `rtsp://bore.pub:<port>/webcam`
  - The `<port>` is printed by the script when the tunnel starts.

> 🔎 Tip: Use VLC to test the stream (`Media → Open Network Stream`). If you use the global URL, set `Input/Codecs → RTP over RTSP (TCP)` for best compatibility.

---

## 🔧 Common tweaks

- Change the webcam device name by updating the `selected_device` variable in `main.py`.
- Change default resolution or bitrate in `stream_webcam()`.

---

## ✅ Troubleshooting

- ❌ **FFmpeg not found:** Install FFmpeg and ensure `ffmpeg` is in your PATH.
- ❌ **MediaMTX doesn’t start:** Make sure `mediamtx.exe` is present and not blocked by antivirus.
- ❌ **bore tunnel not working:** Ensure `bore.exe` is present and your network allows outbound connections.
