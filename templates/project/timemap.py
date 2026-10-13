"""timemap.py — R(t): move a time authored on an EARLIER take of the voice-over onto the current one.

Scenes are written in seconds of the voice-over. If you re-record (a cleaner take 2), keep take 1's
transcript as v1/transcript_edit.json and R() maps every beat to where the same words are spoken in
take 2 (word alignment + piecewise linear). With no v1 file, R() is the identity."""
import json, difflib, bisect, re, os

_n = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

if os.path.exists("v1/transcript_edit.json"):
    A = json.load(open("v1/transcript_edit.json"))
    B = json.load(open("transcript.json"))
    sm = difflib.SequenceMatcher(None, [_n(x["text"]) for x in A], [_n(x["text"]) for x in B], autojunk=False)
    PAIRS = [(0.0, 0.0)]
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            a, b = A[blk.a + k], B[blk.b + k]
            if a["start"] > PAIRS[-1][0] and b["start"] > PAIRS[-1][1]:
                PAIRS.append((a["start"], b["start"]))
    PAIRS.append((A[-1]["end"] + 10, B[-1]["end"] + 10))
    _X = [p[0] for p in PAIRS]

    def R(t):
        i = max(1, min(len(PAIRS) - 1, bisect.bisect_left(_X, t)))
        (x0, y0), (x1, y1) = PAIRS[i - 1], PAIRS[i]
        return round(y0 + (t - x0) * (y1 - y0) / (x1 - x0), 3)
else:
    def R(t):
        return round(t, 3)
