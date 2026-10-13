---
name: ainora-youtube-content-generation
description: Ainora Youtube Content Generation Skill. Turns a talking-head voice-over recording plus its script (both in the project folder) into a finished 16:9 YouTube video built with HyperFrames - retakes removed, voice de-echoed, presenter keyed and moved between full / side / corner / hidden, motion graphics synced word-for-word to the real recording, captions, a ducked music bed, quiet SFX, a cold open, a WhatsApp end card, -14 LUFS delivery - and then packages it (titles, thumbnails, description, chapters). Use it whenever the user says "use Ainora Youtube Content Generation Skill", "make the YouTube video from my voice-over and script", "edit my video", or drops a VO + script into a project folder and asks for the video.
---

# Ainora YouTube Content Generation

One recording + one script in, one YouTube-ready video out. This is the exact pipeline used to make
"2 Days of Editing → 1 Hour: See Who Edits My Videos" (Ainora, 2026).

**Read first:** the HyperFrames skills (`npx hyperframes skills update general-video`, then `/hyperframes`,
`/hyperframes-core`). Every composition rule (timed `data-start`, one paused GSAP timeline per composition,
`window.__timelines`, muted video + separate audio, deterministic code) comes from there.

## 0. Set up the project

```bash
mkdir video && cp -r <this-skill>/templates/project/* video/ && cd video
mkdir -p assets/brand assets/fonts assets/music assets/sfx assets/media compositions
cp <this-skill>/brand/ainora-logo-dark.png assets/brand/      # or your own logo
# Sora variable font (OFL) from Google Fonts -> assets/fonts/sora-var.woff2
# two music beds you are licensed to use -> assets/music/bright.wav, assets/music/calm.wav
# soft SFX you are licensed to use -> assets/sfx/{whoosh-short,heavyclick,pop,tap,quickwhoosh}.mp3
```

Edit `config.json`: `source` (the recording), `green_key` (or `null` + background removal), `scenes`.

## 1. Transcribe the real recording (ground truth)

```bash
ffmpeg -i "$SOURCE" -vn -ac 1 -ar 16000 raw16k.wav
npx hyperframes transcribe raw16k.wav --dir tx --json && cp tx/transcript.json transcript_raw.json
```

Dump the words with indices and gaps (`i:word@start`, newline on gaps > 0.6 s) and read them all.

## 2. Edit the voice (only if needed)

- **Retakes / false starts:** set `keep` to the word ranges of the LAST clean take of each line.
- **Long pauses:** `"tighten": true` shortens pauses > 0.9 s to 0.55 s. No speed change, no word cut.
- A clean single take: leave `keep: null`, `tighten: false` and the recording is used as-is.

```bash
python3 make_vo.py audio
bash <this-skill>/scripts/clean_vo.sh        # DeepFilterNet3 + de-room expander -> assets/vo-clean.wav
```

**Verify the edit:** re-transcribe `assets/vo-clean.wav` and read it start to finish. Every splice must
read as one natural take. If a word is clipped, check the loudness profile around the splice and
move the cut into the silence.

## 3. Presenter

- Green screen: `"green_key": "0x00e575"` (sample your own green) -> `python3 make_vo.py presenter`.
- Plain wall: `npx hyperframes remove-background pres720.mp4 -o pres_alpha.webm` (~13 fps on Apple
  silicon), `"green_key": null`, then `python3 make_vo.py presenter`.

Output: `assets/presenter.webm` (1080x1398, white outline, transparent).

## 4. Scenes

`python3 make_scenes.py` turns the `scenes` phrases into boundaries from the real word timings.

Write `scenes.py` (see the worked example in `templates/project/scenes.py`). Each scene uses the tiny DSL
in `scenelib.py` (`kick`, `chip`, `stamp`, `stat`, `panel`, `code`, `bubble`, `wave`, `strike`, ...),
with every beat timed to the word it belongs to.

**The rule that makes it good:** on-screen text is for labels, numbers and new information only. Never
restate the line being spoken - the captions already carry the words. Show it instead: UI mocks,
diagrams, a calendar filling up, a layer stack, a real screen recording, a callback to an earlier
visual. Ask of every beat: "what should the viewer SEE that the words can't show?"

Presenter modes live in `build_index.py` (`P` list): `FULL`, `LEFT`, `RIGHT`, `PIP`, `hidden(...)`.
Respect the layout zones written at the top of `scenes.py`. Act out what is said when it is about the
layout itself ("full screen", "shrink into the corner", "disappear", "cut to my face").

Caption spelling fixes go in `FIXES` in `build_index.py` (ASR mishearings: "Cloud" -> "Claude", ...).

```bash
python3 build_index.py && python3 build_audio.py    # needs numpy
npx hyperframes check                               # fix every layout/overlap error
npx hyperframes snapshot --at 5,30,60,... --describe false   # look at EVERY scene's contact sheet
```

Common fixes: a kicker/heading never faded out under the next one (add `out=`), long code lines (they
wrap), stamps or text running under the presenter (move them into the free zone), contrast on small labels.

## 5. Render, cold open, deliver

```bash
npx hyperframes render -o renders/body.mp4
bash <this-skill>/scripts/coldopen_clip.sh renders/body.mp4 <start> <end> 1.3   # the showcase moment
cp -r <this-skill>/templates/coldopen ./coldopen && (cd coldopen && npx hyperframes render -o ../renders/coldopen.mp4)
bash <this-skill>/scripts/finish.sh renders/coldopen.mp4 renders/body.mp4 "../Final.mp4"   # -14 LUFS
```

The cold open ("the Premiere"): the finished clip at 1.3x inside a tilted floating frame, "FINAL
OUTPUT / Edited by Claude / 0 timelines / 0 keyframes" on the left, "How was this made? -> Watch the
breakdown" on the right, then the frame straightens and fills the screen and hard-cuts to the hook.
Set `data-duration` in `coldopen/index.html` to the clip length.

**First-draft moment (if the script has one):** render once, take the real flaw from that render as
`assets/media/draft1.mp4`, apply the user's note, render again, cut the fixed moment as `fixed1.mp4`,
and render the final with both clips in the draft panel. Never fake the flaw.

## 6. Package

- Titles: write ten, score them (`/yt-package`), keep three. A number beats an adjective; the thumbnail
  must not repeat the title's words; three words on a thumbnail (five at most).
- Thumbnails: generate with the Codex CLI image model (`codex exec ... < /dev/null`), leave an empty
  corner, then add the presenter with `scripts/thumb_person.sh` at 10-15% of the frame.
- Description + chapters: chapter times = scene starts + cold-open length; first two lines carry the
  search words; the skill + prompt link above the chapters.

Nothing publishes. The user uploads.

## House style (Ainora)

Sora; purples `#655DA9` / `#8D81BD` on lavender; dark pill logo with any text under it in `#655DAA`;
music -24.6 dB under the voice, SFX ~22 dB under and high-passed, no drones/risers/sub hits;
end card with ainora.ai + WhatsApp, no presenter, ~4 s; delivery -14 LUFS / -1.5 dBTP.
