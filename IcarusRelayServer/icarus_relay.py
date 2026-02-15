#!/usr/bin/env python3
"""
Icarus TV Chooser - GUI Version (Fixed)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import http.server
import socketserver
import urllib.request
import ssl
import os
import re
import threading
import time
import json


# HTTP/FFmpeg network tuning (helps with IPTV gateways that are picky / flaky)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def get_ffmpeg_headers():
    base = config.get('iptv_base', 'https://tvnow.best')
    return "User-Agent: %s\r\nReferer: %s/\r\nOrigin: %s\r\n" % (USER_AGENT, base, base)

# Retry behavior for resolving the final redirected stream URL
RESOLVE_RETRIES = 5
RESOLVE_BACKOFF_BASE_SEC = 0.6
def get_final_url(api_url):
    """Follow redirects to get final stream URL (with retries)."""
    last_err = None
    for attempt in range(1, RESOLVE_RETRIES + 1):
        try:
            req = urllib.request.Request(
                api_url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Referer": config.get('iptv_base', 'https://tvnow.best') + "/",
                    "Origin": config.get('iptv_base', 'https://tvnow.best'),
                },
            )
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
                return resp.url
        except Exception as e:
            last_err = e
            # Common with IPTV gateways (temporary upstream errors).
            sleep_s = RESOLVE_BACKOFF_BASE_SEC * (2 ** (attempt - 1))
            print(f"[WARN] get_final_url attempt {attempt}/{RESOLVE_RETRIES} failed: {e} (sleep {sleep_s:.1f}s)")
            time.sleep(sleep_s)
    print(f"[ERROR] get_final_url failed after {RESOLVE_RETRIES} tries: {last_err}")
    return api_url


def search_imdb(query):
    """Search IMDB for TV shows and return results with IDs"""
    url = f"https://v3.sg.media-imdb.com/suggestion/x/{urllib.request.quote(query)}.json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as r:
        data = json.loads(r.read().decode())
        results = []
        for item in data.get('d', []):
            if item.get('qid') == 'tvSeries':
                results.append({
                    'title': item.get('l', ''),
                    'year': item.get('y', ''),
                    'imdb_id': item.get('id', ''),
                    'poster': item.get('i', {}).get('imageUrl', '')
                })
        return results

import subprocess as sp

# ── Configuration ──────────────────────────────────────────────────────────
HTTP_PORT = 8080
STREAM_PATH = "/stream.mp4"
ACCESS_KEY = ""  # e.g. "Icarus123"  (leave empty for no key)

VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.mpg', '.mpeg', '.m2ts', '.vob'}
USE_COPY_FIRST = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG = os.path.join(SCRIPT_DIR, "ffmpeg", "ffmpeg.exe")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "Icarus_config.json")

if not os.path.exists(FFMPEG):
    print(f"[ERROR] FFmpeg not found at: {FFMPEG}")
else:
    print(f"[OK] FFmpeg found: {FFMPEG}")

# ── Credential / config management ────────────────────────────────────────
DEFAULT_CONFIG = {
    "iptv_base": "https://tvnow.best",
    "username": "",
    "password": "",
}

def load_config():
    """Load saved config from Icarus_config.json (next to script)."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)
            # Merge with defaults so new keys are always present
            merged = {**DEFAULT_CONFIG, **cfg}
            return merged
        except Exception as e:
            print(f"[WARN] Failed to read config: {e}")
    return dict(DEFAULT_CONFIG)

