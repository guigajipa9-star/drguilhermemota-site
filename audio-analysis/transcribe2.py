#!/usr/bin/env python3
"""Transcreve audio com faster-whisper usando GPU."""
from faster_whisper import WhisperModel

audio_path = r"C:\Users\Pichau\Downloads\Heloisa conversa.m4a"
output_path = r"C:\Users\Pichau\Projects\DrGuilhermeMota-Marketing\audio-analysis\heloisa_transcript.txt"

print("Carregando modelo tiny...", flush=True)
model = WhisperModel("tiny", device="cpu", compute_type="int8")

print("Transcrevendo audio...", flush=True)
segments, info = model.transcribe(
    audio_path,
    language="pt",
    beam_size=5,
    vad_filter=True,
)

print(f"Idioma: {info.language} | Duracao: {info.duration:.1f}s", flush=True)
print("---", flush=True)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(f"# Transcricao Heloisa conversa\n# Idioma: {info.language} | Duracao: {info.duration:.1f}s\n\n")
    n = 0
    for seg in segments:
        n += 1
        line = f"[{seg.start:.1f}s - {seg.end:.1f}s] {seg.text.strip()}\n"
        f.write(line)
        if n <= 5 or n % 50 == 0:
            print(line.strip()[:120], flush=True)
    print(f"\nTotal: {n} segmentos salvos em {output_path}", flush=True)
