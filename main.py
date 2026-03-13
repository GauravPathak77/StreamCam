import subprocess
import sys
import time
import os
import re
import threading
from pathlib import Path

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found! Please install FFmpeg first.")
        print("Download from: https://www.gyan.dev/ffmpeg/builds/")
        return False

def list_video_devices():
    """List all available video devices"""
    print("\n🔍 Detecting video devices...\n")
    try:
        result = subprocess.run(
            ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'],
            capture_output=True,
            text=True
        )
        
        output = result.stderr if result.stderr else result.stdout
        devices = []
        capture = False
        
        for line in output.split('\n'):
            if 'DirectShow video devices' in line:
                capture = True
                continue
            if 'DirectShow audio devices' in line:
                break
            if capture and '"' in line:
                start = line.find('"')
                end = line.find('"', start + 1)
                if start != -1 and end != -1:
                    device_name = line[start+1:end]
                    devices.append(device_name)
        
        if devices:
            print("📹 Found video devices:")
            for i, device in enumerate(devices, 1):
                print(f"  {i}. {device}")
            return devices
        else:
            print("❌ No video devices found!")
            return []
            
    except Exception as e:
        print(f"❌ Error listing devices: {e}")
        return []

def check_mediamtx():
    """Check if MediaMTX is running on port 8554"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8554))
        sock.close()
        return result == 0
    except:
        return False

def find_mediamtx():
    """Find mediamtx.exe in current folder or extracted folder"""
    if Path('mediamtx.exe').exists():
        return 'mediamtx.exe'
    extracted = Path('mediamtx_v1.15.5_windows_amd64/mediamtx.exe')
    if extracted.exists():
        return str(extracted)
    return None

def start_mediamtx():
    """Start MediaMTX server"""
    print("\n🚀 Starting MediaMTX RTSP server...")

    mediamtx_path = find_mediamtx()

    if not mediamtx_path:
        print("\n❌ mediamtx.exe not found!")
        print("   Looked in:")
        print("   - mediamtx.exe (same folder as script)")
        print("   - mediamtx_v1.15.5_windows_amd64/mediamtx.exe")
        print("📥 Download from: https://github.com/bluenviron/mediamtx/releases")
        return None

    print(f"   Found: {mediamtx_path}")

    mediamtx_abs = str(Path(mediamtx_path).resolve())
    mediamtx_dir = str(Path(mediamtx_abs).parent)

    try:
        process = subprocess.Popen(
            [mediamtx_abs],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=mediamtx_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        if check_mediamtx():
            print("✅ MediaMTX server started successfully on port 8554")
            return process
        else:
            print("❌ MediaMTX failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting MediaMTX: {e}")
        return None

# ─────────────────────────────────────────────
#  BORE TUNNEL
# ─────────────────────────────────────────────

def find_bore():
    """Find bore.exe in current folder, extracted folder, or PATH"""
    if Path('bore.exe').exists():
        return 'bore.exe'
    extracted = Path('bore-v0.6.0-i686-pc-windows-msvc/bore.exe')
    if extracted.exists():
        return str(extracted)
    try:
        subprocess.run(['bore', '--version'], capture_output=True, check=True)
        return 'bore'
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def verify_bore_tunnel(host, port, timeout=5):
    """Verify the bore tunnel is reachable by attempting a TCP connection"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def start_bore_tunnel(local_port=8554):
    """Start bore tunnel on RTSP port for global access"""
    bore_cmd = find_bore()
    
    if not bore_cmd:
        print("\n❌ bore.exe not found!")
        print("   Looked in:")
        print("   - bore.exe (same folder as script)")
        print("   - bore-v0.6.0-i686-pc-windows-msvc/bore.exe")
        print("📥 Download from: https://github.com/ekzhang/bore/releases")
        return None, None

    print(f"\n🌍 Starting bore tunnel on port {local_port} (RTSP)...")
    print(f"   Using: {bore_cmd}")

    public_port_event = threading.Event()
    public_port_holder = [None]

    def read_bore_output(process):
        for line in iter(process.stdout.readline, b''):
            decoded = line.decode('utf-8', errors='ignore').strip()
            print(f"   [bore] {decoded}")
            match = re.search(r'bore\.pub:(\d+)', decoded)
            if match:
                public_port_holder[0] = int(match.group(1))
                public_port_event.set()

    try:
        process = subprocess.Popen(
            [bore_cmd, 'local', str(local_port), '--to', 'bore.pub'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        thread = threading.Thread(target=read_bore_output, args=(process,), daemon=True)
        thread.start()

        print("⏳ Waiting for bore tunnel to establish...")
        got_port = public_port_event.wait(timeout=10)

        if got_port and public_port_holder[0]:
            public_port = public_port_holder[0]

            print("⏳ Verifying tunnel connectivity...")
            if verify_bore_tunnel('bore.pub', public_port):
                print("✅ Tunnel verified — bore.pub is reachable")
            else:
                print("⚠️  Could not verify tunnel (may still work once stream starts)")

            print(f"\n{'='*60}")
            print(f"🌐 GLOBAL RTSP URL (bore tunnel):")
            print(f"   rtsp://bore.pub:{public_port}/webcam")
            print(f"{'='*60}")
            print("💡 In VLC: Media → Open Network Stream → paste URL above")
            print("   VLC TIP: Set Tools → Preferences → Input/Codecs →")
            print("            RTP over RTSP (TCP) for best compatibility")
            return process, public_port
        else:
            print("❌ Could not get public port from bore. Check bore output above.")
            process.terminate()
            return None, None

    except Exception as e:
        print(f"❌ Error starting bore: {e}")
        return None, None

# ─────────────────────────────────────────────

def stream_webcam(device_name, resolution="1280x720", bitrate="2000k"):
    """Stream webcam to RTSP"""
    print(f"\n📡 Starting stream from: {device_name}")
    print(f"   Resolution: {resolution}")
    print(f"   Bitrate: {bitrate}")
    print(f"\n🌐 Local RTSP URL:  rtsp://localhost:8554/webcam")
    print("⏹️  Press Ctrl+C to stop streaming\n")
    
    cmd = [
        'ffmpeg',
        '-f', 'dshow',
        '-rtbufsize', '100M',
        '-video_size', resolution,
        '-i', f'video={device_name}',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-pix_fmt', 'yuv420p',
        '-profile:v', 'baseline',
        '-b:v', bitrate,
        '-maxrate', bitrate,
        '-bufsize', f'{int(bitrate[:-1])*2}k',
        '-g', '30',
        '-f', 'rtsp',
        '-rtsp_transport', 'tcp',
        'rtsp://localhost:8554/webcam'
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n✅ Streaming stopped")
    except Exception as e:
        print(f"\n❌ Streaming error: {e}")

def main():
    print("=" * 60)
    print("🎥 USB Webcam to RTSP Streamer (with bore tunnel)")
    print("=" * 60)
    
    # Check FFmpeg
    if not check_ffmpeg():
        sys.exit(1)
    
    # Device selection
    selected_device = "Integrated Camera"
    # selected_device = "LG Smart Cam"
    print(f"\n✅ Using device: {selected_device}")
    
    # Resolution selection
    print("\n📐 Select resolution:")
    print("  1. 1920x1080 (Full HD)")
    print("  2. 1280x720 (HD)")
    print("  3. 640x480 (SD)")
    
    resolutions = {
        '1': '1920x1080',
        '2': '1280x720',
        '3': '640x480'
    }
    
    res_choice = input("Enter choice (default: 2): ").strip() or '2'
    resolution = resolutions.get(res_choice, '1280x720')
    
    # Check/Start MediaMTX
    mediamtx_process = None
    if not check_mediamtx():
        print("\n⚠️  MediaMTX server not running")
        start = input("Start MediaMTX automatically? (Y/n): ").strip().lower()
        if start != 'n':
            mediamtx_process = start_mediamtx()
            if not mediamtx_process:
                print("\n❌ Cannot proceed without RTSP server")
                sys.exit(1)
    else:
        print("\n✅ MediaMTX server already running")

    # Ask about bore tunnel
    bore_process = None
    use_bore = input("\n🌍 Start bore tunnel for global access? (Y/n): ").strip().lower()
    if use_bore != 'n':
        bore_process, public_port = start_bore_tunnel(local_port=8554)
        if not bore_process:
            print("⚠️  Continuing without bore tunnel (local only)")

    # Start streaming
    try:
        stream_webcam(selected_device, resolution)
    finally:
        if bore_process:
            print("\n🛑 Stopping bore tunnel...")
            bore_process.terminate()
        if mediamtx_process:
            print("🛑 Stopping MediaMTX server...")
            mediamtx_process.terminate()

if __name__ == "__main__":
    main()