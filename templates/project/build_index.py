#!/usr/bin/env python3
"""build_index.py — writes compositions/sNN.html (from scenes.py), compositions/captions.html and index.html.

Host = lavender stage + 34 scene slots + one continuous keyed presenter layer whose mode
(FULL / LEFT / RIGHT / PIP / hidden) is animated on the MAIN timeline at global time + captions +
one premixed audio track (assets/mix.wav). The voice-over plays from t=0 exactly as assembled
(take 1 → Claude Motion take → take 1), never trimmed, sped up or re-cut."""
import json, html
from scenes import build
from timemap import R

SC = json.load(open("scenes.json"))
TOTAL = json.load(open("timeline.json"))["total"]
META = json.load(open("vo_meta.json"))
VO_LEN = META["vo_len"]
SCENES = [(f"s{s['id']:02d}", s["start"], round(s["start"] + s["duration"], 3)) for s in SC]

# presenter wrapper #pw: 1080x1398, left 420 / top -318 (bottom on canvas edge), origin bottom-centre
FULLCLIP = "inset(0px 0px 0px 0px round 0px)"
PIPCLIP = "inset(374px 193px 214px 193px round 80px)"
MODES = {
    "FULL": dict(x=0, y=0, scale=1.0, clip=FULLCLIP, card=0, o=1),
    "FULLs": dict(x=0, y=0, scale=0.9, clip=FULLCLIP, card=0, o=1),
    "LEFT": dict(x=-560, y=0, scale=0.96, clip=FULLCLIP, card=0, o=1),
    "RIGHT": dict(x=560, y=0, scale=0.96, clip=FULLCLIP, card=0, o=1),
    "PIP": dict(x=730, y=40, scale=0.42, clip=PIPCLIP, card=1, o=1),
}
def m(name, **kw):
    d = dict(MODES[name]); d.update(kw); return d
def hidden(name):
    return m(name, scale=MODES[name]["scale"] * 0.8, o=0)

T = {s[0]: s[1] for s in SCENES}
P = [
    (0.0, 0.0, m("FULL"), "none"),                              # hook: presenter is the focus
    (0.2, R(15.0) - 0.4, m("FULL", scale=1.04), "sine.inOut"),
    (T["s02"] - 0.05, 0.8, m("PIP"), "power3.inOut"),           # in / out panels
    (T["s03"] - 0.05, 0.8, m("RIGHT"), "power3.inOut"),         # why I stopped editing
    (T["s04"] - 0.05, 0.8, m("PIP"), "power3.inOut"),           # the stack
    (T["s05"] - 0.05, 0.8, m("LEFT"), "power3.inOut"),          # never repeat myself
    (T["s06"] - 0.05, 0.8, m("RIGHT"), "power3.inOut"),         # step 1
    (T["s07"] - 0.05, 0.8, m("PIP"), "power3.inOut"),           # step 2
    (T["s08"] - 0.05, 0.6, m("PIP"), "power3.inOut"),           # step 3: acts out each layout as he names it
    (R(235.05), 0.6, m("FULL"), "power3.inOut"),                   # "full screen"
    (R(237.85), 0.6, m("PIP"), "power3.inOut"),                    # "shrink into the corner"
    (R(240.95), 0.4, hidden("PIP"), "power2.in"),                  # "disappear"
    (R(244.3), 0.5, m("PIP"), "back.out(1.6)"),
    (T["s09"] - 0.05, 0.8, m("LEFT"), "power3.inOut"),          # step 4
    (R(304.1), 0.8, m("PIP"), "power3.inOut"),                     # draft 1 panel
    (T["s10"] - 0.05, 0.8, m("FULL"), "power3.inOut"),          # the part that still needs me
    (R(317.2), 0.7, m("RIGHT"), "power3.inOut"),                   # taste
    (R(323.8), 0.7, m("FULL", scale=1.06), "power3.inOut"),        # "cut to my face"
    (R(329.0), 0.8, m("LEFT"), "power3.inOut"),
    (T["s11"] - 0.05, 0.8, m("RIGHT"), "power3.inOut"),         # framework
    (T["s12"] - 0.05, 0.8, m("FULLs"), "power3.inOut"),         # close
    (R(400.3), 0.5, hidden("FULLs"), "power2.in"),                 # end card, no presenter
]

def js_state(d):
    return json.dumps({"x": d["x"], "y": d["y"], "scale": d["scale"], "opacity": d["o"], "clipPath": d["clip"]})

