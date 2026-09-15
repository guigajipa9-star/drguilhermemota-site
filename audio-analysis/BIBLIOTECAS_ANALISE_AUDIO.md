# Bibliotecas para Extrair Mais Valor da Reunião (e Futuras)

**Data da análise:** 09/set/2026
**Caso:** reunião com Heloísa sobre sala presencial na Taquara (41 min de áudio)
**Status atual:** transcrição feita com `faster-whisper tiny` em CPU — qualidade ruim

---

## 🎯 O que pode ser extraído além da transcrição pura

### 1. 🗣️ **Speaker Diarization** (quem falou quando)

**O que resolve:** saber se foi Dr. Guilherme ou Heloísa falando em cada trecho. A transcrição atual não tem essa info — está tudo junto, o que dificulta entender o contexto.

**Bibliotecas principais:**

| Biblioteca | Tipo | Qualidade | Velocidade | Custo | Dificuldade |
|---|---|---|---|---|---|
| **pyannote-audio 3.1** | Open-source (Python) | ⭐⭐⭐⭐⭐ | Médio (GPU recomendado) | Grátis | Médio (precisa token HF) |
| **WhisperX** | Open-source | ⭐⭐⭐⭐⭐ | Rápido (otimizado) | Grátis | Médio (precisa token HF) |
| **pyannoteAI API** | Cloud | ⭐⭐⭐⭐⭐ | Lento (upload) | Pago (custo/volume) | Fácil |
| **AssemblyAI** | Cloud | ⭐⭐⭐⭐⭐ | Lento | Pago (~$0.00025/s) | Muito fácil |

**Recomendação:** **pyannote-audio 3.1 + WhisperX** (combinação padrão da indústria em 2026).

**Setup:**
```bash
pip install pyannote.audio whisperx
# Aceitar licença em: huggingface.co/pyannote/speaker-diarization-3.1
# Criar token em: huggingface.co/settings/tokens
export HF_TOKEN="hf_xxxxx"
```

**Aplicação ao nosso áudio:** identificaria "Heloísa falou 18min, Dr. Guilherme falou 23min", além de atribuir cada fala ao speaker correto.

---

### 2. 🔄 **Re-transcrição com modelo maior**

**O que resolve:** a transcrição tiny atual tem MUITOS erros. Um modelo `medium` ou `large-v3` reduziria o WER (Word Error Rate) drasticamente.

| Modelo | Tamanho | Velocidade CPU | Qualidade PT-BR | Quando usar |
|---|---|---|---|---|
| `tiny` | 75MB | 5-10 min para 40 min áudio | ⭐⭐ Ruim | Testes rápidos |
| `base` | 150MB | 15-20 min | ⭐⭐⭐ OK | Quando qualidade mínima serve |
| `small` | 500MB | 30-45 min | ⭐⭐⭐⭐ Bom | Melhor custo/benefício CPU |
| `medium` | 1.5GB | 1-2 horas (CPU) | ⭐⭐⭐⭐⭐ Ótimo | Quando precisa de qualidade |
| `large-v3` | 3GB | 3-4 horas (CPU) | ⭐⭐⭐⭐⭐⭐ Máxima | Produção final |

**Com GPU:** todos esses modelos rodam 5-10× mais rápido.

**Problema atual:** `cublas64_12.dll` ausente impede uso de GPU no seu setup. **Workaround:**
- Habilitar **Developer Mode** no Windows (permite symlinks que CTranslate2 precisa)
- Ou instalar CUDA toolkit manualmente

**Recomendação:** rodar com modelo `medium` em CPU — vai levar ~1-2 horas mas qualidade vai ser suficiente para extrair informações precisas.

---

### 3. 📊 **Análise Acústica**

**O que resolve:** características do áudio que afetam a interpretação.

| Biblioteca | O que extrai |
|---|---|
| **pyAudioAnalysis** | Features (MFCC, spectral), detecção de silêncio, segmentação de speakers |
| **librosa** | Análise espectral, pitch, energia, tempo |
| **pydub** | Detecção de silêncio, chunking, volume |
| **webrtcvad** | Voice Activity Detection (VAD) simples e rápido |

**Aplicação:** medir se a conversa teve muitos silêncios longos (pode indicar hesitação em decisões importantes), distribuição de energia vocal (quem falou mais alto/calmo), pausas significativas.

---

### 4. 🎯 **Extração Estruturada com LLM (Audio-to-LLM)**

**O que resolve:** depois de ter transcrição limpa + diarization, usar LLM para extrair:
- Action items ("Dr. Guilherme vai trazer brinquedos")
- Decisões ("vai começar quarta à tarde")
- Datas, horários, valores mencionados
- Pontos de dúvida ("modelo de cobrança precisa confirmar")
- Perguntas não respondidas
- Tom emocional (positivo/hesitante)

**Ferramentas:**

| Ferramenta | Tipo | Como usar |
|---|---|---|
| **Gladia Audio-to-LLM** | Cloud API | Enviar áudio + prompt, recebe JSON estruturado |
| **AssemblyAI LLM** | Cloud API | Prompt customizado por áudio |
| **Whisper + LLM próprio** | Self-hosted | Transcrever local, enviar texto para LLM (Claude, GPT, local) |

**Pipeline ideal:**
```
áudio M4A
  → WhisperX (transcrição + diarization)  
  → Claude/GPT-4 (extração estruturada com prompt)
  → JSON: { action_items: [...], decisions: [...], open_questions: [...] }
```

