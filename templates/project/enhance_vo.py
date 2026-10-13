"""enhance_vo.py — de-noise / de-room the VO with DeepFilterNet3 (timing untouched). Run with ~/.cache/dfn-venv/bin/python."""
from df.enhance import enhance, init_df, load_audio, save_audio
model, state, _ = init_df()
audio, _ = load_audio("assets/vo.wav", sr=state.sr())
out = enhance(model, state, audio.mean(0, keepdim=True), atten_lim_db=24)
save_audio("assets/vo-dfn.wav", out, sr=state.sr())
print("done", out.shape, state.sr())