def presenter_js():
    out, prev, pc = [], None, None
    for (t, dur, st, ease) in P:
        cur = js_state(st)
        card = json.dumps({"opacity": st["card"] * st["o"], "scale": 1 if st["card"] else 0.6})
        if prev is None or dur == 0:
            out.append(f'tl.set("#pw", {cur}, {t:.2f});')
            out.append(f'tl.set("#pcard", {card}, {t:.2f});')
        else:
            out.append(f'tl.fromTo("#pw", {prev}, Object.assign({cur}, {{duration: {dur}, ease: "{ease}", immediateRender: false}}), {t:.2f});')
            out.append(f'tl.fromTo("#pcard", {pc}, Object.assign({card}, {{duration: {dur}, ease: "{ease}", immediateRender: false}}), {t:.2f});')
        prev, pc = cur, card
    return "\n      ".join(out)

# ------------------------------------------------------------------ captions (script wording, real timing)
FIXES = [
    ("edit by Claude.", "edited by Claude."), ("INOR.", "Ainora."), ("It is in the part you had guessed.", "It isn't the part you'd guess."),
    ("use a purple", "use our purple"), ("one off", "one-off"), ("walthroughs,", "walkthroughs,"), ("it is in the recording.", "it isn't the recording."),
    ("It is in the editing.", "It isn't the editing."), ("Used me two days", "It used to take me two days"),
    ("Cloud code", "Claude Code"), ("Cloud", "Claude"), ("Hyperframes", "HyperFrames"), ("air automation", "AI automation"),
    ("a shot,", "a short,"), ("It is in the part you had guess.", "It isn't the part you'd guess."),
    ("Let me set this up properly Because", "Let me set this up properly, because"), ("talked to,", "talk to,"), ("in.", "in?"),
    ("user purple.", "use our purple"), ("Every time It", "every time. It"), ("step one", "Step one"), ("old fashioned", "old-fashioned"),
    ("I normally", "I'd normally"), ("recording. by word.", "recording, word by word,"), ("W timestamps.", "with timestamps."),
    ("are now the", "are never the"), ("second minute so", "second minute. So"), ("said when", "said. When"),
    ("WhatsApp the WhatsApp lands", "\"WhatsApp\", the WhatsApp icon lands"), ("word not", "word. Not"), ("early on it now", "early. On it. Now"),
    ("scene it decides", "scene. It decides"), ("screen when", "screen, when"), ("corner when", "corner, when"), ("idea it draws", "idea. It draws"),
    ("and then before", "And then before"), ("MP4 mix", "MP4 mixed"), ("an N card", "an end card"), ("this one took", "This one took"),
    ("and I'd rather", "And I'd rather"), ("so the part", "So the part"), ("it is in the recording,", "it isn't the recording,"),
    ("it is in the editing.", "it isn't the editing."), ("jock", "joke"), ("flat, That", "flat, that"), ("I do in", "I'd do in"), ("grant work,", "grunt work,"),
    ("you will still", "you'll still"), ("you have never", "you've never")
]
NO_CAP = [(R(400.3), 9999)]   # end card

def caption_groups(words):
    ws = [dict(t=x["text"], s=x["start"], e=x["end"]) for x in words]
    toks = [w["t"] for w in ws]
    def replace_seq(a, b):
        nonlocal toks, ws
        A, B = a.split(" "), b.split(" ")
        i = 0
        while i <= len(toks) - len(A):
            if toks[i:i + len(A)] == A:
                s, e = ws[i]["s"], ws[i + len(A) - 1]["e"]
                n = len(B); span = (e - s) / n
                ws[i:i + len(A)] = [dict(t=B[k], s=s + k * span, e=s + (k + 1) * span) for k in range(n)]
                toks[i:i + len(A)] = B
                i += n
            else:
                i += 1
    for a, b in FIXES:
        replace_seq(a, b)
    groups, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        chars = sum(len(x["t"]) + 1 for x in cur)
        brk = (w["t"][-1] in ".?!:\"" or (w["t"][-1] == "," and len(cur) >= 3) or len(cur) >= 6 or chars > 34
               or (nxt and nxt["s"] - w["e"] > 0.45))
        if brk or nxt is None:
            groups.append(cur); cur = []
    merged = []
    for g in groups:   # no orphan single-word lines: fold them into the previous line when it still fits
        if merged and len(g) == 1 and g[0]["s"] - merged[-1][-1]["e"] < 0.5 and merged[-1][-1]["t"][-1] not in ".?!" \
                and sum(len(x["t"]) + 1 for x in merged[-1] + g) <= 42:
            merged[-1] = merged[-1] + g
        else:
            merged.append(g)
    return merged

