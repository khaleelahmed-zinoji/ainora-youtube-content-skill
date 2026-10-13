"""deroom.py — soft downward expander that pulls the room-echo tails down between words.
assets/vo-dfn.wav -> assets/vo-clean.wav (same length, same timing). Run with the numpy venv."""
import subprocess, numpy as np, sys
SR = 48000
def load(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).copy()
x = load("assets/vo-dfn.wav")
win = int(0.015 * SR)
env = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, mode="same")) + 1e-7
db = 20 * np.log10(env)
ref = np.percentile(db[db > -60], 90)                 # typical loud-speech level
THR = ref - float(sys.argv[1]) if len(sys.argv) > 1 else ref - 16   # tails sit ~16+ dB below speech
RATIO, RANGE = 2.2, 14.0
red = np.clip((THR - db) * (RATIO - 1), 0, RANGE)     # dB of attenuation below threshold
# smooth: fast attack (gain recovers quickly on new words), slower release (no chatter)
g = np.empty_like(red); s = 0.0
a = np.exp(-1 / (0.004 * SR)); r = np.exp(-1 / (0.06 * SR))
for i in range(len(red)):
    t = red[i]; c = a if t < s else r
    s = t + (s - t) * c; g[i] = s
y = x * 10 ** (-g / 20)
pcm = (np.clip(y, -1, 1) * 32767).astype("<i2").tobytes()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "assets/vo-clean.wav"], input=pcm, check=True)
print(f"speech ref {ref:.1f} dB, threshold {THR:.1f} dB")
