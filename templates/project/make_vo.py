#!/usr/bin/env python3
"""make_vo.py — builds the voice-over timeline from ONE talking-head recording.

Reads config.json:
  "source":     path to the recording (.mov/.mp4), relative to this project folder
  "keep":       inclusive word-index ranges of transcript_raw.json to keep, e.g. [[0, 31], [40, 120]].
                Use it to drop false starts / repeated takes (keep the LAST clean take of each line).
                Omit or null = use every word (the recording as-is).
  "tighten":    true to shorten pauses longer than 0.9s down to 0.55s (no speed change, no word cut)
  "green_key":  hex of the green screen (e.g. "0x00e575") to key the presenter with ffmpeg,
                or null to use a background-removed "pres_alpha.webm" (npx hyperframes remove-background)

  python3 make_vo.py audio      -> assets/vo.wav + transcript.json + vo_meta.json + segments.json
  python3 make_vo.py presenter  -> assets/presenter.webm (+ presenter-last.png), white outline, 1080x1398
"""
import json, subprocess, sys

CFG = json.load(open("config.json"))
SRC = CFG["source"]
w = json.load(open("transcript_raw.json"))
for x in w:  # ASR stretches some sentence-final words across the following silence
    x["end"] = min(x["end"], x["start"] + 0.85)
KEEP = [tuple(k) for k in CFG.get("keep") or [[0, len(w) - 1]]]
PRE, POST = 0.10, 0.22
MAXGAP, NEWGAP = (0.9, 0.55) if CFG.get("tighten") else (99.0, 0.55)


def segments():
    """source time spans to keep, after splitting long internal pauses."""
    out = []
    for a, b in KEEP:
        cur = max(0.0, w[a]["start"] - PRE)
        for i in range(a, b):
            if w[i + 1]["start"] - w[i]["end"] > MAXGAP:
                out.append((cur, w[i]["end"] + NEWGAP / 2, a, i))
                cur = w[i + 1]["start"] - NEWGAP / 2
                a = i + 1
        end = w[b]["end"] + POST
        if b + 1 < len(w):
            end = min(end, w[b + 1]["start"] - 0.03)
        out.append((cur, end, a, b))
    return [(round(s, 3), round(e, 3), a, b) for s, e, a, b in out]


def remap_words(segs):
    words, t = [], 0.0
    for s, e, a, b in segs:
        for i in range(a, b + 1):
            x = w[i]
            words.append(dict(i=i, text=x["text"], start=round(t + x["start"] - s, 3), end=round(t + min(x["end"], e) - s, 3)))
        t += e - s
    return words, round(t, 3)


if __name__ == "__main__":
    segs = segments()
    words, total = remap_words(segs)
    starts, t = [], 0.0
    for s, e, a, b in segs:
        starts.append(round(t, 3)); t += e - s
    json.dump([dict(src_start=s, src_end=e, out_start=o) for (s, e, a, b), o in zip(segs, starts)], open("segments.json", "w"), indent=0)
    if "audio" in sys.argv:
        af = [f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,"
              f"afade=t=in:d=0.015,afade=t=out:st={e - s - 0.02:.3f}:d=0.02[a{k}]" for k, (s, e, _, _) in enumerate(segs)]
        fa = ";".join(af) + ";" + "".join(f"[a{k}]" for k in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1,highpass=f=80[ao]"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", fa, "-map", "[ao]", "-ar", "48000", "-ac", "1", "assets/vo.wav"], check=True)
        json.dump(words, open("transcript.json", "w"))
        json.dump({"vo_len": total, "cuts": starts[1:]}, open("vo_meta.json", "w"))
        print("segments", len(segs), "VO length", total)
    if "presenter" in sys.argv:
        key_src = CFG.get("green_key")
        vin = SRC if key_src else "pres_alpha.webm"
        vf = [f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS,fps=30,scale=720:932:flags=lanczos[v{k}]" for k, (s, e, _, _) in enumerate(segs)]
        key = ((f"colorkey={key_src}:0.16:0.06," if key_src else "") +
               "format=yuva444p,split=3[c][a1][a2];[a1]alphaextract,erosion,gblur=sigma=0.6[m];"
               "[a2]alphaextract,dilation,dilation,dilation,dilation,dilation,gblur=sigma=0.9[mo];"
               "[c][m]alphamerge[p];color=c=white:s=720x932:r=30,format=yuva444p[wb];[wb][mo]alphamerge[o];"
               "[o][p]overlay=format=auto:shortest=1,scale=1080:1398:flags=lanczos,format=yuva420p[vo]")
        fv = ";".join(vf) + ";" + "".join(f"[v{k}]" for k in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0," + key
        pre = [] if key_src else ["-c:v", "libvpx-vp9"]
        subprocess.run(["ffmpeg", "-v", "error", "-y", *pre, "-i", vin, "-filter_complex", fv, "-map", "[vo]", "-an",
                        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "3.5M", "-deadline", "realtime", "-cpu-used", "6",
                        "-row-mt", "1", "-auto-alt-ref", "0", "assets/presenter.webm"], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-c:v", "libvpx-vp9", "-i", "assets/presenter.webm",
                        "-frames:v", "1", "assets/presenter-last.png"], check=True)
        print("presenter done")