def captions_html(groups):
    items, js = [], []
    for gi, g in enumerate(groups):
        start = g[0]["s"] - 0.08
        end = g[-1]["e"] + 0.25
        nxt = groups[gi + 1][0]["s"] - 0.1 if gi + 1 < len(groups) else TOTAL
        end = min(end if end - start > 0.9 else start + 0.9, nxt)
        for a, b in NO_CAP:
            if start < b and end > a:
                end = min(end, a)
        if end <= start:
            continue
        spans = "".join(f'<span id="cw{gi}_{k}">{html.escape(w["t"])}</span> ' for k, w in enumerate(g))
        items.append(f'<div class="cg" id="cg{gi}"><div class="cpill">{spans.strip()}</div></div>')
        js.append(f'tl.set("#cg{gi}", {{opacity: 1}}, {start:.2f}); tl.set("#cg{gi}", {{opacity: 0}}, {end:.2f});')
        for k, w in enumerate(g):
            js.append(f'tl.set("#cw{gi}_{k}", {{color: "#7c3aed"}}, {max(start, w["s"] - 0.03):.2f});')
    return f'''<!doctype html>
<html><head><meta charset="UTF-8" /></head><body>
<template>
<style>
  @font-face {{ font-family: "Sora"; font-style: normal; font-weight: 200 800; font-display: block; src: url("assets/fonts/sora-var.woff2") format("woff2"); }}
  #cap-root {{ position: absolute; inset: 0; pointer-events: none; }}
  .cg {{ position: absolute; left: 0; top: 968px; width: 1920px; display: flex; justify-content: center; opacity: 0; }}
  .cpill {{ font-family: "Sora", sans-serif; font-weight: 600; font-size: 34px; line-height: 1.2; color: rgba(29,20,66,.92);
           background: rgba(255,255,255,.9); padding: 10px 26px 12px; border-radius: 16px; white-space: nowrap;
           border: 1px solid rgba(124,58,237,.22); box-shadow: 0 8px 24px rgba(76,29,149,.15); }}
</style>
<div id="cap-root" data-composition-id="captions" data-width="1920" data-height="1080">
{chr(10).join(items)}
</div>
<script>
(function () {{
  const tl = gsap.timeline({{ paused: true }});
  {chr(10).join("  " + j for j in js)}
  window.__timelines["captions"] = tl;
}})();
</script>
</template>
</body></html>
'''

