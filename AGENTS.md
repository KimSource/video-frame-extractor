# Repository Guidelines

- This is a Windows Python/Tkinter app. `main.py` is the entry point and uses `ffmpeg\bin\ffmpeg.exe`.
- Use `.venv\Scripts\python.exe` for project Python commands.
- Preserve existing behavior unless a change is requested. Keep changes focused and avoid unrelated cleanup.
- After Python changes, run `.\.venv\Scripts\python.exe -m py_compile main.py`. Smoke-test affected GUI and FFmpeg flows when applicable.
- Discuss new third-party dependencies before adding them.
- Do not commit, push, or rewrite Git history or tags unless explicitly requested. Before committing, follow `docs/agents/git-conventions.md`.
