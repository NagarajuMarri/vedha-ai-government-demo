# Backend

FastAPI skeleton for the Vedha AI Government Demo. It currently provides infrastructure only—no authentication, database tables, AI, uploads, analytics, or learning features.

## Setup

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

Environment variables are documented in `backend/.env.example`. Set them in the shell or through an approved local environment workflow; the application does not automatically read `.env` files and never needs an OpenAI key for this sprint.

## Run the API

```powershell
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Available endpoints:

- API health: `http://127.0.0.1:8000/api/v1/health`
- OpenAPI: `http://127.0.0.1:8000/docs`

## Run tests

```powershell
python -m pytest
```
