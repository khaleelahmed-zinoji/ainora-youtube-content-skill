#!/usr/bin/env python3
"""build_audio.py — premix assets/mix.wav: cleaned voice-over (assets/vo-clean.wav, from t=0, untouched) + a ducked
music bed alternating bright/calm by section (config "music", "music_switch") + quiet SFX from events.json.
Music sits -24.6 dB under the voice while talking and lifts on the voiceless end card; SFX ~22 dB under, high-passed.
SFX files expected in assets/sfx/: whoosh-short, heavyclick, pop, tap, quickwhoosh (.mp3). Bring your own licensed sounds.
Run with a python that has numpy."""
import subprocess, json, numpy as np
CFG = json.load(open("config.json"))

SR = 48000
TOTAL = json.load(open("timeline.json"))["total"]
N = int(TOTAL * SR)
SC = {s["name"]: s["start"] for s in json.load(open("scenes.json"))}

def load(path, ss=0.0, t=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-i", path]
    if t: cmd += ["-t", str(t)]
    cmd += ["-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32)
    return a.reshape(-1, 2).copy()

def place(buf, a, t, g=1.0):
    i = int(t * SR); j = min(N, i + len(a))
    if j > i: buf[i:j] += a[: j - i] * g

def fade(a, fi, fo):
    n = len(a); fi = int(fi * SR); fo = int(fo * SR)
    if fi: a[:fi] *= np.linspace(0, 1, fi)[:, None]
    if fo: a[n - fo:] *= np.linspace(1, 0, fo)[:, None]
    return a

def looped(path, length, xf=1.0):
    a = load(path); out = a.copy(); x = int(xf * SR)
    while len(out) < int(length * SR):
        ramp = np.linspace(0, 1, x)[:, None]
        out = np.concatenate([out[:-x], out[-x:] * (1 - ramp) + a[:x] * ramp, a[x:]])
    return out[: int(length * SR)].copy()

vo = load("assets/vo-clean.wav")
voice = np.zeros((N, 2), np.float32); place(voice, vo, 0.0)

music = np.zeros((N, 2), np.float32)
# Elegant, non-humming bed (v4 feedback: "remove that humming music"): two bright catalog tracks, pre-filtered
# high-pass 140 Hz ×2 and −3 dB @ 3.5 kHz (house rule from the Ainora Shorts audio notes), alternating by section.
# Two alternating beds (bright / calm), switched at the scene names in config "music_switch".
# House rule: bright tracks with little energy below 150 Hz, no humming drones.
EL, PI = CFG["music"]["bright"], CFG["music"]["calm"]
B = [SC[k] for k in CFG["music_switch"]]
marks = [0.0] + B + [TOTAL]
ACTS = [((EL, PI)[i % 2], marks[i], marks[i + 1] - marks[i] + (1.5 if i + 1 < len(marks) - 1 else 0), 0.6 if i == 0 else 1.5)
        for i in range(len(marks) - 1)]
for f, at, ln, fi in ACTS:
    a = fade(looped(f, ln, 2.0), fi, 1.5)
    a /= (np.sqrt(np.mean(a ** 2)) + 1e-9)
    place(music, a, at)
music = fade(music, 0.0, 1.8)

def env_dip(t0, t1, g, ramp=0.3):
    i0, i1, r = int(t0 * SR), int(t1 * SR), int(ramp * SR)
    e = np.ones(N, np.float32); e[i0:i1] = g
    e[i0 - r:i0] = np.linspace(1, g, r); e[i1:i1 + r] = np.linspace(g, 1, r)
    return e

# speech envelope (smoothed) → music dips 55% and SFX 60% while he talks
env = np.abs(voice).mean(axis=1)
win = int(0.05 * SR); env = np.convolve(env, np.ones(win) / win, mode="same")
active = (env > 0.01).astype(np.float32)
out = np.zeros_like(active); a_c = np.exp(-1 / (0.04 * SR)); r_c = np.exp(-1 / (0.7 * SR)); s = 0.0
for i in range(0, len(active), 48):
    x = active[i]; c = a_c ** 48 if x > s else r_c ** 48
    s = x + (s - x) * c; out[i:i + 48] = s
music *= (1.0 - 0.55 * out)[:, None]
m = out > 0.5
v_rms = np.sqrt(np.mean(voice[m] ** 2)); mu_rms = np.sqrt(np.mean(music[m] ** 2)) + 1e-9
music *= (v_rms * 10 ** (-24.6 / 20)) / mu_rms                       # lock: −24.6 dB under the voice while talking
END = json.load(open("timeline.json"))["vo_len"]
i0 = int((END - 0.6) * SR); music[i0:] *= np.linspace(1, 2, len(music) - i0)[:, None].clip(1, 2)   # ×2 on the voiceless end card

# SFX: soft palette only (no sub hits / risers / drones), high-passed 180 Hz, ~22 dB under the voice
S = "assets/sfx/"
CUE = {"panel": ("whoosh-short", 0.5, -0.15), "stamp": ("heavyclick", 0.55, -0.02), "stat": ("pop", 0.5, 0.0),
       "chip": ("tap", 0.35, 0.0), "wipe": ("quickwhoosh", 0.5, 0.0)}
cache, last = {}, {}
sfx = np.zeros((N, 2), np.float32)
ev = json.load(open("events.json"))
cuts = [s for k, s in SC.items() if s > 0.5]   # a soft whoosh into every scene
ev += [[c - 0.3, "wipe"] for c in cuts]
n = 0
for t, k in sorted(ev):
    name, vol, off = CUE[k]
    if t - last.get("any", -9) < 0.25 or t - last.get(k, -9) < (0.6 if k in ("chip", "panel") else 0.3):
        continue
    if name not in cache:
        cmd = ["ffmpeg", "-v", "error", "-i", S + name + ".mp3", "-af", "highpass=f=180:poles=2", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
        cache[name] = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, dtype=np.float32).reshape(-1, 2).copy()
    place(sfx, cache[name], max(0, t + off), vol)
    last[k] = last["any"] = t; n += 1
sfx *= (1.0 - 0.6 * out)[:, None]
sx = sfx[np.abs(sfx).mean(axis=1) > 1e-4]
s_rms = np.sqrt(np.mean(sx ** 2)) + 1e-9 if len(sx) else 1.0
sfx *= (v_rms * 10 ** (-22.0 / 20)) / s_rms                         # SFX events ≈ 22 dB under the voice

mix = voice + music + sfx
pk = np.abs(mix).max()
if pk > 0.98: mix *= 0.98 / pk
pcm = (np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-ar", str(SR), "assets/mix.wav"], input=pcm, check=True)
mu = np.sqrt(np.mean(music[m] ** 2))
print("sfx cues:", n, "| music under voice while talking:", round(20 * np.log10(mu / v_rms), 1), "dB")
