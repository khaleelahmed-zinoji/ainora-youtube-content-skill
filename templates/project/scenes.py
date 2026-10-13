"""scenes.py — the 12 scenes of "I Let Claude Edit My Entire Video" (v4: visuals, not echoed narration).
Times are written as GLOBAL seconds on the v1 timeline (scene_word_timing.txt) and moved onto the v2
recording with R(); L() then makes them scene-local. Layout zones follow the presenter mode in build_index.py:
  PIP   → presenter bubble bottom-right (x>1540, y>690): main panel x80-1380, side column x1420-1850 above y660
  LEFT  → presenter at x≈400: content x 860-1850
  RIGHT → presenter at x≈1520: content x 70-1100
  FULL  → presenter centre: content only in the side columns x<560 / x>1360
Rule (Khaleel, 2026-10-13): on-screen text is for labels, numbers and new info only. Never restate the line
he is saying; show it (UI mocks, diagrams, icons, callbacks, the real HyperFrames screen recording)."""
from scenelib import Scene
from timemap import R   # scene beats were authored on the v1 timeline; R() moves them onto v2

M = "assets/media/"
PX, PY, PW, PH = 80, 150, 1300, 773
RX = 1420
CHECK = "✓"
WA_SVG = ('<svg width="92" height="92" viewBox="0 0 32 32"><path fill="#fff" d="M16 3C8.8 3 3 8.7 3 15.8c0 2.5.7 4.9 2 6.9L3.2 29l6.5-1.7c1.9 1 4.1 1.6 6.3 1.6 7.2 0 13-5.7 13-12.8S23.2 3 16 3zm0 23.5c-2 0-3.9-.5-5.6-1.5l-.4-.2-3.9 1 1-3.7-.3-.4a10.4 10.4 0 0 1-1.6-5.6C5.2 10 10 5.3 16 5.3s10.8 4.7 10.8 10.6S22 26.5 16 26.5zm5.9-7.9c-.3-.2-1.9-.9-2.2-1s-.5-.2-.7.2-.8 1-1 1.2-.4.2-.7.1a8.8 8.8 0 0 1-4.4-3.8c-.3-.6.3-.5 1-1.7.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4s-1.2 1.1-1.2 2.8 1.2 3.2 1.4 3.5c.2.2 2.4 3.6 5.8 5 2.1.9 3 1 4 .8.7-.1 1.9-.8 2.2-1.5s.3-1.4.2-1.5-.3-.2-.6-.3z"/></svg>')


