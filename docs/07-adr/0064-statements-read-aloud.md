# ADR 0064 — Problem statements read aloud

**STATUS:** accepted
**Date:** 2026-11-12
**Approved by:** Saidakbar (owner). Decision record:
[voice statements](../decisions/2026-11-12-voice-statements.md).

**Scope:** `problems` (the spoken text and its endpoint); a speech service and the web player follow in
a second change, under this ADR.

## 1. Context

The 2026-11-10 decision ④ listed «matnni ovoz bilan tinglash» and the owner deferred it: try it with AI
tools and pick the model together, by measurement. On 2026-11-12 he asked for that measurement.

The 2026-10-14 benchmark (`video-lab/tts/benchmark`, 30 sentences, 3 seeds, an Uzbek Whisper judge)
had already ranked the Uzbek voices: Edge/Azure Sardor 2.7 % CER, Madina 3.6 %, Navoiy «xotirjam»
5.0 %, Chatterbox and Anadil 7–9 %, MMS 23.4 %. Its sentences held no formulas, while 1 690 of the
2 336 public statements do. So the new question was how a statement with formulas sounds.

Measured 2026-11-12 on three production statements with the same judge:

| Voice | Formulas as written | Formulas spoken | RTF |
|---|---|---|---|
| Azure Sardor | 22.5 % | 5.9 % | 0.15 (cloud) |
| Azure Madina | 30.2 % | 13.4 % | 0.15 (cloud) |
| Navoiy «xotirjam» | — | 6.0 % | 0.84 (RTX 2080 Ti, 3.4 GB VRAM) |

The browser's own speech has no Uzbek voice (0 of 5 in the tested browser). Turning formulas into words
matters more than which voice reads them.

## 2. Decision

1. **The text.** `problems.speech.spoken()` turns a statement into what the voice reads. Formulas and
   numbers become Uzbek words, and so do ranges (`1 \le n \le 10^5` becomes «en birdan o'nning beshinchi
   darajasigacha»), powers, fractions, sums and `\pmod`. The MathJax delimiters some imports use, and
   their apostrophe spellings (`o\z`, ``yo`l``), are read too. Markdown the ear does not need (images,
   code blocks, tables, links) is silent. It is a pure function: the same statement gives the same text.
   A formula it cannot read, or one too deep to be worth reading, is said as «murakkab formula»; it never
   fails the statement.
   Measured over all 2 336 public statements: 0 failures, 97.0 % with every formula read, and nothing
   unread (backslash, brace, dollar) reaches the voice.
2. **Uzbek only.** The voice reads Uzbek: the author's text when it is Uzbek, else an Uzbek translation
   (ADR-0058). A problem with neither has no speech.
3. **Same visibility.** `GET /problems/<slug>/speech/` uses the detail's own lookup, so a contest problem
   before its start (ADR-0055) has no text here either.
4. **The voice: Navoiy, self-hosted on our GPU** (the owner's choice over Azure Sardor, which measured a
   little better but is a paid external service). CosyVoice2 and the Navoiy weights are Apache-2.0.
   Other models will be tried later.
5. **On demand, then cached** (the owner's choice over pre-generating every statement, about 150 GPU
   hours that a model change would discard). The first listener starts hearing while it is generated
   (RTF 0.84 keeps ahead of playback); the file is kept under `cache_key(model, text)`, so an edited
   statement or another model gets a new file and nothing stale is served.

6. **Phase 2 — built 2026-11-12.** The voice clones the **FLEURS** recording (CC-BY 4.0; the owner's
   choice of 2026-11-12, «keyinchalik vaziyatga qaraymiz»), credited under the player. The model name
   carries the voice (`navoiy-xotirjam-fleurs`), so another voice gets new files.
   - **The service runs on the host**, not in a compose service as first planned: `services/tts/server.py`
     with the Navoiy venv the voice was measured in, bound to 127.0.0.1 and reached by `tts-worker` as
     `host.docker.internal`. A CUDA image with the CosyVoice stack would add several GB to Docker's disk.
   - **Pieces.** `speech.segments()` splits the spoken text into pieces of 120 characters, then growing
     by 15 % up to 400; a short first piece is what the first listener waits for (~8 s), and each next
     piece is made while the one before plays. Each piece is its own file, `speech/<cache_key>.mp3` in
     object storage, served by `/api/v1/speech/<key>.mp3` for a year (`immutable`, at the edge too).
   - `POST /problems/<slug>/speech/generate/` queues the missing pieces on the `tts` queue (one GPU, one
     at a time), each once (a 10-minute claim), throttled per client (`THROTTLE_SPEECH`, 30/hour).
   - **MP3**, not Ogg/Opus: older Safari does not play Ogg.
   - Measured in the browser: the first sound 8.4 s after «Tinglash» cold, 0.2 s once made; gaps between
     pieces 1.1 s (the one cold transition), then 0.1 s and 0 s. The first try packed the title alone
     (18 characters) before a 384-character piece — about 20 s of silence; fixed by filling the first
     piece and growing gently.

## 3. Consequences

- Phase 1: the spoken text and its endpoint. Phase 2 (§ 2.6): the host service, the pieces, the cache
  in object storage and the player.
- The voice is off until the host service runs and `TTS_URL` is set (`services/tts/README.md`); the
  page then shows «Tinglash» on problems with an Uzbek text.
- The GPU is on the production host. Generation competes with nothing there today (judging runs on CPU);
  a busy GPU answers «try later» instead of queueing without bound.
