# Repository Guidelines

- This is a Windows Python/Tkinter app. `main.py` is the entry point and uses `ffmpeg\bin\ffmpeg.exe`.
- Use `.venv\Scripts\python.exe` for project Python commands.
- Run tests with: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`
- The venv may reference a base Python installed outside the repository; this is normal.
- If Python fails to start with an access-denied or sandbox-related error, the tests were not run. Retry the command with elevated execution permission. Do not recreate the venv unless the executable is missing or corrupted.
- Preserve existing behavior unless a change is requested. Keep changes focused and avoid unrelated cleanup.
- After Python changes, run `.\.venv\Scripts\python.exe -m py_compile main.py`. Smoke-test affected GUI and FFmpeg flows when applicable.
- Discuss new third-party dependencies before adding them.
- Do not commit, push, or rewrite Git history or tags unless explicitly requested. Before committing, follow `docs/agents/git-conventions.md`.
