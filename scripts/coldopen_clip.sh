#!/usr/bin/env bash
# coldopen_clip.sh <body.mp4> <start_s> <end_s> [speed]
# Cuts the showcase moment from the rendered body and speeds it up (default 1.3x, pitch-preserved) into
# coldopen/assets/clip.mp4 + clip.wav. Pick start/end inside silences (check the transcript gaps).
set -euo pipefail
B="$1"; A="$2"; E="$3"; S="${4:-1.3}"
mkdir -p coldopen/assets
ffmpeg -v error -y -ss "$A" -to "$E" -i "$B" -filter_complex "[0:v]setpts=(PTS-STARTPTS)/$S,fps=30[v];[0:a]asetpts=PTS-STARTPTS,atempo=$S,afade=t=in:d=0.02[a]" \
  -map "[v]" -an -c:v libx264 -crf 16 -g 15 -pix_fmt yuv420p coldopen/assets/clip.mp4 -map "[a]" -c:a pcm_s16le -ar 48000 coldopen/assets/clip.wav
ffprobe -v error -show_entries format=duration -of csv=p=0 coldopen/assets/clip.mp4
