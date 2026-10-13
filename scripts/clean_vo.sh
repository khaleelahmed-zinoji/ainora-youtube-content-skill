#!/usr/bin/env bash
# clean_vo.sh — run inside the project. assets/vo.wav -> assets/vo-dfn.wav (DeepFilterNet3) -> assets/vo-clean.wav (de-room).
# Removes noise and pulls the room-echo tail down between words. Timing is untouched.
# DFN_PY: a python with deepfilternet installed   (python3 -m venv ~/.cache/dfn-venv && ~/.cache/dfn-venv/bin/pip install deepfilternet torch==2.1.2 torchaudio==2.1.2 soundfile)
# NP_PY:  a python with numpy
set -euo pipefail
DFN_PY="${DFN_PY:-$HOME/.cache/dfn-venv/bin/python}"; NP_PY="${NP_PY:-python3}"
"$DFN_PY" enhance_vo.py | tail -1
"$NP_PY" deroom.py "${1:-16}"