def build(sc):
    S = {s["id"]: s for s in sc}
    out = {}

    def mk(i):
        s = Scene(f"s{i:02d}", S[i]["duration"])
        o = S[i]["start"]
        return s, (lambda t: round(R(t) - o, 2))

    def box(s, cls, x, y, inner, t, kind="pop", out_=None, w=None, h=None, style="", name="bx", d=0.45):
        e = s.id(name)
        if "stamp" in cls or "pn-tag" in cls:
            cls += '" data-layout-allow-overlap="true'
        st = f"left:{x}px; top:{y}px;" + (f" width:{w}px;" if w else "") + (f" height:{h}px;" if h else "") + style
        s.raw(f'<div class="{cls}" id="{e}" style="{st}">{inner}</div>', e, t, kind, out_, d)
        if t is not None and kind in ("pop", "rise", "up", "right", "left"):
            s.ev.append(('stamp' if 'stamp' in cls else 'panel' if cls in ('pn', 'cal', 'lyr', 'tile claude') else 'chip', t))
        return e

    def nle(s, x, y, w, t, out_=None, kill=None):
        """mini editor timeline: 3 tracks of clips + keyframes. kill = (t_dim, t_kf, t_drag) to tear it down."""
        e = s.id("nle")
        cols = ["#8D81BD", "#655DA9", "#c4b5fd"]
        clips = [(0, 20, 120), (0, 160, 90), (1, 40, 150), (1, 220, 110), (2, 10, 80), (2, 120, 170)]
        kfs = [(0, 60), (0, 95), (0, 200), (1, 70), (1, 130), (1, 260), (2, 40), (2, 180), (2, 240)]
        inner = "".join(f'<div class="trk" style="top:{24 + k * 46}px;"></div>' for k in range(3))
        inner += "".join(f'<div class="cl2" id="{e}-c{i}" style="left:{26 + a * (w - 60) / 340:.0f}px; top:{28 + r * 46}px; width:{b * (w - 60) / 340:.0f}px; background:{cols[r]};"></div>'
                         for i, (r, a, b) in enumerate(clips))
        inner += "".join(f'<div class="kf" id="{e}-k{i}" style="left:{26 + a * (w - 60) / 340:.0f}px; top:{38 + r * 46}px;"></div>' for i, (r, a) in enumerate(kfs))
        inner += f'<div class="ph" id="{e}-ph" style="left:{w * 0.3:.0f}px;"></div>'
        s.raw(f'<div class="nle" id="{e}" style="left:{x}px; top:{y}px; width:{w}px; height:170px;">{inner}</div>', e, t, "rise", out_, 0.55)
        s.js(f"tl.fromTo('#{e}-ph', {{x:0}}, {{x:{w * 0.5:.0f}, duration:{max(1, (kill[0] if kill else t + 6) - t):.2f}, ease:'none', immediateRender:false}}, {t:.2f});")
        if kill:
            td, tk, tg = kill
            s.js(f"tl.to('#{e}', {{filter:'grayscale(1)', opacity:.45, duration:0.3}}, {td:.2f});")
            s.js(f"tl.to('#{e} .kf', {{y:140, rotation:225, opacity:0, duration:0.6, ease:'power2.in', stagger:0.04}}, {tk:.2f});")
            s.js(f"tl.to('#{e}-c3', {{x:90, y:-30, opacity:0, duration:0.5, ease:'power2.in'}}, {tg:.2f});")
            s.ev += [('stamp', td), ('chip', tk), ('chip', tg)]
        return e

    # 1 HOOK · FULL ------------------------------------------------------------------------------
    s, L = mk(1)
    s.dots(70, 120, 420, 280, 0.0)
    s.kick("Edited by Claude", 80, 80, L(0.4))
    s.chip("Every cut", 80, 300, L(1.4), badge=CHECK, tone="green", out=L(11.2))
    s.chip("Every caption", 80, 395, L(1.9), badge=CHECK, tone="green", out=L(11.2))
    s.chip("Every sound", 80, 490, L(2.4), badge=CHECK, tone="green", out=L(11.2))
    box(s, "vs", 1400, 175, "the editor", L(4.6), "fade", L(11.2), style=" color:#655DA9;")
    nle(s, 1390, 215, 470, L(4.5), out_=L(11.2), kill=(L(7.1), L(8.1), L(9.3)))
    box(s, "stamp", 1520, 260, "✕", L(5.9), "pop", L(11.2), style=" font-size:84px; padding:0 30px; transform:rotate(-8deg);")
    # the roadmap for the next minutes: four steps
    for k, (ic, lab) in enumerate([("🎙", "Record"), ("📝", "Transcribe"), ("🎬", "Build"), ("📦", "Render")]):
        box(s, "chip", 1430, 300 + k * 100, f"<b>{k + 1}</b>{ic} {lab}", L(12.4 + k * 0.45), "right", None)
    s.raw('<div id="s01-rl" style="position:absolute; left:1450px; top:330px; width:4px; height:300px; background:#c4b5fd; transform-origin:50% 0;"></div>', "s01-rl", None)
    s.js(f"tl.fromTo('#s01-rl', {{scaleY:0}}, {{scaleY:1, duration:1.6, ease:'power1.inOut'}}, {L(12.4):.2f});")
    out["s01"] = s

    # 2 TURN · PIP -----------------------------------------------------------------------------------
    s, L = mk(2)
    s.kick("What went in → what came out", PX, 70, L(16.2), out=L(32.2))
    s.panel(M + "in_raw.mp4", 110, 170, 440, 570, L(16.3), out=L(32.0), bar=False, ms=0.0, kb=1.03, tag="IN · raw phone take", tagpos=(130, 690))
    s.chip("+ script.md", 150, 770, L(19.6), out=L(32.0), badge="1")
    s.panel(M + "out_render.mp4", 760, 210, 820, 461, L(21.6), out=L(32.0), url="AI Weekly · Oct Week 1 · final render", ms=0.0, kb=1.03, tag="OUT", tagpos=(784, 620))
    # the space between them: a dotted path with four stops
    s.raw('<svg id="s02-path" style="position:absolute; left:550px; top:300px; width:220px; height:200px; overflow:visible;" viewBox="0 0 220 200">'
          '<path id="s02-pp" d="M0 150 C 60 20, 150 220, 210 60" fill="none" stroke="#8D81BD" stroke-width="5" stroke-dasharray="10 10" stroke-linecap="round"/></svg>', "s02-path", L(23.5), "fade", L(32.0))
    for k, (x, y) in enumerate([(560, 430), (615, 360), (690, 410), (745, 340)]):
        box(s, "chip", x, y, f"<b>{k + 1}</b>", L(27.1 + k * 0.35), "pop", L(32.0), style=" padding:6px; border-radius:14px;")
    # four jobs Claude now does + one mystery job that still needs a human
    for k, (ic, lab) in enumerate([("✂️", "Cuts"), ("💬", "Captions"), ("🎵", "Sound"), ("📦", "Render")]):
        box(s, "tile claude", 120 + k * 230, 300, f'<div class="ic">{ic}</div><div class="tl2">{lab}</div>', L(32.6 + k * 0.3), "rise", None)
    e = box(s, "tile mystery", 1040, 300, '<div class="ic">?</div><div class="tl2">You</div>', L(34.6), "pop", None)
    s.js(f"tl.fromTo('#{e}', {{scale:1}}, {{scale:1.07, duration:0.5, yoyo:true, repeat:5, ease:'sine.inOut', immediateRender:false}}, {L(35.3):.2f});")
    box(s, "pn-tag", 1050, 520, "revealed at the end", L(37.8), "up", None)
    out["s02"] = s

    # 3 WHY · RIGHT ------------------------------------------------------------------------------------
    s, L = mk(3)
    s.kick("Why I stopped editing by hand", 90, 70, L(40.8), out=L(59.6))
    e = box(s, "chip", 100, 170, "<b>⏱</b>a few minutes saved", L(43.6), "up", L(47.3))
    s.strike(170, 205, 270, L(44.6), out=L(47.3))
    s.raw('<img id="s03-logo" src="assets/brand/ainora-logo-dark.png" alt="" style="position:absolute; left:92px; top:120px; width:300px;" />', "s03-logo", L(47.6), "up", L(59.6))
    box(s, "logo-sub", 100, 290, "AI automation for businesses", L(49.0), "up", L(59.6))
    box(s, "logo-sub", 100, 340, "Video is how we explain it.", L(51.7), "up", L(59.6))
    for k, (ic, lab, t) in enumerate([("📰", "News breakdown", 56.7), ("▶", "Short", 58.1), ("💡", "Explainer", 58.9)]):
        box(s, "chip", 100 + k * 330, 440, f"<b>{ic}</b>{lab}", L(t), "up", L(59.6))
    # the real thing: editing one element by hand in HyperFrames Studio
    for k in (1, 0):   # "every single one": the stack of videos behind it
        box(s, "pn", 90 + 26 * (k + 1), 130 - 22 * (k + 1), "", L(64.5 + (1 - k) * 0.25), "fade", L(67.0), w=960, h=594, style=" opacity:.6;")
    s.panel(M + "sr_full.mp4", 90, 130, 960, 594, L(60.2), out=L(67.0), url="HyperFrames Studio · editing by hand", ms=0.0, kb=1.0, vdur=7.2,
            tag="real screen recording · 2× speed", tagpos=(110, 660))
    st = s.stat("Per video", 760, 760, L(61.9), count=(0, 3.5, 1.6, "v.toFixed(1) + ' hrs'"), sub="in the editor", tone="red", w=330, vsize=72, out=L(67.0))
    # a working week eaten by editing
    box(s, "vs", 100, 150, "One person · one week", L(67.3), "fade", L(79.0), style=" color:#655DA9;")
    days = "".join(f'<div class="day"><div class="dn">{d}</div><div class="blk" id="s03-b{k}" style="top:{50 + (k % 2) * 30}px; height:{160 + (k * 37) % 70}px;"><span>edit</span></div></div>'
                   for k, d in enumerate(["MON", "TUE", "WED", "THU", "FRI"]))
    box(s, "cal", 100, 200, days, L(67.5), "up", L(79.0))
    s.js(f"tl.fromTo('#s03-root .blk', {{scaleY:0}}, {{scaleY:1, duration:0.5, ease:'power2.out', stagger:0.3}}, {L(68.7):.2f});")
    s.ev.append(('chip', L(68.7)))
    # "no economic sense": a rubber stamp slammed down from the camera onto the free space, frame shakes
    s.raw('<div class="stamp" id="s03-nes" data-layout-allow-overlap="true" style="left:90px; top:600px; font-size:66px; padding:14px 34px; border-width:7px; opacity:0;">No Economic Sense</div>', "s03-nes", None)
    s.js(f"tl.fromTo('#s03-nes', {{opacity:0, scale:4.2, rotation:-16, filter:'blur(10px)'}}, {{opacity:1, scale:1, rotation:-6, filter:'blur(0px)', duration:0.34, ease:'power4.in'}}, {L(72.6):.2f});")
    s.js(f"tl.fromTo('#s03-root', {{x:0, y:0}}, {{x:7, y:5, duration:0.05, yoyo:true, repeat:5, ease:'none', immediateRender:false}}, {L(72.6) + 0.34:.2f});")
    s.js(f"tl.to('#s03-nes', {{opacity:0, duration:0.3}}, {L(76.0):.2f});")
    s.ev.append(('stamp', L(72.6) + 0.34))
    s.panel(M + "sr_tl.mp4", 100, 560, 960, 250, L(76.2), out=L(79.0), bar=False, ms=4.0, kb=1.0, vdur=3.0, tag="keyframes", tagpos=(120, 760))
    # the idea: talk to the editor instead
    box(s, "vs", 100, 150, "What if…", L(79.2), "fade", None, style=" color:#655DA9;")
    s.bubble("Make the video from my voice-over.", 100, 260, L(83.4), me=True)
    s.bubble("On it. Building 12 scenes…", 100, 370, L(85.0))
    e = box(s, "nle", 100, 520, "", L(85.8), "fade", None, w=520, h=150, style=" opacity:.5;")
    box(s, "stamp", 230, 560, "✕ drag", L(86.9), "pop", None, style=" font-size:40px; transform:rotate(-6deg);")
    out["s03"] = s

    # 4 STACK · PIP -----------------------------------------------------------------------------------
    s, L = mk(4)
    s.kick("The whole stack", PX, 70, L(90.0), out=L(119.0))
    s.mcard("1 · the worker", "Claude Code", "files on my Mac · runs commands", PX, 150, L(94.7), w=560, out=L(119.0))
    s.code("terminal", ['<span class="p">$</span> claude', '<span class="c"># reads the folder, writes the scenes, runs the render</span>'],
           PX, 380, 560, L(98.6), times=[L(98.8), L(100.4)], out=L(119.0))
    box(s, "arrow", 660, 220, "→", L(104.0), "left", L(119.0))
    s.mcard("2 · the builder", "HyperFrames", "every scene is a web page", 740, 150, L(104.2), w=600, out=L(119.0))
    s.code("compositions/s07.html", ['<span class="k">&lt;div</span> <span class="n">data-start</span>=<span class="s">"152.4"</span><span class="k">&gt;</span>',
                                     '  <span class="c">&lt;!-- HTML --&gt;</span>', '  <span class="p">tl</span>.fromTo(<span class="s">"#icon"</span>, …)', '  <span class="c">// timing = your words</span>'],
           740, 380, 600, L(108.3), times=[L(108.6), L(110.5), L(111.5), L(112.3)], out=L(119.0))
    box(s, "bigicon", RX + 60, 200, "🎞", L(116.5), "pop", L(119.0), w=150, h=150, style=" font-size:72px;")
    box(s, "vs", RX + 66, 370, ".mp4", L(116.8), "up", L(119.0), style=" color:#059669; font-size:30px;")
    s.mcard("3 · the brief", "Skills", "read before every job", PX, 150, L(119.9), w=520)
    s.code("~/.claude/skills/ainoravideoskill/SKILL.md", [
        '<span class="c"># a written brief Claude reads before it starts</span>',
        '<span class="k">brand</span>:   Ainora',
        '<span class="k">font</span>:    <span class="s">Sora</span> (embedded)',
        '<span class="k">palette</span>: <span class="s">#655DA9</span>  <span class="s">#8D81BD</span>',
        '<span class="k">logo</span>:    assets/brand/ainora-logo-dark.png',
        '<span class="k">scenes</span>:  the proven 7-beat template',
        '<span class="k">sound</span>:   cue map · which sfx, which moment'],
        PX, 360, 1060, L(122.5), times=[L(122.8), L(129.1), L(130.1), L(131.2), L(132.4), L(133.6), L(135.1)])
    box(s, "", 1200, 600, '<div style="display:flex; gap:14px;"><div style="width:70px;height:70px;border-radius:18px;background:#655DA9"></div><div style="width:70px;height:70px;border-radius:18px;background:#8D81BD"></div></div>',
        L(131.2), "pop", None, style=" position:absolute;")
    s.raw('<img id="s04-lg" src="assets/brand/ainora-logo-dark.png" alt="" style="position:absolute; left:1200px; top:440px; width:180px;" />', "s04-lg", L(132.4), "pop")
    out["s04"] = s

    # 5 NEVER REPEAT · LEFT -----------------------------------------------------------------------------
    s, L = mk(5)
    s.bubble("Use our purple.", 900, 150, L(140.7), me=True, out=L(146.3))
    s.bubble("Use our purple. Again.", 900, 260, L(142.0), me=True, out=L(146.3))
    s.bubble("Use our purple!!", 900, 370, L(143.3), me=True, out=L(146.3))
    box(s, "bigicon", 1500, 230, "✓", L(145.0), "pop", L(146.3), w=170, h=170, style=" font-size:96px; color:#059669;")
    e = s.id("doc")
    s.raw(f'<div id="{e}" style="position:absolute; left:900px; top:180px; width:420px; height:520px; border-radius:22px; background:#fff; border:1px solid rgba(109,40,217,.2); box-shadow:0 26px 60px rgba(76,29,149,.18); padding:34px; overflow:hidden;">'
          '<div style="font-size:18px; font-weight:800; letter-spacing:.2em; color:#655DA9;">DAY 1 · ONBOARDING</div>'
          + "".join(f'<div style="margin-top:24px; height:16px; width:{w}px; border-radius:8px; background:rgba(101,93,169,.18)"></div>' for w in (330, 280, 340, 220, 300, 260, 320, 180, 290))
          + f'<div id="{e}-scan" style="position:absolute; left:0; right:0; top:0; height:70px; background:linear-gradient(180deg, transparent, rgba(141,129,189,.45), transparent);"></div></div>', e, L(150.4), "rise")
    box(s, "bigicon", 1360, 200, "🧑‍💻", L(153.1), "pop", None, w=140, h=140)
    box(s, "vs", 1370, 360, "new editor · day 1", L(153.3), "fade", None, style=" color:#4b4390; font-size:18px;")
    s.js(f"tl.fromTo('#{e}-scan', {{y:-70}}, {{y:520, duration:0.9, ease:'none', repeat:3, immediateRender:false}}, {L(156.0):.2f});")
    for k in range(4):   # every video gets the whole brief
        box(s, "chip", 1360, 430 + k * 90, f"<b>{CHECK}</b>video {k + 1}", L(156.6) + k * 0.9, "right", None, style=" font-size:24px;")
    out["s05"] = s

    # 6 STEP 1 · RIGHT --------------------------------------------------------------------------------------
    s, L = mk(6)
    s.kick("Step 1 · record and hand it over", 90, 70, L(161.3))
    e = s.id("ph")
    s.raw(f'<div id="{e}" style="position:absolute; left:100px; top:150px; width:200px; height:360px; border-radius:36px; background:#1d1442; padding:12px;">'
          '<div style="width:100%; height:100%; border-radius:26px; background:linear-gradient(160deg,#ede9fe,#c4b5fd); display:flex; align-items:center; justify-content:center;">'
          '<div style="width:54px; height:54px; border-radius:50%; background:#e11d48; box-shadow:0 0 0 10px rgba(225,29,72,.2)"></div></div></div>', e, L(163.0), "rise", L(177.9))
    r = box(s, "rec", 340, 170, '<i></i><span id="s06-rt">00:00</span>', L(166.6), "pop", L(177.9))
    s.js(f"(function(){{const o={{v:0}}; const el=document.getElementById('s06-rt'); tl.fromTo(o,{{v:0}},{{v:334, duration:{L(171.6) - L(166.8):.2f}, ease:'power1.in', onUpdate:()=>{{const m=Math.floor(o.v/60), x=Math.floor(o.v%60); el.textContent=String(m).padStart(2,'0')+':'+String(x).padStart(2,'0');}}}}, {L(166.8):.2f});}})();")
    box(s, "chip", 340, 270, "<b>1</b>take", L(171.3), "up", L(177.9))
    s.code("Claude Edits My Video/", ['📁 <span class="s">Voice over v2.MOV</span>', '📄 <span class="s">script.md</span>'],
           340, 360, 620, L(172.7), times=[L(173.9), L(174.8)], out=L(177.9))
    # by hand vs by prompt
    box(s, "vs", 100, 140, "by hand", L(178.0), "fade", None, style=" color:#e11d48;")
    s.panel(M + "sr_full.mp4", 100, 180, 620, 384, L(178.0), url="1 element · dozens of keyframes", ms=6.0, kb=1.0, vdur=9.0, enter="left")
    box(s, "vs", 760, 330, "vs", L(178.4), "pop", None, style=" color:#655DA9; font-size:34px;")
    box(s, "vs", 100, 610, "by prompt", L(176.4), "fade", None, style=" color:#059669;")
    s.code("prompt", ['<span class="p">›</span> Use Ainora Youtube Content Generation Skill to generate the youtube video with the uploaded Voice over and Script in the project folder'],
           100, 650, 1000, L(176.4), times=[L(176.8)])
    box(s, "chip", 820, 200, "<b>🎬</b>scenes", L(180.8), "up", None, style=" font-size:24px;")
    s.strike(870, 228, 110, L(181.5))
    box(s, "chip", 820, 290, "<b>🎵</b>music", L(183.2), "up", None, style=" font-size:24px;")
    s.strike(870, 318, 100, L(183.8))
    box(s, "chip", 820, 400, "<b>✓</b>SKILL.md", L(188.9), "pop", None, style=" font-size:24px;")
    out["s06"] = s

    # 7 STEP 2 · PIP ------------------------------------------------------------------------------------------
    s, L = mk(7)
    s.kick("Step 2 · it listens before it builds", PX, 70, L(190.9), out=L(203.2))
    s.code("transcript.json · my actual recording", [
        '<span class="p">{</span> <span class="k">"text"</span>: <span class="s">"Before"</span>,   <span class="k">"start"</span>: <span class="n">156.94</span> <span class="p">}</span>',
        '<span class="p">{</span> <span class="k">"text"</span>: <span class="s">"it"</span>,       <span class="k">"start"</span>: <span class="n">157.42</span> <span class="p">}</span>',
        '<span class="p">{</span> <span class="k">"text"</span>: <span class="s">"builds"</span>,   <span class="k">"start"</span>: <span class="n">157.66</span> <span class="p">}</span>',
        '<span class="p">{</span> <span class="k">"text"</span>: <span class="s">"anything"</span>, <span class="k">"start"</span>: <span class="n">158.30</span> <span class="p">}</span>',
        '<span class="c">  … 936 words, every one timestamped</span>'],
        PX, 150, 1150, L(195.1), times=[L(195.2), L(195.7), L(195.9), L(196.6), L(200.5)], out=L(203.0))
    s.wave(PX + 20, 560, L(200.4), n=70, hmax=60, seed=4, out=L(203.0))
    for k in range(9):
        box(s, "", PX + 40 + k * 120, 530, "", L(200.5) + k * 0.12, "fade", L(203.0), w=3, h=110, style=" position:absolute; background:#655DA9; border-radius:2px;")
    # what I wrote vs what I said: same words, different rhythm
    words = ["I", "pause", "I", "rush", "a", "section", "I", "add", "a", "line"]
    box(s, "vs", PX + 10, 160, "the script", L(204.9), "fade", L(214.0), style=" color:#8D81BD;")
    box(s, "vs", PX + 10, 380, "the recording", L(205.8), "fade", L(214.0), style=" color:#655DA9;")
    for k, wd in enumerate(words):
        box(s, "chip", PX + 10 + k * 128, 210, wd, L(205.2) + k * 0.05, "up", L(214.0), style=" font-size:22px; padding:10px 14px;")
    xs = [0, 1, 3.2, 4.05, 4.9, 5.75, 7.0, 8.0, 9.0, 10.0]          # real delivery: a gap, a rush, an extra line
    for k, wd in enumerate(words):
        e = box(s, "chip", PX + 10 + k * 128, 430, wd, L(205.9) + k * 0.05, "up", L(214.0), style=" font-size:22px; padding:10px 14px;")
        s.js(f"tl.to('#{e}', {{x:{(xs[k] - k) * 112:.0f}, duration:0.5, ease:'power2.inOut'}}, {L(209.0):.2f});")
        if k >= 6:
            s.js(f"tl.to('#{e}', {{backgroundColor:'#d1fae5', borderColor:'#059669', duration:0.3}}, {L(211.2):.2f});")
    box(s, "pn-tag", PX + 160, 510, "pause", L(209.2), "pop", L(214.0))
    box(s, "pn-tag", PX + 420, 510, "rushed", L(210.0), "pop", L(214.0), style=" background:#d97706;")
    box(s, "pn-tag", PX + 800, 510, "+ ad-lib", L(211.4), "pop", L(214.0), style=" background:#059669;")
    # animate to the script → drift
    s.raw('<div class="drift" id="s07-d1" style="left:100px; top:300px; width:900px; background:#8D81BD;">your voice</div>', "s07-d1", L(214.6), "fade", L(220.1))
    s.raw('<div class="drift" id="s07-d2" style="left:100px; top:370px; width:900px; background:#e11d48;">animation timed to the script</div>', "s07-d2", L(214.8), "fade", L(220.1))
    s.js(f"tl.fromTo('#s07-d2', {{x:0}}, {{x:180, duration:3.2, ease:'power1.in', immediateRender:false}}, {L(216.3)});")
    s.stat("Drift", 100, 460, L(217.6), count=(0, 2, 1.6, "'0' + Math.floor(v) + ':00'"), sub="minutes in · visibly off", tone="red", w=360, vsize=72, out=L(220.1))
    # …so it animates to what I said: the WhatsApp icon lands on the word
    e = "s07-wa"
    s.raw(f'<div class="wa" id="{e}" style="left:560px; top:330px;">{WA_SVG}</div>', e, None)
    s.js(f"tl.fromTo('#{e}', {{opacity:0, scale:0.2, y:-260}}, {{opacity:1, scale:1, y:0, duration:0.42, ease:'back.out(2.2)'}}, {L(224.73) - 0.3:.2f});")
    s.js(f"tl.fromTo('#{e}', {{scale:1}}, {{scale:1.12, duration:0.12, yoyo:true, repeat:1, ease:'power2.out', immediateRender:false}}, {L(224.73) + 0.12:.2f});")
    s.ev.append(('stamp', L(224.73)))
    s.wave(260, 560, L(221.0), n=60, hmax=70, seed=5)
    s.raw('<div id="s07-mk" style="position:absolute; left:633px; top:520px; width:4px; height:120px; border-radius:2px; background:#25D366;"></div>', "s07-mk", L(224.6), "fade")
    s.chip("“…WhatsApp…”", 520, 700, L(224.73), badge="↓", tone="green", flt=False)
    s.stat("Offset", 900, 330, L(227.3), value="0.00 s", sub="icon vs spoken word", tone="green", w=330, vsize=72)
    box(s, "bigicon", 1000, 560, "✓", L(229.7), "pop", None, w=130, h=130, style=" font-size:80px; color:#059669;")
    out["s07"] = s

    # 8 STEP 3 · PIP → FULL → PIP → hidden → PIP --------------------------------------------------------------
    s, L = mk(8)
    s.kick("Step 3 · the build", PX, 70, L(230.5), out=L(244.3))
    for k in range(12):   # the deck of scenes, dealt one by one
        box(s, "chip", PX + (k % 6) * 200, 160 + (k // 6) * 110, f"<b>s{k + 1:02d}</b>", L(231.4) + k * 0.12, "pop", L(235.0), style=" padding:10px 18px;")
    for k, (lab, t, kind) in enumerate([("full", 235.3, "full"), ("corner", 238.1, "pip"), ("hidden", 241.2, "none")]):
        e = s.id("mini")
        ph = {"full": '<div class="ph" style="left:95px; top:40px; width:70px; height:120px;"></div>',
              "pip": '<div class="ph" style="left:200px; top:100px; width:34px; height:60px;"></div>', "none": ""}[kind]
        s.raw(f'<div class="mini" id="{e}" style="left:110px; top:{170 + k * 240}px; overflow:visible;"><div class="bg"></div>{ph}<div class="lb">{lab}</div></div>', e, L(t), "pop", L(244.3))
        s.ev.append(('chip', L(t)))
    box(s, "bigicon", 760, 300, "💡", L(241.5), "pop", L(244.3), w=300, h=300, style=" font-size:170px; border-radius:60px;")
    # exploded layer stack: what goes on top of the footage
    lays = [("Characters &amp; metaphors", "#8D81BD", 244.9), ("Captions", "#655DA9", 247.4), ("Music bed", "#a78bfa", 249.4), ("Sound effects", "#7c6fd0", 253.3)]
    for k, (lab, col, t) in enumerate(lays):
        box(s, "lyr", 200 + k * 70, 150 + k * 90, lab, L(t), "rise", L(257.6), style=f" background:{col}; transform:rotate(-4deg) skewX(-6deg);")
    s.wave(620, 342, L(250.0), n=24, hmax=40, seed=2, color="#ffffff", out=L(257.6))
    box(s, "chip", RX, 300, "<b>🔉</b>−22 dB", L(256.7), "pop", L(257.6), style=" font-size:24px;")
    box(s, "vs", 110, 190, "room echo", L(259.5), "fade", L(263.6), style=" color:#e11d48;")
    s.wave(110, 230, L(259.5), n=44, hmax=110, seed=1, color="#c4b5fd", out=L(263.6))
    box(s, "vs", 110, 420, "cleaned", L(261.5), "fade", L(263.6), style=" color:#059669;")
    s.wave(110, 460, L(261.5), n=44, hmax=110, seed=1, tail=True, out=L(263.6))
    s.code("npx hyperframes check", [
        '<span class="p">●</span> lint ............... <span class="s">ok</span>',
        '<span class="n">⚠</span> s07: text runs off the screen',
        '<span class="n">⚠</span> s11: scene with nothing in it',
        '<span class="p">●</span> fixed · re-checked .. <span class="s">0 errors</span>'],
        PX, 160, 1100, L(264.0), times=[L(266.9), L(271.7), L(275.0), L(276.9)])
    out["s08"] = s

    # 9 STEP 4 · LEFT → PIP at draft ----------------------------------------------------------------------------
    s, L = mk(9)
    s.kick("Step 4 · the render", 880, 70, L(278.4), out=L(288.2))
    e = s.id("pg")
    s.raw(f'<div class="prog" id="{e}" style="left:900px; top:170px; width:900px;"><i id="{e}-i"></i></div>', e, L(278.4), "fade", L(288.2))
    s.js(f"tl.fromTo('#{e}-i', {{scaleX:0}}, {{scaleX:1, duration:{L(280.4) - L(278.6):.2f}, ease:'power1.inOut'}}, {L(278.6)});")
    s.chip("final.mp4", 900, 240, L(280.4), badge="▶", tone="green", out=L(288.2))
    s.chip("−14 LUFS · YouTube loudness", 900, 340, L(282.5), badge="🔊", out=L(288.2), size=26)
    e = s.id("ec")
    s.raw(f'<div id="{e}" style="position:absolute; left:900px; top:450px; width:620px; height:300px; border-radius:24px; background:linear-gradient(160deg,#655DA9,#8D81BD); box-shadow:0 26px 60px rgba(76,29,149,.3);">'
          '<div style="position:absolute; left:40px; top:44px; font-size:64px; font-weight:800; color:#fff; letter-spacing:-.04em;">ainora.ai</div>'
          '<div style="position:absolute; left:40px; top:170px; padding:16px 26px; border-radius:18px; background:#25D366; color:#fff; font-size:30px; font-weight:800;">WhatsApp · 0526235035</div></div>',
          e, L(284.4), "rise", L(288.2))
    s.kick("How long it took", 880, 70, L(288.4), out=L(298.0))
    s.stat("Before", 900, 160, L(289.5), value="2 days", sub="minimum · idea → finished video", tone="red", w=430, vsize=96, out=L(298.0))
    s.stat("This video", 1380, 160, L(295.3), value="1 hour", sub="idea → final render", tone="green", w=430, vsize=96, out=L(298.0))
    # first try: a filmstrip, one frame circled in red
    strip = "".join(f'<div style="width:170px; height:100px; border-radius:10px; background:linear-gradient(135deg,#ede9fe,#c4b5fd);"></div>' for _ in range(5))
    box(s, "", 900, 520, f'<div style="display:flex; gap:12px; padding:16px; border-radius:16px; background:#1d1442;">{strip}</div>', L(298.4), "up", L(304.1), style=" position:absolute;")
    box(s, "", 1250, 495, "", L(301.15), "pop", L(304.1), w=210, h=150, style=" position:absolute; border:6px solid #e11d48; border-radius:50%;")
    # first draft: the real flaw from v4 (a bare "−$" at 1:07), the note, then the fix
    DW, DH = 900, 506
    s.panel(M + "draft1.mp4", PX, PY, DW, DH, L(304.4), out=L(307.6), url="draft 1 · 1:07", ms=0.0, kb=1.0, vdur=3.4, tag="DRAFT 1", tagpos=(PX + 24, PY + DH - 64))
    box(s, "note", 1030, 170, "<b>📝</b>A bare “−$” isn't enough. Put a “No Economic Sense” stamp in the free space, slammed in from the camera.", L(305.9), "rise", None, w=340, style=" font-size:24px; transform:rotate(-2deg);")
    s.panel(M + "fixed1.mp4", PX, PY, DW, DH, L(307.7), url="draft 2 · 1:07", ms=0.0, kb=1.0, vdur=4.2, tag="FIXED", tagpos=(PX + 24, PY + DH - 64), enter="zoom")
    box(s, "chip green", PX, PY + DH + 40, "<b>✓</b>no editor · one note in plain words", L(309.0), "up", None, style=" font-size:26px;")
    out["s09"] = s

    # 10 PAYOFF · FULL → RIGHT → FULL → LEFT ------------------------------------------------------------------------
    s, L = mk(10)
    box(s, "tile", 150, 330, '<div class="ic">🎙</div><div class="tl2">recording</div>', L(314.5), "rise", L(317.3))
    box(s, "stamp", 210, 380, "✕", L(315.0), "pop", L(317.3), style=" font-size:70px; padding:0 22px; transform:rotate(-8deg);")
    box(s, "tile", 1560, 330, '<div class="ic">✂️</div><div class="tl2">editing</div>', L(315.9), "rise", L(317.3))
    box(s, "stamp", 1620, 380, "✕", L(316.4), "pop", L(317.3), style=" font-size:70px; padding:0 22px; transform:rotate(-8deg);")
    # the mystery tile from the start flips: it was taste
    e = box(s, "tile mystery", 160, 150, '<div class="ic">?</div><div class="tl2">You</div>', L(317.3), "fade", None, w=300, h=300)
    s.js(f"tl.to('#{e}', {{rotationY:90, duration:0.25, ease:'power2.in'}}, {L(317.6):.2f});")
    e2 = box(s, "tile claude", 160, 150, '<div class="ic" style="font-size:110px;">👁</div><div class="tl2" style="font-size:40px;">TASTE</div>', None, "fade", L(323.7), w=300, h=300)
    s.js(f"tl.fromTo('#{e2}', {{opacity:0, rotationY:-90}}, {{opacity:1, rotationY:0, duration:0.3, ease:'power2.out'}}, {L(317.85):.2f});")
    s.ev.append(('stamp', L(317.85)))
    for k, (ic, txt, t) in enumerate([("🐢", "s04 — trim 2 s", 319.6), ("😐", "0:47 — cut the joke", 321.9)]):
        box(s, "note", 520 + k * 330, 220 + k * 40, f"<b>{ic}</b>{txt}", L(t), "rise", L(323.7), style=f" transform:rotate({-3 + k * 5}deg);")
    s.ev += [('chip', L(319.6)), ('chip', L(321.9))]
    # cut to my face: framing brackets close in
    br = "".join(f'<div style="position:absolute; {a}:0; {b}:0; width:70px; height:70px; border-{a}:8px solid #fff; border-{b}:8px solid #fff;"></div>'
                 for a, b in [("top", "left"), ("top", "right"), ("bottom", "left"), ("bottom", "right")])
    e = box(s, "", 560, 40, br, L(323.9), "fade", L(329.0), w=800, h=700, style=" position:absolute;")
    s.js(f"tl.fromTo('#{e}', {{x:0, y:0, width:800, height:700}}, {{x:210, y:40, width:380, height:440, duration:0.9, ease:'power3.inOut', immediateRender:false}}, {L(325.0):.2f});")
    box(s, "pn-tag", 1440, 200, "director's note · 1:12", L(324.2), "pop", L(329.0))
    # Claude's toolbox: every editor tool ticked, one thing missing
    tools = [("✂️", "cut"), ("💬", "captions"), ("🎵", "music"), ("◆", "keyframes"), ("🎨", "colour"), ("🔊", "mix")]
    for k, (ic, lab) in enumerate(tools):
        box(s, "tile", 880 + (k % 3) * 220, 130 + (k // 3) * 230, f'<div class="ic">{ic}</div><div class="tl2">{lab}</div>', L(330.0) + k * 0.15, "pop", L(338.0), w=190, h=190)
        box(s, "chip green", 1010 + (k % 3) * 220, 120 + (k // 3) * 230, "<b>✓</b>", L(331.0) + k * 0.15, "pop", L(338.0), style=" padding:4px;")
    box(s, "tile mystery", 1540, 360, '<div class="ic">🧭</div><div class="tl2">purpose</div>', L(333.3), "pop", L(338.0), w=240, h=240)
    # editor → director
    box(s, "bigicon", 900, 220, "✂️", L(339.2), "pop", None, w=200, h=200, style=" font-size:100px;")
    s.strike(890, 320, 220, L(340.3))
    box(s, "arrow", 1150, 270, "→", L(340.8), "left", None)
    box(s, "bigicon", 1280, 220, "🎬", L(341.3), "pop", None, w=200, h=200, style=" font-size:100px; border-color:#655DA9; border-width:4px;")
    for k, (ic, lab, t) in enumerate([("👀", "I watch", 342.3), ("📝", "I give notes", 343.3), ("⚙️", "Claude builds", 344.6)]):
        box(s, "chip" + (" green" if k == 2 else ""), 900 + k * 300, 520, f"<b>{ic}</b>{lab}", L(t), "up", None, style=" font-size:24px;")
    out["s10"] = s

    # 11 FOR WHO · RIGHT ----------------------------------------------------------------------------------------------
    s, L = mk(11)
    s.kick("Is it worth it for you?", 90, 70, L(346.9))
    th = lambda c, r: f'<div style="width:70px; height:46px; border-radius:8px; background:{c}; {r}"></div>'
    same = "".join(th("#8D81BD", "") for _ in range(3))
    diff = th("#8D81BD", "") + th("#f59e0b", "transform:rotate(8deg);") + th("#34d399", "border-radius:50%;")
    box(s, "", 100, 190, f'<div style="display:flex; gap:10px;">{same}</div>', L(350.8), "right", None, style=" position:absolute;")
    box(s, "vs", 100, 260, "same shape every week", L(353.3), "fade", None, style=" color:#4b4390; font-size:18px;")
    box(s, "arrow", 350, 165, "→", L(359.9), "left", None, style=" color:#4b4390;")
    bars = "".join(f'<div class="blk2" id="s11-b{k}" style="width:46px; height:{30 + k * 18}px; border-radius:8px 8px 0 0; background:linear-gradient(180deg,#34d399,#059669); transform-origin:50% 100%;"></div>' for k, _ in enumerate(range(8)))
    box(s, "", 460, 130, f'<div style="display:flex; align-items:flex-end; gap:10px; height:170px;">{bars}</div>', L(361.4), "fade", None, style=" position:absolute;")
    s.js(f"tl.fromTo('#s11-root .blk2', {{scaleY:0}}, {{scaleY:1, duration:0.4, ease:'back.out(1.6)', stagger:0.18}}, {L(361.6):.2f});")
    box(s, "vs", 470, 320, "time back · week by week", L(363.1), "fade", None, style=" color:#064e3b; font-size:20px; font-weight:800;")
    box(s, "", 100, 440, f'<div style="display:flex; gap:10px;">{diff}</div>', L(365.1), "right", None, style=" position:absolute;")
    box(s, "vs", 100, 510, "every video different", L(366.8), "fade", None, style=" color:#b45309; font-size:18px;")
    box(s, "arrow", 350, 415, "→", L(369.0), "left", None, style=" color:#4b4390;")
    for k in range(3):
        box(s, "note", 470 + k * 40, 400 + k * 22, "<b>📝</b>", L(371.4) + k * 0.4, "rise", None, w=150, style=f" transform:rotate({-6 + k * 6}deg); padding:14px;")
    box(s, "bigicon", 100, 650, "📄", L(375.4), "pop", None, w=140, h=140)
    box(s, "vs", 100, 805, "brand.md", L(376.9), "fade", None, style=" color:#4b4390; font-size:18px;")
    box(s, "stamp green", 290, 680, "start here", L(378.1), "pop", None, style=" font-size:40px; transform:rotate(-5deg);")
    box(s, "chip green", 640, 690, "<b>✓</b>with AI", L(383.5), "up", None, style=" font-size:24px;")
    box(s, "chip green", 860, 690, "<b>✓</b>without", L(385.0), "up", None, style=" font-size:24px;")
    out["s11"] = s

    # 12 CLOSE · FULL, then end card (no presenter) ------------------------------------------------------------------
    s, L = mk(12)
    box(s, "chip", 80, 300, "<b>↓</b>skills + exact prompt", L(387.6), "right", L(400.3))
    box(s, "vs", 90, 390, "in the description", L(390.4), "fade", L(400.3), style=" color:#655DA9;")
    box(s, "chip", 1380, 300, "<b>▶</b>new breakdown weekly", L(392.4), "left", L(400.3), style=" font-size:26px;")
    box(s, "chip green", 1380, 400, "<b>+</b>Subscribe", L(398.0), "pop", L(400.3))
    e = "s12-end"
    s.raw(f'<div id="{e}" style="position:absolute; inset:0; background:radial-gradient(120% 100% at 50% 30%, #8D81BD 0%, #655DA9 55%, #4b4390 100%);"></div>', e, L(400.4), "fade", None, 0.6)
    s.raw('<div class="head" id="s12-q" style="left:0; width:1920px; top:250px; text-align:center; font-size:84px; color:#fff;">Want videos like this <span style="color:#d9d2ff">for your business?</span></div>', "s12-q", L(400.8), "up")
    s.raw('<div class="wm" id="s12-wm" style="left:0; width:1920px; top:400px; text-align:center; font-size:110px; color:#fff;">ainora<span style="color:#d9d2ff">.ai</span></div>', "s12-wm", L(401.2), "up")
    s.raw('<div id="s12-cta" style="position:absolute; left:0; top:620px; width:1920px; display:flex; justify-content:center;"><div class="endcta" style="position:relative; font-size:44px;">Message us on WhatsApp · 0526235035</div></div>', "s12-cta", L(401.7), "pop")
    s.ev.append(('stamp', L(401.7)))
    out["s12"] = s
    return out
