#!/usr/bin/env bash
# finish.sh <coldopen.mp4> <body.mp4> <out.mp4>
# Joins the cold open to the body, then two-pass loudnorm to -14 LUFS / -1.5 dBTP (YouTube) with a true-peak limiter.
set -euo pipefail
C="$1"; B="$2"; OUT="$3"; T=$(mktemp -d)
CD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$C")
ffmpeg -v error -y -i "$C" -i "$B" -filter_complex "[0:v]fps=30,setpts=PTS-STARTPTS[a0];[0:a]aresample=48000,asetpts=PTS-STARTPTS,afade=t=out:st=$(python3 -c "print($CD-0.05)"):d=0.04[b0];[1:v]fps=30,setpts=PTS-STARTPTS[a1];[1:a]aresample=48000,asetpts=PTS-STARTPTS[b1];[a0][b0][a1][b1]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a pcm_s16le "$T/joined.mov"
M=$(ffmpeg -hide_banner -i "$T/joined.mov" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | grep -A12 '^{')
g(){ echo "$M" | grep "\"$1\"" | grep -oE '[-0-9.]+' | head -1; }
ffmpeg -v error -y -i "$T/joined.mov" -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset),aresample=192000,alimiter=limit=0.8:level=false,aresample=48000" \
  -c:a aac -b:a 192k -movflags +faststart "$OUT"
ffmpeg -nostats -i "$OUT" -af loudnorm=print_format=summary -f null - 2>&1 | grep -E "Input Integrated|Input True Peak"
