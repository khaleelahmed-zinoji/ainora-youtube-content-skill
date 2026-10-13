#!/usr/bin/env bash
# thumb_person.sh <thumb.png> <person_cutout.png> <out.jpg> [size_px=340] [x=-42] [y=330] [crop=W:H:X:Y]
# Puts the presenter cutout (npx hyperframes remove-background photo.jpg -o cut.png) on a 1280x720 thumbnail
# with the house white outline + soft purple glow. 340px square = 12.5% of the frame (keep it 10-15%).
set -euo pipefail
BG="$1"; P="$2"; OUT="$3"; S="${4:-340}"; X="${5:--42}"; Y="${6:-330}"; CROP="${7:-iw:ih:0:0}"; Q=$((S+100))
ffmpeg -v error -y -i "$BG" -i "$P" -filter_complex "[0]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720[bg];[1]crop=$CROP,scale=$S:$S:force_original_aspect_ratio=decrease:flags=lanczos,format=rgba,pad=$Q:$Q:50:50:color=black@0,split=3[p][a1][a2];[a1]alphaextract,dilation,dilation,dilation,dilation,gblur=sigma=0.8[mo];color=c=white:s=${Q}x${Q},format=rgba[w];[w][mo]alphamerge[ol];[a2]alphaextract,dilation,dilation,dilation,dilation,dilation,dilation,gblur=sigma=12[g];color=c=0x8D81BD:s=${Q}x${Q},format=rgba[gc];[gc][g]alphamerge,colorchannelmixer=aa=0.8[glow];[glow][ol]overlay=format=auto[o2];[o2][p]overlay=format=auto[person];[bg][person]overlay=x=$X:y=$Y:format=auto" -frames:v 1 -q:v 2 "$OUT"
