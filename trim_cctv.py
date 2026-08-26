"""Trim downloaded CCTV clips to small mp4 files (web-friendly)."""
import os, subprocess
import imageio_ffmpeg as iioff

FFMPEG = iioff.get_ffmpeg_exe()
SRC = os.path.join("dashboard", "public", "cctv")
os.makedirs(SRC, exist_ok=True)

JOBS = [
    ("cam_classroom.webm", "cam1-classroom.mp4", "students in classroom"),
    ("cam_corridor.webm",  "cam2-hallway.mp4",   "hallway / people walking"),
    ("cam_street.webm",    "cam3-corridor.mp4",  "corridor / street"),
]

for src, dst, desc in JOBS:
    inp = os.path.join(SRC, src)
    outp = os.path.join(SRC, dst)
    if not os.path.exists(inp):
        print(f"  -- skip {src}: not found"); continue
    if os.path.exists(outp) and os.path.getsize(outp) > 100_000:
        print(f"  -- skip {dst}: already exists"); continue
    cmd = [FFMPEG, "-y", "-i", inp, "-t", "12",
           "-vf", "scale=640:-2,fps=24",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
           "-movflags", "+faststart", "-an", outp]
    print(f"  -> {desc}: {src} -> {dst}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("     FAILED:", r.stderr[-500:])
    else:
        print(f"     OK ({os.path.getsize(outp)/1e6:.1f} MB)")

for name in ("cam_classroom.webm", "cam_corridor.webm", "cam_street.webm"):
    p = os.path.join(SRC, name)
    if os.path.exists(p):
        os.remove(p); print(f"  - removed {name}")
print("done.")