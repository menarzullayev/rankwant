# Statements read aloud — the voice service (ADR-0064, phase 2)

`server.py` runs **on the host**, with the Navoiy venv (`video-lab/tts/navoiy/.venv`: Python 3.10,
torch 2.3.1+cu121, the RTX 2080 Ti). It loads CosyVoice2-0.5B and the Navoiy checkpoint once and answers
`POST /synthesize {"text": ...}` with MP3 (48 kbit/s, mono). It binds **127.0.0.1:8370** only; the
`tts-worker` container reaches it as `host.docker.internal:8370` (Docker Desktop forwards that to the
host's loopback — measured 2026-11-12), the network does not.

Why not a container: that venv is the one the voice was measured in (RTF 0.84), and a CUDA image with the
CosyVoice stack would add several GB to Docker's disk (`docker_data.vhdx`, 2026-11-11 disk rule).

## Run

```powershell
$env:NAVOIY_ROOT = "D:\Linux\Web_Projects\video-lab\tts\navoiy"
$env:TTS_REFERENCE_WAV = "D:\Linux\Web_Projects\video-lab\tts\benchmark\refs\common.wav"  # FLEURS, CC-BY 4.0
& "D:\Linux\Web_Projects\video-lab\tts\navoiy\.venv\Scripts\python.exe" services\tts\server.py
```

`GET http://127.0.0.1:8370/health` → `{"model": "navoiy-xotirjam-fleurs", "ready": true}` after the model
loads (~30 s). The model name carries the voice (`TTS_VOICE`, default `fleurs`); it must equal the API's
`TTS_MODEL`, or the worker refuses the audio (`model_mismatch`) instead of filing it under the wrong name.

## Turn the voice on

1. Keep the server running (a logon task, like the other host tasks):

   ```powershell
   $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument '-NoProfile -WindowStyle Hidden -Command "$env:NAVOIY_ROOT=''D:\Linux\Web_Projects\video-lab\tts\navoiy''; $env:TTS_REFERENCE_WAV=''D:\Linux\Web_Projects\video-lab\tts\benchmark\refs\common.wav''; & ''D:\Linux\Web_Projects\video-lab\tts\navoiy\.venv\Scripts\python.exe'' ''D:\Linux\Web_Projects\rankwant\services\tts\server.py''"'
   Register-ScheduledTask -TaskName "RankWant Voice" -Action $action -Trigger (New-ScheduledTaskTrigger -AtLogOn) -Settings (New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit 0)
   ```

2. `.env.public`: `TTS_URL=http://host.docker.internal:8370`.
3. `docker compose -p rankwant --env-file .env.public -f docker-compose.yml -f docker-compose.public.yml --profile tts up -d --build api tts-worker`

With `TTS_URL` empty the problem page shows no player (`voice: false` on the problem).

## Measured (2026-11-12, local, the FLEURS voice)

- A+B (301 characters): 17.1 s of synthesis for 20.5 s of audio, 82 KB; the Uzbek Whisper judge
  transcribed the content (its CER counts «10-9» against «o'nning to'qqizinchi darajasi»).
- In the browser, cold: the first sound 8.4 s after «Tinglash»; with the first piece already made, 0.2 s.
  Pieces made while the previous one played: gaps 1.1 s (the one cold transition), 0.1 s, 0 s.
