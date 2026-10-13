#!/usr/bin/env python3
"""make_scenes.py — scene boundaries from the real transcript (scene start = first spoken word - 0.3s).
Scenes come from config.json "scenes": [[name, "first few words of the scene", search_after_seconds], ...]."""
import json
w = json.load(open("transcript.json")); meta = json.load(open("vo_meta.json")); CFG = json.load(open("config.json"))
END_HOLD = CFG.get("end_card_seconds", 4.2)          # voiceless end card after the last word
TOTAL = round(meta["vo_len"] + END_HOLD, 2)

def find(phrase, after=0):
    toks = phrase.lower().split(); T = [x["text"].lower().strip('.,?!:"') for x in w]
    for i in range(len(T)):
        if w[i]["start"] >= after and T[i:i + len(toks)] == toks: return w[i]["start"]
    raise SystemExit("not found in transcript: " + phrase)

P = CFG["scenes"]
st = [0.0] + [round(find(ph, af) - 0.3, 2) for _, ph, af in P[1:]]
sc = [dict(id=i + 1, name=n, start=st[i], duration=round((st[i + 1] if i + 1 < len(P) else TOTAL) - st[i], 2)) for i, (n, _, _) in enumerate(P)]
json.dump(sc, open("scenes.json", "w"), indent=1)
json.dump({"total": TOTAL, "vo_len": meta["vo_len"]}, open("timeline.json", "w"))
for s in sc: print(s)
print("total", TOTAL)
