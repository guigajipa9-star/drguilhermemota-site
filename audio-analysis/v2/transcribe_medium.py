#!/usr/bin/env python3
"""Re-transcricao com modelo medium em CPU para melhor qualidade."""
from faster_whisper import WhisperModel

audio_path = r"C:\Users\Pichau\Downloads\Heloisa conversa.m4a"
out_dir = r"C:\Users\Pichau\Projects\DrGuilhermeMota-Marketing\audio-analysis\v2"

print("Carregando modelo medium em CPU...", flush=True)
print("(Download ~1.5GB na primeira vez; pode demorar 1-2h para processar 41min de audio)", flush=True)
model = WhisperModel("medium", device="cpu", compute_type="int8")

print("Transcrevendo...", flush=True)
segments, info = model.transcribe(
    audio_path,
    language="pt",
    beam_size=5,
    vad_filter=True,
)

print(f"Idioma: {info.language} | Duracao: {info.duration:.1f}s ({info.duration/60:.1f} min)", flush=True)

txt_path = f"{out_dir}\\heloisa_transcript_medium.txt"
with open(txt_path, "w", encoding="utf-8") as f:
    f.write(f"# Re-transcricao modelo medium (CPU)\n")
    f.write(f"# Idioma: {info.language} | Duracao: {info.duration:.1f}s\n\n")
    n = 0
    for seg in segments:
        n += 1
        line = f"[{seg.start:.1f}s - {seg.end:.1f}s] {seg.text.strip()}\n"
        f.write(line)
        # Mostra progresso a cada 10 segmentos
        if n % 10 == 0:
            print(f"  ... {n} segmentos processados", flush=True)

print(f"\nConcluido: {n} segmentos salvos em {txt_path}", flush=True)
