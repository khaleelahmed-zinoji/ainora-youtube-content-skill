"""scenelib.py — tiny DSL that writes HyperFrames scene sub-compositions (HTML + one paused GSAP timeline).
All times are scene-local seconds (taken from scene_word_timing / words_compact). Deterministic, seek-safe."""
import html as H

FONT = '@font-face { font-family: "Sora"; font-style: normal; font-weight: 200 800; font-display: block; src: url("assets/fonts/sora-var.woff2") format("woff2"); }'


class Scene:
    def __init__(self, sid, dur):
        self.sid, self.dur, self.h, self.j, self.css = sid, round(dur, 3), [], [], []
        self.n = 0
        self.ev = []

    # ---------------------------------------------------------------- helpers
    def id(self, name=None):
        self.n += 1
        return f"{self.sid}-{name or 'e'}{self.n}"

    def js(self, s):
        self.j.append(s)

    def enter(self, eid, t, kind="up", d=0.5):
        K = {
            "up": ("{opacity:0, y:40}", "{opacity:1, y:0, ease:'power3.out'}"),
            "down": ("{opacity:0, y:-40}", "{opacity:1, y:0, ease:'power3.out'}"),
            "left": ("{opacity:0, x:-70}", "{opacity:1, x:0, ease:'power3.out'}"),
            "right": ("{opacity:0, x:70}", "{opacity:1, x:0, ease:'power3.out'}"),
            "pop": ("{opacity:0, scale:.8}", "{opacity:1, scale:1, ease:'back.out(1.7)'}"),
            "zoom": ("{opacity:0, scale:1.08}", "{opacity:1, scale:1, ease:'power2.out'}"),
            "fade": ("{opacity:0}", "{opacity:1, ease:'power1.out'}"),
            "rise": ("{opacity:0, y:120, rotation:-3}", "{opacity:1, y:0, rotation:0, ease:'back.out(1.4)'}"),
        }
        a, b = K[kind]
        self.js(f"tl.fromTo('#{eid}', {a}, Object.assign({b}, {{duration:{d}}}), {t:.2f});")

    def out(self, eid, t, kind="fade", d=0.3):
        if t is None:
            return
        if kind == "up":
            self.js(f"tl.to('#{eid}', {{opacity:0, y:-30, duration:{d}, ease:'power2.in'}}, {t:.2f});")
        elif kind == "left":
            self.js(f"tl.to('#{eid}', {{opacity:0, x:-80, duration:{d}, ease:'power2.in'}}, {t:.2f});")
        else:
            self.js(f"tl.to('#{eid}', {{opacity:0, duration:{d}, ease:'power1.in'}}, {t:.2f});")

    def float_(self, eid, t, amp=6, per=2.2):
        reps = max(1, int((self.dur - t) / per))
        self.js(f"tl.fromTo('#{eid}', {{y:0}}, {{y:-{amp}, duration:{per/2:.2f}, ease:'sine.inOut', yoyo:true, repeat:{reps*2-1}, immediateRender:false}}, {t+0.6:.2f});")

    def base(self, eid, cls, x, y, inner, w=None, h=None, extra=""):
        st = f"left:{x}px; top:{y}px; opacity:0;" + (f" width:{w}px;" if w else "") + (f" height:{h}px;" if h else "") + extra
        self.h.append(f'<div class="{cls}" id="{eid}" style="{st}">{inner}</div>')

    # ---------------------------------------------------------------- elements
    def kick(self, text, x, y, t, out=None, name="k"):
        e = self.id(name)
        self.base(e, "kick", x, y, f"<i></i>{H.escape(text)}")
        self.enter(e, t, "left", 0.45); self.out(e, out)
        return e

    def head(self, html_, x, y, t, size=64, out=None, kind="up", name="h", w=None, align=None):
        e = self.id(name)
        extra = f" font-size:{size}px;" + (f" text-align:{align};" if align else "")
        self.base(e, "head", x, y, html_, w=w, extra=extra)
        self.enter(e, t, kind, 0.55); self.out(e, out)
        return e

    def sub(self, text, x, y, t, out=None, size=28, name="s"):
        e = self.id(name)
        self.base(e, "sub", x, y, text, extra=f" font-size:{size}px;")
        self.enter(e, t, "up", 0.45); self.out(e, out)
        return e

    def panel(self, src, x, y, w, h, t, out=None, kind=None, ms=0.0, url=None, fit="cover", light=False, enter="rise",
              kb=1.05, bar=True, tag=None, tagpos=None, name="p", top=False, vdur=None, zoom=None):
        """Browser-framed media panel. video: plays from scene-local t for (out-t) or vdur seconds, starting ms into the file."""
        e = self.id(name)
        kind = kind or ("video" if src.endswith(".mp4") else "img")
        end = out if out is not None else self.dur
        cls = "pn-body" + (" contain" if fit == "contain" else "") + (" light" if light else "") + (" top" if top else "")
        if kind == "video":
            vd = round(min(vdur or 999, end - t + 0.4, self.dur - t), 3)
            media = (f'<video id="{e}-v" class="clip" src="{src}" data-start="{t:.2f}" data-duration="{vd}" '
                     f'data-media-start="{ms}" muted playsinline></video>')
        else:
            zs = f' style="transform-origin:{zoom[1]}% {zoom[2]}%; transform:scale({zoom[0]});"' if zoom else ""
            media = f'<img id="{e}-v" src="{src}" alt=""{zs} />'
        barh = f'<div class="pn-bar"><i></i><i></i><i></i><span>{H.escape(url or "")}</span></div>' if bar else ""
        inner = f'{barh}<div class="{cls}" id="{e}-b">{media}</div>'
        self.base(e, "pn" + ("" if bar else " nobar"), x, y, inner, w=w, h=h)
        self.enter(e, t, enter, 0.65)
        self.ev.append(('panel', t))
        if kb:
            self.js(f"tl.fromTo('#{e}-b', {{scale:1}}, {{scale:{kb}, duration:{max(1, end - t):.2f}, ease:'none'}}, {t:.2f});")
        if tag:
            tx, ty = tagpos or (x + 24, y + h - 70)
            te = self.id("tag")
            self.base(te, "pn-tag", tx, ty, H.escape(tag))
            self.enter(te, t + 0.5, "pop", 0.4); self.out(te, out)
        self.out(e, out, "fade", 0.35)
        return e

    def chip(self, html_, x, y, t, out=None, tone="", badge=None, kind="right", name="c", size=None, flt=True):
        e = self.id(name)
        b = f"<b>{badge}</b>" if badge else ""
        self.base(e, f"chip {tone}", x, y, f"{b}{html_}", extra=(f" font-size:{size}px;" if size else ""))
        self.ev.append(('chip', t))
        self.enter(e, t, kind, 0.45); self.out(e, out)
        if flt:
            self.float_(e, t, 4, 2.6)
        return e

    def stamp(self, text, x, y, t, out=None, tone="", rot=-6, size=None, name="st"):
        e = self.id(name)
        self.base(e, f"stamp {tone}", x, y, H.escape(text), extra=(f" font-size:{size}px;" if size else ""))
        self.ev.append(('stamp', t + 0.3))
        self.js(f"tl.fromTo('#{e}', {{opacity:0, scale:2.2, rotation:{rot}}}, {{opacity:1, scale:1, rotation:{rot}, duration:0.32, ease:'power4.in'}}, {t:.2f});")
        self.js(f"tl.fromTo('#{e}', {{x:0}}, {{x:6, duration:0.05, yoyo:true, repeat:5, immediateRender:false}}, {t+0.32:.2f});")
        self.out(e, out)
        return e

    def stat(self, label, x, y, t, value=None, count=None, sub=None, tone="", out=None, w=None, vsize=None, name="sv"):
        """count = (from, to, dur, fmt_js) where fmt_js is a JS arrow fn body using v."""
        e = self.id(name)
        vs = f' style="font-size:{vsize}px"' if vsize else ""
        inner = f'<div class="k">{H.escape(label)}</div><div class="v" id="{e}-n"{vs}>{value or ""}</div>' + (f'<div class="s">{sub}</div>' if sub else "")
        self.base(e, f"stat {tone}", x, y, inner, w=w)
        self.h[-1] = self.h[-1].replace('<div class="', '<div data-layout-allow-overlap="true" class="', 1)
        self.enter(e, t, "pop", 0.5); self.out(e, out)
        self.ev.append(('stat', t))
        if count:
            f, to, d, fmt = count
            self.js(f"(function(){{const o={{v:{f}}}; const el=document.getElementById('{e}-n'); const fmt=(v)=>{fmt}; el.textContent=fmt({f});"
                    f" tl.fromTo(o,{{v:{f}}},{{v:{to}, duration:{d}, ease:'power2.out', onUpdate:()=>{{el.textContent=fmt(o.v);}}}}, {t+0.15:.2f});}})();")
        self.float_(e, t, 5, 3.0)
        return e

    def bar(self, label, pct, x, y, w, t, val, tone="", out=None, d=1.0, name="b"):
        e = self.id(name)
        inner = f'<div class="lb">{label}</div><div class="tr"><div class="fl" id="{e}-f"></div></div><div class="vl">{val}</div>'
        self.base(e, f"bar {tone}", x, y, inner, w=w)
        self.enter(e, t, "up", 0.4)
        self.js(f"tl.fromTo('#{e}-f', {{scaleX:0}}, {{scaleX:{pct/100:.3f}, duration:{d}, ease:'power3.out'}}, {t+0.2:.2f});")
        self.out(e, out)
        return e

    def mcard(self, org, name_, desc, x, y, t, out=None, w=None, kind="pop", name="m"):
        e = self.id(name)
        self.base(e, "mcard", x, y, f'<div class="o">{org}</div><div class="n">{name_}</div><div class="d">{desc}</div>', w=w)
        self.enter(e, t, kind, 0.55); self.out(e, out)
        self.float_(e, t, 5, 3.2)
        return e

    def raw(self, html_, eid, t=None, kind="fade", out=None, d=0.5):
        if t is not None:
            html_ = html_.replace('style="', 'style="opacity:0; ', 1)
            self.enter(eid, t, kind, d)
        self.h.append(html_)
        self.out(eid, out)

    def deco(self, x, y, size, t, name="ring"):
        """slow rotating dashed ring + dot grid patch: fills empty canvas without competing."""
        e = self.id(name)
        self.raw(f'<div class="ring" id="{e}" style="left:{x}px; top:{y}px; width:{size}px; height:{size}px;"></div>', e, t, "fade", None, 1.0)
        self.js(f"tl.fromTo('#{e}', {{rotation:0}}, {{rotation:120, duration:{max(1, self.dur - t):.2f}, ease:'none', immediateRender:false}}, {t:.2f});")
        return e

    def dots(self, x, y, w, h, t, name="dg"):
        e = self.id(name)
        self.raw(f'<div class="dotgrid" id="{e}" style="left:{x}px; top:{y}px; width:{w}px; height:{h}px; opacity:.6"></div>', e, t, "fade", None, 1.0)
        self.js(f"tl.fromTo('#{e}', {{y:0}}, {{y:-26, duration:{max(1, self.dur - t):.2f}, ease:'none', immediateRender:false}}, {t:.2f});")
        return e

    # ---------------------------------------------------------------- Claude-edit additions
    def code(self, title, lines, x, y, w, t, times=None, out=None, name="cd", h=None):
        """dark code window; lines are pre-escaped HTML; each line fades in at times[i] (default staggered)."""
        e = self.id(name)
        times = times or [t + 0.35 + 0.18 * i for i in range(len(lines))]
        body = "".join(f'<div class="cl" id="{e}-l{i}">{ln}</div>' for i, ln in enumerate(lines))
        self.base(e, "code", x, y, f'<div class="cb"><i></i><i></i><i></i><span>{H.escape(title)}</span></div>{body}', w=w, h=h)
        self.enter(e, t, "rise", 0.6); self.ev.append(('panel', t))
        for i, tt in enumerate(times):
            self.js(f"tl.fromTo('#{e}-l{i}', {{opacity:0, x:-14}}, {{opacity:1, x:0, duration:0.25, ease:'power2.out'}}, {tt:.2f});")
        self.out(e, out, "fade", 0.35)
        return e

    def bubble(self, html_, x, y, t, out=None, me=False, name="bb", size=None):
        e = self.id(name)
        self.base(e, "bubble" + (" me" if me else ""), x, y, html_, extra=(f" font-size:{size}px;" if size else ""))
        self.enter(e, t, "pop", 0.45); self.out(e, out); self.ev.append(('chip', t))
        return e

    def strike(self, x, y, w, t, out=None, name="x"):
        e = self.id(name)
        self.h.append(f'<div class="xline" id="{e}" style="left:{x}px; top:{y}px; width:{w}px; opacity:0;"></div>')
        self.js(f"tl.fromTo('#{e}', {{opacity:1, scaleX:0}}, {{opacity:1, scaleX:1, duration:0.3, ease:'power2.out'}}, {t:.2f});")
        self.out(e, out); self.ev.append(('stamp', t))
        return e

    def wave(self, x, y, t, n=36, hmax=90, seed=3, color=None, out=None, name="wv", tail=False):
        e = self.id(name)
        import math
        bars = []
        for i in range(n):
            v = abs(math.sin(i * 0.9 + seed) * math.sin(i * 0.37 + seed * 2))
            hh = 10 + v * hmax
            if tail and i > n * 0.62:
                hh = 10 + v * hmax * max(0.0, 1 - (i - n * 0.62) / (n * 0.38)) * 0.55
            bars.append(f'<i style="height:{hh:.0f}px;{" background:" + color + ";" if color else ""}"></i>')
        self.base(e, "wave", x, y, "".join(bars), h=hmax + 12)
        self.enter(e, t, "fade", 0.4)
        self.js(f"tl.fromTo('#{e} i', {{scaleY:0.2}}, {{scaleY:1, duration:0.5, ease:'back.out(1.6)', stagger:0.015}}, {t:.2f});")
        self.out(e, out)
        return e

    def wordmark(self, x, y, t, size=96, out=None, name="wm"):
        e = self.id(name)
        self.base(e, "wm", x, y, "ainora<span>.ai</span>", extra=f" font-size:{size}px;")
        self.enter(e, t, "up", 0.55); self.out(e, out)
        return e

    # ---------------------------------------------------------------- output
    def html(self):
        return f'''<!doctype html>
<html><head><meta charset="UTF-8" /></head><body>
<template>
<style>
  {FONT}
  #{self.sid}-root {{ position: absolute; inset: 0; overflow: hidden; }}
  {chr(10).join(self.css)}
</style>
<link rel="stylesheet" href="shared.css" />
<div id="{self.sid}-root" class="sc-root" data-composition-id="{self.sid}" data-width="1920" data-height="1080" data-duration="{self.dur}">
  {chr(10).join("  " + x for x in self.h)}
</div>
<script>
(function () {{
  const tl = gsap.timeline({{ paused: true }});
  {chr(10).join("  " + x for x in self.j)}
  window.__timelines["{self.sid}"] = tl;
}})();
</script>
</template>
</body></html>
'''
