# Frontend

Static HTML, CSS, and vanilla JavaScript interfaces for the Vedha AI Government Demo. Sprint 3C connects the Student Tutor to the controlled lesson API.

From the repository root, run a local static server:

```powershell
python -m http.server 8080 --bind 127.0.0.1 --directory frontend
```

Open `http://127.0.0.1:8080/`. The four navigation cards lead to separate Student, Teacher, Parent, and Government interface shells.

Start the FastAPI backend first at `http://127.0.0.1:8000`. The Student Tutor uses that URL by default. A development host may set `window.VEDHA_API_BASE_URL` before the API client loads to use another backend URL; it must not contain secrets.

The tutor currently supports structured text lessons through deterministic fallback responses. Voice, attachments, conversation history, persistence, and live-provider configuration remain out of scope.
