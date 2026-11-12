@echo off
rem The voice service (ADR-0064) with the Navoiy venv. The "RankWant Voice"
rem logon task runs this file from the deploy worktree, which auto-deploy keeps
rem on origin/main; the log goes next to the auto-deploy log.
if not defined NAVOIY_ROOT set "NAVOIY_ROOT=D:\Linux\Web_Projects\video-lab\tts\navoiy"
if not defined TTS_REFERENCE_WAV set "TTS_REFERENCE_WAV=D:\Linux\Web_Projects\video-lab\tts\benchmark\refs\common.wav"
if not defined TTS_LOG set "TTS_LOG=D:\Linux\Web_Projects\rankwant\.handoff\voice.log"
rem One request is one log line; keep a single 5 MB generation.
for %%F in ("%TTS_LOG%") do if %%~zF GTR 5242880 move /y "%TTS_LOG%" "%TTS_LOG%.1" >nul
rem supervisor.py listens on 8370 and loads server.py only while the voice is used.
"%NAVOIY_ROOT%\.venv\Scripts\python.exe" -u "%~dp0supervisor.py" >> "%TTS_LOG%" 2>&1
