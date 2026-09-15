#!/usr/bin/env python3
"""Transcreve audio com faster-whisper usando GPU."""
import sys
from faster_whisper import WhisperModel

audio_path = r"C:\Users\Pichau\Downloads\Heloisa conversa.m4a"
output_path = r"C:\Users\Pichau\Projects\DrGuilhermeMota-Marketing\audio-analysis\heloisa_transcript.txt"

# Modelo tiny em GPU, float16 = rapido
print("Carregando modelo...", flush=True)
model = WhisperModel("tiny", device="cuda", compute_type="float16")

print("Transcrevendo audio...", flush=True)
segments, info = model.transcribe(
    audio_path,
    language="pt",
    beam_size=5,
    vad_filter=True,
)

print(f"Idioma detectado: {info.language} (probabilidade {info.language_probability:.2f})", flush=True)
print(f"Duracao: {info.duration:.1f}s", flush=True)
print("---", flush=True)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(f"# Transcricao - {audio_path}\n")
    f.write(f"# Idioma: {info.language} | Duracao: {info.duration:.1f}s\n\n")
    for seg in segments:
        line = f"[{seg.start:.1f}s - {seg.end:.1f}s] {seg.text.strip()}\n"
        f.write(line)
        print(line.strip(), flush=True)

print(f"\nSalvo em: {output_path}", flush=True)