SECTION_CUTS = [T[k] for k in ["s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "s10", "s11", "s12"]]

def index_html(total=TOTAL, scenes=SCENES):
    slots = "\n    ".join(
        f'<div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
        f'data-start="{a}" data-duration="{round(b - a, 3)}" data-track-index="1" data-width="1920" data-height="1080"></div>'
        for sid, a, b in scenes)
    vo_len = min(VO_LEN, total)
    tail = "" if total <= VO_LEN else (f'<img id="plast" class="clip" src="assets/presenter-last.png" data-start="{VO_LEN}" '
                                       f'data-duration="{round(total - VO_LEN, 3)}" data-track-index="4" alt="" />')
    cuts = [c for c in SECTION_CUTS if c < total - 0.5]
    return f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <link rel="stylesheet" href="shared.css" />
    <style>
      @font-face {{ font-family: "Sora"; font-style: normal; font-weight: 200 800; font-display: block; src: url("assets/fonts/sora-var.woff2") format("woff2"); }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #f3eeff; }}
      #root {{ width: 100%; height: 100%; position: relative; overflow: hidden; font-family: "Sora", sans-serif; color: #1d1442; background: #f3eeff; }}
      #bg {{ position: absolute; inset: 0; overflow: hidden; }}
      #bg .base {{ position: absolute; inset: 0; background: radial-gradient(120% 100% at 70% 10%, #fbf8ff 0%, #f1eaff 40%, #e9e0ff 75%, #e2d6ff 100%); }}
      #bg .noise {{ position: absolute; inset: 0; background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .35  0 0 0 0 .2  0 0 0 0 .6  0 0 0 .55 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>"); background-size: 240px; opacity: .22; mix-blend-mode: multiply; }}
      #bg .grid {{ position: absolute; inset: -120px; background-image: linear-gradient(rgba(124,58,237,.045) 1px, transparent 1px), linear-gradient(90deg, rgba(124,58,237,.045) 1px, transparent 1px); background-size: 60px 60px; }}
      #bg .glow {{ position: absolute; border-radius: 50%; filter: blur(90px); }}
      #bg .g1 {{ width: 900px; height: 900px; left: -220px; top: -320px; background: #c4b5fd; opacity: .55; }}
      #bg .g2 {{ width: 800px; height: 800px; right: -220px; bottom: -380px; background: #f5d0fe; opacity: .55; }}
      #bg .g3 {{ width: 620px; height: 620px; left: 650px; top: 380px; background: #ddd6fe; opacity: .6; }}
      #vignette {{ position: absolute; inset: 0; background: radial-gradient(130% 110% at 50% 45%, transparent 60%, rgba(91,33,182,.14) 100%); pointer-events: none; }}
      #pcard {{ position: absolute; left: 1544px; top: 690px; width: 292px; height: 340px; border-radius: 34px; transform-origin: 50% 100%;
               background: radial-gradient(90% 80% at 50% 20%, #ffffff 0%, #f3eeff 45%, #ddd2ff 100%);
               box-shadow: 0 24px 60px rgba(76,29,149,.25), 0 0 0 2px rgba(124,58,237,.45); }}
      #pw {{ position: absolute; left: 420px; top: -318px; width: 1080px; height: 1398px; transform-origin: 50% 100%; }}
      #pv, #plast {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1398px; filter: drop-shadow(0 10px 22px rgba(46,16,101,.16)); }}
      #wipe {{ position: absolute; left: -900px; top: -200px; width: 700px; height: 1480px; background: linear-gradient(90deg, transparent, rgba(167,139,250,0) 10%, rgba(167,139,250,.45) 50%, rgba(255,255,255,0) 90%, transparent);
               transform: rotate(14deg); filter: blur(8px); opacity: 0; }}
      #fade {{ position: absolute; inset: 0; background: #000; opacity: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1920" data-height="1080">
    <div id="bg" data-layout-allow-overflow="true">
      <div class="base"></div>
      <div class="noise"></div>
      <div class="grid" id="bg-grid"></div>
      <div class="glow g1" id="bg-g1"></div><div class="glow g2" id="bg-g2"></div><div class="glow g3" id="bg-g3"></div>
    </div>
    {slots}
    <div id="pcard"></div>
    <div id="pw">
      <video id="pv" class="clip" src="assets/presenter.webm" data-start="0" data-duration="{vo_len}" data-track-index="3" muted playsinline></video>
      {tail}
    </div>
    <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{total}" data-track-index="5" data-track-kind="captions" data-width="1920" data-height="1080"></div>
    <div id="vignette"></div>
    <div id="wipe"></div>
    <div id="fade"></div>
    <audio id="mix" src="assets/mix.wav" data-start="0" data-duration="{total}" data-track-index="10" data-volume="1"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#bg-g1", {{ x: 0, y: 0 }}, {{ x: 260, y: 140, duration: {total / 2}, ease: "sine.inOut", yoyo: true, repeat: 1 }}, 0);
      tl.fromTo("#bg-g2", {{ x: 0, y: 0 }}, {{ x: -300, y: -120, duration: {total / 3}, ease: "sine.inOut", yoyo: true, repeat: 2 }}, 0);
      tl.fromTo("#bg-g3", {{ scale: 1, opacity: .32 }}, {{ scale: 1.25, opacity: .2, duration: {total / 6}, ease: "sine.inOut", yoyo: true, repeat: 5 }}, 0);
      tl.fromTo("#bg-grid", {{ x: 0, y: 0 }}, {{ x: 120, y: 120, duration: {total}, ease: "none" }}, 0);
      {presenter_js()}
      const cuts = {json.dumps(cuts)};
      cuts.forEach((c) => {{
        tl.fromTo("#wipe", {{ x: 0, opacity: 0 }}, {{ x: 3000, opacity: 1, duration: 0.55, ease: "power2.inOut", immediateRender: false }}, c - 0.3);
        tl.set("#wipe", {{ opacity: 0 }}, c + 0.27);
      }});
      tl.fromTo("#fade", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.4, ease: "power1.out" }}, 0);
      tl.fromTo("#fade", {{ opacity: 0 }}, {{ opacity: 1, duration: 1.0, ease: "power1.in", immediateRender: false }}, {total - 1.05});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''

if __name__ == "__main__":
    import sys
    scenes = build(SC)
    ev = []
    for sid, s in scenes.items():
        open(f"compositions/{sid}.html", "w").write(s.html())
        ev += [(round(T[sid] + t, 3), k) for k, t in s.ev]
    json.dump(sorted(ev), open("events.json", "w"))
    open("index.html", "w").write(index_html())
    # 40s sample: first scenes only
    if "--sample" in sys.argv:   # writes a 40s cut into a separate sample dir (keeps one root composition here)
        samp = [(sid, a, min(b, 40.0)) for sid, a, b in SCENES if a < 40.0]
        open(sys.argv[sys.argv.index("--sample") + 1] + "/index.html", "w").write(index_html(40.0, samp))
    words = json.load(open("transcript.json"))
    groups = caption_groups(words)
    open("compositions/captions.html", "w").write(captions_html(groups))
    json.dump([[round(g[0]["s"], 2), " ".join(w["t"] for w in g)] for g in groups], open("caption_groups.json", "w"), indent=0)
    print("scenes:", len(scenes), "caption groups:", len(groups))