def save_config(cfg):
    """Persist config to Icarus_config.json."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
        print(f"[CONFIG] Saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"[ERROR] Failed to save config: {e}")

# Runtime config (populated after login)
config = load_config()

def iptv_configured():
    """True if we have enough info to call the IPTV API."""
    return bool(config.get("username") and config.get("password") and config.get("iptv_base"))

def build_episode_url(imdb_id, season, episode):
    return f"{config['iptv_base']}/api/stream/{config['username']}/{config['password']}/tvshow/{imdb_id}/{season}/{episode}"

# ── Shared state ──────────────────────────────────────────────────────────
class State:
    url = ""
    title = "Nothing playing"

state = State()

# Current URL for direct streaming
current_url = ""

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

tunnel_url = None

def start_tunnel():
    global tunnel_url
    proc = sp.Popen(['cloudflared', 'tunnel', '--url', 'http://localhost:8080'],
                    stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
    for line in proc.stdout:
        if 'trycloudflare.com' in line:
            import re
            match = re.search(r'https://[^\s]+\.trycloudflare\.com', line)
            if match:
                tunnel_url = match.group(0)
                print(f"[TUNNEL] {tunnel_url}")
                break

def fetch_m3u(playlist_type, num=1):
    base = config['iptv_base']
    user = config['username']
    pw = config['password']
    if playlist_type == "livetv":
        url = f"{base}/api/list/{user}/{pw}/m3u8/livetv"
    elif playlist_type == "movies":
        url = f"{base}/api/list/{user}/{pw}/m3u8/movies"
    else:
        url = f"{base}/api/list/{user}/{pw}/m3u8/tvshows/{num}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
        return resp.read().decode('utf-8')

def parse_m3u(content):
    entries = []
    lines = content.strip().split('\n')
    for i, line in enumerate(lines):
        if line.startswith('#EXTINF:'):
            match = re.search(r'group-title="([^"]*)".*,(.+)$', line)
            if match and i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url and not url.startswith('#'):
                    entries.append({'group': match.group(1), 'title': match.group(2).strip(), 'url': url})
    return entries

# Shared stream - one FFmpeg process for all viewers
# Shared stream - one FFmpeg process for all viewers
class SharedStream:
    def __init__(self):
        self.proc = None
        self.lock = threading.Lock()
        self.running = False

        # Exact MP4 init segment (ftyp+moov) for every new client (UE4 needs this)
        self.init_bytes = b""
        self.init_ready = threading.Event()

        # Live MP4 fragments (each fragment starts at a 'moof' box)
        self.fragments = []
        self.max_fragments = 120  # ~ last few minutes depending on fragment duration
        self.frag_base = 0  # logical index of fragments[0]

        # Parsing state
        self._buf = bytearray()
        self._cur_frag = bytearray()
        self._saw_moof = False

        # Bookkeeping
        self.last_data_time = 0.0
        self.current_api_url = None

        # Client tracking / idle stop
        self.active_clients = 0
        self.last_client_time = 0.0

        # Restart signaling (stall/corruption)
        self.restart_event = threading.Event()
        self.restart_reason = ""
        self.err_window = []
        self._is_local = False

    # ---- client tracking ----
    def client_connected(self):
        with self.lock:
            self.active_clients += 1
            self.last_client_time = time.time()
            return self.active_clients

    def client_disconnected(self):
        with self.lock:
            if self.active_clients > 0:
                self.active_clients -= 1
            self.last_client_time = time.time()
            return self.active_clients

    def _request_restart(self, reason: str):
        with self.lock:
            self.restart_reason = reason
        self.restart_event.set()

    def start(self, url, is_local=False):
        self.stop()
        self.init_bytes = b""
        self.fragments = []
        self.frag_base = 0
        self._buf = bytearray()
        self._cur_frag = bytearray()
        self._saw_moof = False
        self.init_ready.clear()
        self.restart_event.clear()
        with self.lock:
            self.err_window = []
            self.current_api_url = url
            self._is_local = is_local

        print(f"[SHARED] Starting stream...")
        print(f"[SHARED] {'Local file' if is_local else 'API URL'}: {url}")

        if is_local:
            input_url = url
        else:
            input_url = get_final_url(url)
            print(f"[SHARED] Final URL: {input_url[:80]}...")

        # Build FFmpeg command based on source type
        cmd = [
            FFMPEG,
            "-hide_banner", "-loglevel", "warning",
        ]

        if is_local:
            # Local file: no network options needed
            cmd += [
                "-re",  # real-time pacing for UE4
                "-i", input_url,
            ]
        else:
            # IPTV stream: browser-like headers + reconnects
            cmd += [
                "-user_agent", USER_AGENT,
                "-headers", get_ffmpeg_headers(),
                "-reconnect", "1",
                "-reconnect_streamed", "1",
                "-reconnect_on_network_error", "1",
                "-reconnect_delay_max", "5",
                "-rw_timeout", "30000000",
                "-re",
                "-i", input_url,
            ]

        # Common output settings: UE4-safe fragmented MP4
        cmd += [
            # Timestamp sanity
            "-fflags", "+genpts",
            "-avoid_negative_ts", "make_zero",

            # Video: UE4-safe H.264
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "zerolatency",
            "-pix_fmt", "yuv420p",
            "-profile:v", "main",
            "-level", "4.1",

            # Force a keyframe every 2 seconds (30fps => 60)
            "-r", "30",
            "-g", "60",
            "-keyint_min", "60",
            "-sc_threshold", "0",
            "-force_key_frames", "expr:gte(t,n_forced*2)",

            # Keep bitrate sane (helps Media Foundation)
            "-b:v", "3500k",
            "-maxrate", "3500k",
            "-bufsize", "7000k",

            # Audio
            "-c:a", "aac",
            "-ar", "44100",
            "-ac", "2",
            "-b:a", "128k",

            # MP4 fragmentation for stream playback
            "-movflags", "frag_keyframe+empty_moov+default_base_moof",
            "-muxdelay", "0",
            "-muxpreload", "0",
            "-f", "mp4",
            "-"
        ]

        try:
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"[SHARED] FFmpeg started PID: {self.proc.pid}")
        except Exception as e:
            print(f"[SHARED] FFmpeg failed to start: {e}")
            self.proc = None
            return

        self.running = True
        self.last_data_time = time.time()

        threading.Thread(target=self._read_loop, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()
        threading.Thread(target=self._supervisor, daemon=True).start()

    def _read_stderr(self):
        if not self.proc:
            return
        bad_markers = (
            "Invalid NAL unit size",
            "Error splitting the input into NAL units",
            "missing picture in access unit",
            "Invalid data found when processing input",
            "Error submitting packet to decoder",
            "Number of bands",
            "channel element",
        )
        try:
            for raw in self.proc.stderr:
                try:
                    line = raw.decode(errors="ignore").strip()
                except Exception:
                    continue
                if not line:
                    continue
                print(f"[FFMPEG] {line}")

                if any(m in line for m in bad_markers):
                    now = time.time()
                    with self.lock:
                        self.err_window.append(now)
                        cutoff = now - 10.0
                        self.err_window = [t for t in self.err_window if t >= cutoff]
                        n = len(self.err_window)
                    if n >= 20:
                        self._request_restart("decoder corruption burst")
                        return
        except Exception:
            pass

    def _parse_mp4_boxes(self):
        # Consume self._buf into init_bytes / fragments.
        # We only need to reliably detect box boundaries and 'moof'.
        while True:
            if len(self._buf) < 8:
                return

            size = int.from_bytes(self._buf[0:4], 'big', signed=False)
            boxtype = bytes(self._buf[4:8])

            # Basic sanity to avoid lockups on corrupted boundaries
            if size < 8 or size > 50 * 1024 * 1024:
                # resync by dropping one byte
                del self._buf[0:1]
                continue

            if len(self._buf) < size:
                return

            box = bytes(self._buf[0:size])
            del self._buf[0:size]

            # Before first moof: collect init boxes
            if not self._saw_moof:
                if boxtype == b'moof':
                    self._saw_moof = True
                    # init is now complete
                    with self.lock:
                        if not self.init_bytes:
                            self.init_bytes = self.init_bytes  # no-op for clarity
                    self.init_ready.set()
                    # Start new fragment with this moof
                    self._cur_frag = bytearray()
                    self._cur_frag += box
                else:
                    # ftyp/moov/other init data
                    self.init_bytes += box
                continue

            # After first moof: build fragments that begin with moof
            if boxtype == b'moof':
                # finalize previous fragment if any
                if self._cur_frag:
                    frag_bytes = bytes(self._cur_frag)
                    with self.lock:
                        self.fragments.append(frag_bytes)
                        if len(self.fragments) > self.max_fragments:
                            self.fragments.pop(0)
                            self.frag_base += 1
                    self._cur_frag = bytearray()
                self._cur_frag += box
            else:
                # add box to current fragment
                if self._cur_frag is not None:
                    self._cur_frag += box

    def _read_loop(self):
        bytes_read = 0
        print(f"[SHARED] Read loop started, running={self.running}, proc={self.proc is not None}")

        while self.running and self.proc:
            chunk = self.proc.stdout.read(32768)
            if not chunk:
                if self.proc and self.proc.poll() is not None:
                    print(f"[SHARED] FFmpeg exited with code: {self.proc.returncode}")
                break

            self.last_data_time = time.time()
            bytes_read += len(chunk)
            self._buf += chunk

            # parse as much as possible
            self._parse_mp4_boxes()

            if bytes_read and (bytes_read % (1024*1024) < 32768):
                print(f"[SHARED] Streaming... {bytes_read // 1024} KB")

        # flush last fragment if present
        if self._cur_frag:
            frag_bytes = bytes(self._cur_frag)
            with self.lock:
                self.fragments.append(frag_bytes)
                if len(self.fragments) > self.max_fragments:
                    self.fragments.pop(0)

        print(f"[SHARED] Stream ended. Total bytes read: {bytes_read}")

        if not self.init_ready.is_set():
            self.init_ready.set()

        if self.running:
            # Don't auto-restart local files that finished normally
            is_local = getattr(self, '_is_local', False)
            rc = None
            try:
                if self.proc:
                    rc = self.proc.returncode
            except Exception:
                pass
            if is_local and rc == 0:
                print("[SHARED] Local file finished playing.")
                self.running = False
            else:
                self._request_restart("ffmpeg ended")

    def _supervisor(self):
        while self.running:
            with self.lock:
                clients = self.active_clients
                last_client_time = self.last_client_time
                api_url = self.current_api_url
                reason = self.restart_reason

            now = time.time()

            # Idle-stop: if nobody is watching, stop after 60s
            if clients == 0 and last_client_time and (now - last_client_time) > 60:
                print("[SHARED] No viewers for 60s -> stopping FFmpeg.")
                self.stop()
                return

            # Stall detection: no data for 60s
            if self.proc and (now - self.last_data_time) > 60:
                self._request_restart("stream stalled")

            if self.restart_event.is_set():
                with self.lock:
                    api_url = self.current_api_url
                    reason = self.restart_reason or "restart requested"
                    is_local = getattr(self, '_is_local', False)
                print(f"[SHARED] Restarting stream ({reason})...")
                try:
                    self.start(api_url or current_url, is_local=is_local)
                except Exception:
                    pass
                return

            time.sleep(2)

    def stop(self):
        self.running = False
        self.init_ready.set()
        self.restart_event.clear()
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass
            self.proc = None
        time.sleep(0.2)

    def get_init_bytes(self) -> bytes:
        with self.lock:
            return self.init_bytes

    def get_fragment_count(self) -> int:
        with self.lock:
            return self.frag_base + len(self.fragments)

    def get_fragment(self, idx: int):
        with self.lock:
            real_idx = idx - self.frag_base
            if 0 <= real_idx < len(self.fragments):
                return self.fragments[real_idx]
        return None

shared_stream = SharedStream()


class StreamHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        try:
            print(f'[HTTP] {self.address_string()} - {format % args}')
        except Exception:
            pass

    def do_GET(self):
        if not self.path.startswith(STREAM_PATH):
            self.send_error(404)
            return

        if ACCESS_KEY:
            if ("?key=" + ACCESS_KEY) not in self.path and ("&key=" + ACCESS_KEY) not in self.path:
                self.send_error(403, "Forbidden")
                return

        shared_stream.client_connected()
        try:
            if not shared_stream.running:
                try:
                    shared_stream.start(current_url)
                except Exception as e:
                    self.send_error(503, f"Stream not ready: {e}")
                    return

            # Wait for init segment (ftyp+moov)
            shared_stream.init_ready.wait(timeout=30)

            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Connection", "close")
            self.end_headers()

            init_bytes = shared_stream.get_init_bytes()
            if init_bytes:
                self.wfile.write(init_bytes)

            # Start at a clean fragment boundary (last 2 fragments)
            count = shared_stream.get_fragment_count()
            pos = max(0, count - 2)

            stall_count = 0
            while True:
                frag = shared_stream.get_fragment(pos)
                if frag is not None:
                    self.wfile.write(frag)
                    self.wfile.flush()
                    pos += 1
                    stall_count = 0
                else:
                    # Check if stream restarted (fragments got cleared behind us)
                    current_count = shared_stream.get_fragment_count()
                    if current_count > 0 and pos > current_count:
                        # Stream restarted - break so UE4 reconnects via power toggle
                        print(f"[HTTP] Stream restarted, closing client connection")
                        break
                    if not shared_stream.running:
                        break
                    stall_count += 1
                    if stall_count > 1500:  # ~30 seconds of no data
                        print(f"[HTTP] No data for 30s, closing connection")
                        break
                    time.sleep(0.02)

        except Exception:
            pass
        finally:
            shared_stream.client_disconnected()

def start_server():

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(("", HTTP_PORT), StreamHandler)
    httpd.daemon_threads = True
    print(f"Server running on port {HTTP_PORT}")
    httpd.serve_forever()

class LoginDialog:
    """Modal dialog for IPTV credentials. Shown on first run or via Settings."""
    def __init__(self, parent, on_success=None):
        self.result = False
        self.on_success = on_success

        self.win = tk.Toplevel(parent)
        self.win.title("IPTV Account Setup")
        self.win.geometry("420x280")
        self.win.configure(bg='#1a1a1a')
        self.win.resizable(False, False)
        self.win.transient(parent)
        self.win.grab_set()

        tk.Label(self.win, text="IPTV Account Setup", bg='#1a1a1a', fg='white',
                 font=('Arial', 14, 'bold')).pack(pady=(15, 5))
        tk.Label(self.win, text="Enter your IPTV provider credentials.\nThese are saved locally and never shared.",
                 bg='#1a1a1a', fg='#aaa', font=('Arial', 9)).pack(pady=(0, 10))

        form = tk.Frame(self.win, bg='#1a1a1a')
        form.pack(padx=30, fill=tk.X)

        tk.Label(form, text="Provider URL:", bg='#1a1a1a', fg='white', anchor='w').grid(row=0, column=0, sticky='w', pady=4)
        self.url_var = tk.StringVar(value=config.get('iptv_base', 'https://tvnow.best'))
        tk.Entry(form, textvariable=self.url_var, width=32, font=('Arial', 10)).grid(row=0, column=1, pady=4, padx=(10,0))

        tk.Label(form, text="Username:", bg='#1a1a1a', fg='white', anchor='w').grid(row=1, column=0, sticky='w', pady=4)
        self.user_var = tk.StringVar(value=config.get('username', ''))
        tk.Entry(form, textvariable=self.user_var, width=32, font=('Arial', 10)).grid(row=1, column=1, pady=4, padx=(10,0))

        tk.Label(form, text="Password:", bg='#1a1a1a', fg='white', anchor='w').grid(row=2, column=0, sticky='w', pady=4)
        self.pass_var = tk.StringVar(value=config.get('password', ''))
        self.pass_entry = tk.Entry(form, textvariable=self.pass_var, width=32, font=('Arial', 10), show='*')
        self.pass_entry.grid(row=2, column=1, pady=4, padx=(10,0))

        self.show_pw = tk.BooleanVar(value=False)
        tk.Checkbutton(form, text="Show", variable=self.show_pw, bg='#1a1a1a', fg='#aaa',
                       selectcolor='#333', command=self._toggle_pw).grid(row=2, column=2, padx=4)

        btn_frame = tk.Frame(self.win, bg='#1a1a1a')
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Save & Connect", command=self._save, bg='#4caf50', fg='white',
                  font=('Arial', 10, 'bold'), padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Skip (Local Files Only)", command=self._skip,
                  font=('Arial', 10), padx=10).pack(side=tk.LEFT, padx=5)

    def _toggle_pw(self):
        self.pass_entry.config(show='' if self.show_pw.get() else '*')

    def _save(self):
        url = self.url_var.get().strip().rstrip('/')
        user = self.user_var.get().strip()
        pw = self.pass_var.get().strip()

        if not url:
            messagebox.showwarning("Missing", "Provider URL is required.", parent=self.win)
            return
        if not user or not pw:
            messagebox.showwarning("Missing", "Username and password are required.", parent=self.win)
            return

        config['iptv_base'] = url
        config['username'] = user
        config['password'] = pw
        save_config(config)

        self.result = True
        self.win.destroy()
        if self.on_success:
            self.on_success()

    def _skip(self):
        self.result = False
        self.win.destroy()

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Icarus - Video Entertainment for Icarus Network")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')
        
        self.shows = {}
        self.episodes = []
        self._local_mode = False
        self._local_folder = ""
        
        self.build_ui()
        self._update_iptv_buttons()
        threading.Thread(target=start_server, daemon=True).start()
        threading.Thread(target=start_tunnel, daemon=True).start()
        self.root.after(3000, self.update_tunnel_url)

        # Show login on first run (no saved credentials)
        if not iptv_configured():
            self.root.after(100, self._show_login)
    
    def build_ui(self):
        top = tk.Frame(self.root, bg='#1a1a1a')
        top.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(top, text="Local URL:", bg='#1a1a1a', fg='white', font=('Arial', 10)).pack(side=tk.LEFT)
        self.url_entry = tk.Entry(top, width=35, font=('Arial', 10))
        self.url_entry.insert(0, f"http://localhost:{HTTP_PORT}{STREAM_PATH}" + (f"?key={ACCESS_KEY}" if ACCESS_KEY else ""))
        self.url_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Copy", command=self.copy_url).pack(side=tk.LEFT)
        
        tk.Label(top, text="  Friend URL:", bg='#1a1a1a', fg='yellow', font=('Arial', 10)).pack(side=tk.LEFT)
        self.tunnel_entry = tk.Entry(top, width=45, font=('Arial', 10))
        self.tunnel_entry.insert(0, "Starting tunnel...")
        self.tunnel_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Copy", command=self.copy_tunnel).pack(side=tk.LEFT)
        
        self.status = tk.Label(top, text="● Server Running", bg='#1a1a1a', fg='#4caf50', font=('Arial', 10))
        self.status.pack(side=tk.RIGHT)
        
        btn_frame = tk.Frame(self.root, bg='#1a1a1a')
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_load_all = tk.Button(btn_frame, text="Load ALL", command=self.load_all, bg='#4caf50')
        self.btn_load_all.pack(side=tk.LEFT, padx=2)
        self.btn_movies = tk.Button(btn_frame, text="Movies", command=lambda: self.load_playlist('movies', 1))
        self.btn_movies.pack(side=tk.LEFT, padx=2)
        self.btn_livetv = tk.Button(btn_frame, text="Live TV", command=lambda: self.load_playlist('livetv', 1))
        self.btn_livetv.pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="📁 Local Files", command=self.browse_local_files, bg='#2196f3', fg='white').pack(side=tk.LEFT, padx=6)
        
        tk.Label(btn_frame, text=" | IMDB Search:", bg='#1a1a1a', fg='white').pack(side=tk.LEFT, padx=5)
        self.imdb_search = tk.Entry(btn_frame, width=20, font=('Arial', 10))
        self.imdb_search.pack(side=tk.LEFT, padx=2)
        self.imdb_search.bind('<Return>', lambda e: self.do_imdb_search())
        self.btn_imdb = tk.Button(btn_frame, text="Search", command=self.do_imdb_search, bg='#ff9800')
        self.btn_imdb.pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="⚙ Settings", command=self._show_login).pack(side=tk.RIGHT, padx=5)
        
        self.loading = tk.Label(btn_frame, text="", bg='#1a1a1a', fg='cyan')
        self.loading.pack(side=tk.LEFT, padx=20)
        
        paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg='#1a1a1a')
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left = tk.Frame(paned, bg='#2a2a2a')
        paned.add(left, width=350)
        
        tk.Label(left, text="Shows", bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold')).pack(anchor=tk.W, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_shows)
        tk.Entry(left, textvariable=self.search_var, font=('Arial', 10)).pack(fill=tk.X, padx=5, pady=5)
        
        scroll1 = tk.Scrollbar(left)
        scroll1.pack(side=tk.RIGHT, fill=tk.Y)
        self.shows_list = tk.Listbox(left, bg='#333', fg='white', font=('Arial', 10), 
                                      selectbackground='#4fc3f7', yscrollcommand=scroll1.set)
        self.shows_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll1.config(command=self.shows_list.yview)
        self.shows_list.bind('<<ListboxSelect>>', self.on_show_select)
        
        right = tk.Frame(paned, bg='#2a2a2a')
        paned.add(right)
        
        tk.Label(right, text="Episodes", bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold')).pack(anchor=tk.W, padx=5, pady=5)
        
        scroll2 = tk.Scrollbar(right)
        scroll2.pack(side=tk.RIGHT, fill=tk.Y)
        self.ep_list = tk.Listbox(right, bg='#333', fg='white', font=('Arial', 10),
                                   selectbackground='#4fc3f7', yscrollcommand=scroll2.set)
        self.ep_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll2.config(command=self.ep_list.yview)
        self.ep_list.bind('<Double-1>', self.on_ep_double_click)
        
        bot = tk.Frame(self.root, bg='#1a1a1a')
        bot.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(bot, text="▶ Play Selected", command=self.play_selected, font=('Arial', 11)).pack(side=tk.LEFT, padx=5)
        
        self.now_playing = tk.Label(bot, text="No IPTV configured — use Local Files or ⚙ Settings" if not iptv_configured() else f"▶ {state.title}",
                                    bg='#1a1a1a', fg='#4fc3f7', font=('Arial', 11))
        self.now_playing.pack(side=tk.LEFT, padx=20)
    
    def _show_login(self):
        LoginDialog(self.root, on_success=self._update_iptv_buttons)

    def _update_iptv_buttons(self):
        """Enable/disable IPTV buttons based on whether credentials are configured."""
        st = tk.NORMAL if iptv_configured() else tk.DISABLED
        for btn in (self.btn_load_all, self.btn_movies, self.btn_livetv, self.btn_imdb):
            btn.config(state=st)
        if iptv_configured():
            self.now_playing.config(text=f"▶ Ready — {config['iptv_base']}")
    
    def copy_url(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.url_entry.get())
        messagebox.showinfo("Copied", "Local URL copied!\n\nUse this on YOUR PC in Icarus.")
    
    def copy_tunnel(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.tunnel_entry.get())
        messagebox.showinfo("Copied", "Friend URL copied!\n\nSend this to your friend for Icarus.")
    
    def update_tunnel_url(self):
        if tunnel_url:
            self.tunnel_entry.delete(0, tk.END)
            self.tunnel_entry.insert(0, f"{tunnel_url}{STREAM_PATH}" + (f"?key={ACCESS_KEY}" if ACCESS_KEY else ""))
        else:
            self.root.after(2000, self.update_tunnel_url)
    
    def load_all(self):
        if not iptv_configured():
            messagebox.showwarning("Not Configured", "Set up your IPTV account first via ⚙ Settings.")
            return
        self._local_mode = False
        self.loading.config(text="Loading ALL playlists (1-14)...")
        self.shows_list.delete(0, tk.END)
        self.ep_list.delete(0, tk.END)
        
        def load():
            self.shows = {}
            for i in range(1, 15):  # tvshows 1-14
                try:
                    self.root.after(0, lambda n=i: self.loading.config(text=f"Loading playlist {n}/14..."))
                    content = fetch_m3u('tvshows', i)
                    entries = parse_m3u(content)
                    for e in entries:
                        g = e['group']
                        if g not in self.shows:
                            self.shows[g] = []
                        # Avoid duplicates
                        if e not in self.shows[g]:
                            self.shows[g].append(e)
                except Exception as ex:
                    print(f"[WARN] Playlist {i} failed: {ex}")
            self.root.after(0, self.populate_shows)
        
        threading.Thread(target=load, daemon=True).start()
    
    def load_playlist(self, ptype, num):
        if not iptv_configured():
            messagebox.showwarning("Not Configured", "Set up your IPTV account first via ⚙ Settings.")
            return
        self._local_mode = False
        self.loading.config(text="Loading...")
        self.shows_list.delete(0, tk.END)
        self.ep_list.delete(0, tk.END)
        
        def load():
            try:
                content = fetch_m3u(ptype, num)
                entries = parse_m3u(content)
                self.shows = {}
                for e in entries:
                    g = e['group']
                    if g not in self.shows:
                        self.shows[g] = []
                    self.shows[g].append(e)
                self.root.after(0, self.populate_shows)
            except Exception as e:
                self.root.after(0, lambda: self.loading.config(text=f"Error: {e}"))
        
        threading.Thread(target=load, daemon=True).start()
    
    def populate_shows(self):
        self.loading.config(text=f"{len(self.shows)} shows")
        self.shows_list.delete(0, tk.END)
        for name in sorted(self.shows.keys()):
            self.shows_list.insert(tk.END, name)
    
    def filter_shows(self, *args):
        search = self.search_var.get().lower()
        self.shows_list.delete(0, tk.END)
        for name in sorted(self.shows.keys()):
            if search in name.lower():
                self.shows_list.insert(tk.END, name)
    
    def do_imdb_search(self):
        if not iptv_configured():
            messagebox.showwarning("Not Configured", "Set up your IPTV account first via ⚙ Settings.")
            return
        query = self.imdb_search.get().strip()
        if not query:
            return
        self.loading.config(text="Searching IMDB...")
        
        def search():
            try:
                results = search_imdb(query)
                if not results:
                    self.root.after(0, lambda: self.loading.config(text="No TV shows found"))
                    return
                
                # Add results to shows list
                self.shows = {}
                for r in results:
                    name = f"{r['title']} ({r['year']}) [{r['imdb_id']}]"
                    # Generate episodes S01-S10, E01-E20 as possibilities
                    self.shows[name] = []
                    for s in range(1, 12):
                        for e in range(1, 25):
                            self.shows[name].append({
                                'group': name,
                                'title': f"S{s:02d} E{e:02d}",
                                'url': build_episode_url(r['imdb_id'], s, e)
                            })
                
                self.root.after(0, lambda: self.loading.config(text=f"{len(results)} shows from IMDB"))
                self.root.after(0, self.populate_shows)
            except Exception as ex:
                self.root.after(0, lambda: self.loading.config(text=f"Search error: {ex}"))
        
        threading.Thread(target=search, daemon=True).start()
    
    def on_show_select(self, event):
        sel = self.shows_list.curselection()
        if not sel:
            return
        show_name = self.shows_list.get(sel[0])
        self.episodes = self.shows.get(show_name, [])
        self.ep_list.delete(0, tk.END)
        for ep in self.episodes:
            self.ep_list.insert(tk.END, ep['title'])
    
    def browse_local_files(self):
        folder = filedialog.askdirectory(title="Select Media Folder", initialdir=self._local_folder or os.path.expanduser("~"))
        if not folder:
            return
        self._local_folder = folder
        self._local_mode = True
        self.loading.config(text=f"Scanning {folder}...")

        def scan():
            shows = {}
            # Walk folder recursively, group by parent folder
            for root_dir, dirs, files in os.walk(folder):
                media_files = []
                for f in sorted(files):
                    ext = os.path.splitext(f)[1].lower()
                    if ext in VIDEO_EXTENSIONS:
                        filepath = os.path.join(root_dir, f)
                        media_files.append({
                            'group': os.path.basename(root_dir),
                            'title': f,
                            'url': filepath,
                            '_local': True
                        })
                if media_files:
                    group_name = os.path.relpath(root_dir, folder) if root_dir != folder else os.path.basename(folder)
                    shows[group_name] = media_files

            # If no subfolders with media, put everything under root
            if not shows:
                self.root.after(0, lambda: self.loading.config(text="No video files found"))
                return

            self.shows = shows
            self.root.after(0, self.populate_shows)
            self.root.after(0, lambda: self.loading.config(text=f"📁 {sum(len(v) for v in shows.values())} files in {len(shows)} folders"))

        threading.Thread(target=scan, daemon=True).start()

    def on_ep_double_click(self, event):
        self.play_selected()
    
    def play_selected(self):
        global current_url
        sel = self.ep_list.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an episode first.")
            return
        ep = self.episodes[sel[0]]
        is_local = ep.get('_local', False)
        
        # Update state
        state.url = ep['url']
        state.title = ep['title']
        current_url = ep['url']

        # Start (or switch) the shared stream so ALL connected viewers get the same feed
        try:
            shared_stream.start(current_url, is_local=is_local)
        except Exception as e:
            messagebox.showerror("Stream Error", f"Failed to start stream:\n{e}")
            return

        prefix = "📁" if is_local else "▶"
        print(f"[GUI] Selected: {state.title}")
        print(f"[GUI] {'Path' if is_local else 'URL'}: {state.url[:70]}...")
        
        self.now_playing.config(text=f"{prefix} {state.title}")
        messagebox.showinfo("Channel Switched", f"Now playing: {state.title}\n\nAll connected TVs will update automatically.")
    
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    App().run()
