# Ainora YouTube Content Generation Skill

A Claude Code skill that turns **one phone recording + one script** into a finished YouTube video,
with no editor, no timeline and no keyframes. It's the exact workflow behind the Ainora video
**"2 Days of Editing → 1 Hour: See Who Edits My Videos"**.

## The prompt

Put your voice-over recording and your script in a project folder, open Claude Code there, and type:

```
Use Ainora Youtube Content Generation Skill to generate the youtube video with the uploaded Voice over and Script in the project folder
```

## What it does

1. **Transcribes your actual recording** word by word (not the script, since delivery always differs).
2. **Edits the voice:** keeps the last clean take of each line, drops false starts, optionally tightens long pauses, then removes noise and room echo.
3. **Keys you out:** works with a green screen or a plain wall (AI background removal). You get a white outline and move between full screen, side, corner and hidden.
4. **Builds every scene in HyperFrames,** with motion graphics timed to the word you say: mocks, diagrams, code windows, stamps, counters and real screen recordings. It shows what you say instead of repeating it as text.
5. **Mixes** a ducked music bed and quiet sound effects, adds captions and an end card.
6. **Checks its own work** (layout, overlaps, contrast), renders, adds a "Premiere" cold open and delivers at −14 LUFS.
7. **Packages it:** scored titles, Codex-generated thumbnails (presenter at 10–15%), description and chapters.

## Install

```bash
git clone https://github.com/khaleelahmed-zinoji/ainora-youtube-content-skill ~/.claude/skills/ainora-youtube-content-generation
npx hyperframes skills update general-video     # HyperFrames' own skills (by HeyGen)
```

You also need **ffmpeg** and **Node 18+**. Python 3 with `numpy` is needed for the audio mix.
For voice cleaning, set up DeepFilterNet:

```bash
python3 -m venv ~/.cache/dfn-venv && ~/.cache/dfn-venv/bin/pip install deepfilternet torch==2.1.2 torchaudio==2.1.2 soundfile
```

Optional: the [Codex CLI](https://github.com/openai/codex) to generate thumbnails.

## Bring your own

Not included because of licensing. Drop these into each project's `assets/`:
- **Font:** Sora (free, OFL) from [Google Fonts](https://fonts.google.com/specimen/Sora) → `assets/fonts/sora-var.woff2`
- **Music:** two beds you're licensed to use → `assets/music/bright.wav`, `assets/music/calm.wav`
- **Sound effects:** soft clicks/pops/whooshes → `assets/sfx/whoosh-short.mp3`, `heavyclick.mp3`, `pop.mp3`, `tap.mp3`, `quickwhoosh.mp3`
- **Your logo** (the Ainora one is in `brand/` as an example)

## What's inside

```
SKILL.md                    the workflow Claude follows
config.example.json         source, retake ranges, green key, scene phrases, music switch points
templates/project/          make_vo · make_scenes · scenelib · scenes (worked example) · build_index · build_audio
                            timemap (re-recordings) · shared.css · enhance_vo + deroom (voice cleaning)
templates/coldopen/         the "Premiere" cold open composition
scripts/                    clean_vo.sh · coldopen_clip.sh · finish.sh (join + loudness) · thumb_person.sh
brand/                      example logo
```

`templates/project/scenes.py` is the real scene file from the Ainora video, kept as a worked example.
It references media from that project (screen recordings, B-roll), so write your own scenes for your video.

## Made by

[Ainora](https://ainora.ai) builds AI automation for businesses: WhatsApp, CRM and AI workflows.
Want this set up for your team? WhatsApp **0526235035**.

MIT licensed. The Ainora name and logo are not covered by the licence; use your own brand.