**Já temos o último passo:** posso enviar a transcrição atual (mesmo com ruído) para um LLM e pedir para extrair essas coisas. Mas a transcrição atual é tão ruim que o LLM vai alucinar muita coisa.

**Recomendação:** transcrever melhor ANTES de usar LLM para extração.

---

### 5. 🧠 **Análise de Emoção/Sentimento**

**O que resolve:** identificar hesitação, entusiasmo, preocupação, desconforto no tom de voz.

**Bibliotecas:**

| Biblioteca | Modelo | Limitações |
|---|---|---|
| **speech-emotion** (2026 paper) | Multilingual emotion | Funciona com áudios longos (não snippets) |
| **NRClex** | Lexicon-based sentiment | Funciona melhor com texto que áudio |
| **HuggingFace models** | wav2vec2 + classifier | Precisa fine-tuning para PT-BR |

**Aplicação ao nosso caso:** identificar se Heloísa demonstrou entusiasmo ou cautela ao falar do prédio/sala; se você mostrou hesitação em algum momento. Útil mas não crítico.

---

### 6. 📝 **Anotação de Tempo / Estrutura da Conversa**

**O que resolve:** mapear a estrutura da conversa — introdução, negociação, decisões, despedida.

**Ferramentas:**
- **whisperX** já dá timestamps por speaker
- **GPT/Claude** pode segmentar por tópicos a partir do texto

---

## 🚀 Plano de Ação Recomendado

Para extrair o MÁXIMO valor desta reunião específica:

### Passo 1 — Re-transcrever com qualidade (URGENTE)

```bash
# Opção A: modelo medium em CPU (~1-2h, sem GPU)
faster-whisper --model medium --language pt audio.m4a

# Opção B: habilitar Developer Mode + usar GPU (~10 min)
# 1. Configurações → Privacidade e Segurança → Para Desenvolvedores → Modo Desenvolvedor
# 2. Reiniciar PC
# 3. faster-whisper --model large-v3 --language pt --device cuda audio.m4a
```

### Passo 2 — Adicionar Speaker Diarization

```python
import whisperx

model = whisperx.load_model("large-v3", device="cuda")
audio = whisperx.load_audio("audio.m4a")
result = model.transcribe(audio)

# Diarization
diarize_model = whisperx.DiarizationPipeline(
    model_name="pyannote/speaker-diarization-3.1",
    use_auth_token="hf_xxx"
)
diarize_segments = diarize_model(audio)
result = whisperx.assign_speakers(result, diarize_segments)

# result agora tem [SPEAKER_00], [SPEAKER_01] em cada segmento
```

### Passo 3 — Extração Estruturada com LLM

Enviar transcrição limpa para Claude/GPT com prompt:
```
Analise a transcrição abaixo de uma reunião entre Dr. Guilherme Mota 
(psiquiatra) e Heloísa (dona de sala comercial na Taquara/RJ).

Extraia em JSON:
- action_items: lista de compromissos/pendências
- decisions: decisões tomadas
- open_questions: perguntas que ficaram sem resposta
- dates_mentioned: datas, dias da semana, horários citados
- values_mentioned: qualquer valor monetário citado
- concerns: pontos de hesitação ou preocupação de qualquer parte
- next_steps: próximos passos acordados
```

---

## 📦 Stack Completo (para automatizar análises futuras)

Para um pipeline **reutilizável** em todas as suas reuniões:

```bash
# 1. Instalar tudo
pip install faster-whisper whisperx pyannote.audio librosa pydub

# 2. Aceitar licenças
# huggingface.co/pyannote/speaker-diarization-3.1 → "Agree and access"
# huggingface.co/settings/tokens → criar token

# 3. Variáveis de ambiente
export HF_TOKEN="hf_xxxxx"
export HF_HUB_DISABLE_SYMLINKS_WARNING=1

# 4. Script (esboço)
python analyze_meeting.py audio.m4a \
  --model large-v3 \
  --device cuda \
  --output transcript.json \
  --extract-with claude
```

---

## 💡 Recomendação Imediata (esta reunião)

Como você **já tem** uma transcrição (mesmo que ruim), e o objetivo é extrair informação útil:

**Curto prazo (hoje):**
1. ✅ **Salvar transcrição atual** (já feito)
2. ✅ **Análise manual por LLM** (posso fazer agora — enviar a transcrição para Claude com prompt de extração)

**Médio prazo (próxima semana):**
1. ⏳ **Re-transcrever com modelo `medium` em CPU** (1-2 horas unattended)
2. ⏳ **Setup do GPU** (habilitar Developer Mode no Windows + reiniciar)
3. ⏳ **Re-transcrever com `large-v3` em GPU** (~10 min)

**Longo prazo (se virar rotina):**
1. 🔮 **Salvar skill `meeting-analyzer`** com pipeline WhisperX + pyannote + LLM
2. 🔮 **Aplicar em toda reunião futura** (Heloísa, colegas, fornecedores, etc.)

---

## 🔗 Referências

- pyannote-audio: https://github.com/pyannote/pyannote-audio
- WhisperX: https://github.com/m-bain/whisperx
- faster-whisper: https://github.com/SYSTRAN/faster-whisper
- AssemblyAI diarization: https://www.assemblyai.com/blog/top-speaker-diarization-libraries-and-apis
- Gladia Audio-to-LLM: https://docs.gladia.io/chapters/audio-intelligence/audio-to-llm
- speech-emotion (2026 paper): https://www.sciencedirect.com/science/article/pii/S235271102600169X
