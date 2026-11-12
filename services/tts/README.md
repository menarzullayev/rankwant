# Statements read aloud — the voice service (ADR-0064, phase 2)

`server.py` runs **on the host**, with the Navoiy venv (`video-lab/tts/navoiy/.venv`: Python 3.10,
torch 2.3.1+cu121, the RTX 2080 Ti). It loads CosyVoice2-0.5B and the Navoiy checkpoint once and answers
`POST /synthesize {"text": ...}` with MP3 (48 kbit/s, mono). It binds **127.0.0.1:8370** only; the
`tts-worker` container reaches it as `host.docker.internal:8370` (Docker Desktop forwards that to the
host's loopback — measured 2026-11-12), the network does not.

Why not a container: that venv is the one the voice was measured in (RTF 0.84), and a CUDA image with the
CosyVoice stack would add several GB to Docker's disk (`docker_data.vhdx`, 2026-11-11 disk rule).

## Run

`run.cmd` sets the paths (the Navoiy venv, the FLEURS reference voice — CC-BY 4.0) and starts the server;
its output goes to `.handoff/voice.log` in the main checkout, kept to one 5 MB generation:

```powershell
services\tts\run.cmd
```

`GET http://127.0.0.1:8370/health` → `{"model": "navoiy-xotirjam-fleurs", "ready": true}` after the model
loads (39 s, measured 2026-11-12). The model name carries the voice (`TTS_VOICE`, default `fleurs`); it must
equal the API's `TTS_MODEL`, or the worker refuses the audio (`model_mismatch`) instead of filing it under
the wrong name.

## Turn the voice on

1. Keep the server running — a logon task, like the other host tasks. It runs `run.cmd` from the **deploy
   worktree**, which auto-deploy keeps on `origin/main`; the main checkout may stand on any branch:

   ```powershell
   $action = New-ScheduledTaskAction -Execute "C:\WINDOWS\System32\conhost.exe" -Argument '--headless cmd.exe /c "D:\Windows\project\wt\deploy\services\tts\run.cmd"'
   $user = "$env:USERDOMAIN\$env:USERNAME"
   Register-ScheduledTask -TaskName "RankWant Voice" -Action $action -Trigger (New-ScheduledTaskTrigger -AtLogOn -User $user) -User $user -Settings (New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit 0)
   Start-ScheduledTask -TaskName "RankWant Voice"
   ```

   The trigger names the user: a logon trigger without one is for every user and needs an administrator
   (`Register-ScheduledTask : Access is denied`, measured 2026-11-12); the other host tasks are registered
   the same way.

   The server reads `server.py` once at start: a deploy that changes it takes effect at the next logon, or
   after `Stop-ScheduledTask` / `Start-ScheduledTask`.

   **Memory.** Loading the model needs free commit (RAM + page file) on the host. On 2026-11-12, with
   1.4 GB of RAM and 0.6 GB of commit free (49 `claude` and 118 `node` processes, 29 GB between them), the
   server died while loading, with no traceback: `python.exe` faulted in `c10.dll` (torch), `0xc0000005`, in
   the Application event log. Check `Get-CimInstance Win32_OperatingSystem` → `FreeVirtualMemory` before
   starting it; the same morning, with memory free, it was ready in 39 s.

   Running, it holds **8.3 GB of commit** (3.1 GB working set) and 2.5 GB of GPU memory: starting it took
   the host's free commit from 10.9 to 1.4 GB, and stopping it gave back 8.6 GB (measured 2026-11-12). The
   production stack shares that commit, so the voice stays off until the host has room for it.

   Where it goes (measured step by step, 2026-11-12): importing torch 1.15 GB (its CUDA DLLs), the CUDA
   context 0.3, CosyVoice's imports 0.9, building the models on the CPU before they move to the GPU +3.5,
   the two ONNX sessions (the speech tokenizer runs on the CPU: this onnxruntime has no CUDA provider) ~1.
   After the move only 0.04 GB of CPU tensors are alive; the rest is memory torch's allocator (mimalloc)
   keeps committed, and the GPU memory itself (2.6 GB), which Windows counts as commit under WDDM.
   `MIMALLOC_PURGE_DECOMMITS=1 MIMALLOC_PURGE_DELAY=0` takes the loaded server from 8.9 to 6.7 GB, but the
   first piece brings it back to 8.1 GB in both cases — so allocator settings do not change what it
   needs: about 8 GB while it runs.

2. The env file (`.env.public` in the main checkout): `TTS_URL=http://host.docker.internal:8370`.
3. `docker compose -p rankwant --env-file .env.public -f docker-compose.yml -f docker-compose.public.yml --profile tts up -d --build api tts-worker`

With `TTS_URL` empty the problem page shows no player (`voice: false` on the problem).

`tools/deploy.sh` rebuilds and recreates a **running** `tts-worker` (and `ai-worker`, `video-worker`) with
every API change. They are not in its `SERVICES`, because each runs only once its feature is turned on, and
each builds its own image — without that step a deploy would leave them on the old code.

To turn the voice off: empty `TTS_URL`, `up -d api`, `docker compose … stop tts-worker`, and
`Disable-ScheduledTask -TaskName "RankWant Voice"`. Made pieces stay in S3 under `speech/`.

## Measured (2026-11-12, local, the FLEURS voice)

- A+B (301 characters): 17.1 s of synthesis for 20.5 s of audio, 82 KB; the Uzbek Whisper judge
  transcribed the content (its CER counts «10-9» against «o'nning to'qqizinchi darajasi»).
- In the browser, cold: the first sound 8.4 s after «Tinglash»; with the first piece already made, 0.2 s.
  Pieces made while the previous one played: gaps 1.1 s (the one cold transition), 0.1 s, 0 s.
