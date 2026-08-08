# Vedha AI Platform Web

Versioned React and TypeScript frontend for the unified Vedha AI Learning Platform.

## Current milestone

- Platform gateway for Student, Parent, Teacher and Government experiences
- Functional Student Learning Studio
- English-medium and Telugu-medium lesson setup
- FastAPI lesson integration through `NEXT_PUBLIC_VEDHA_API_BASE_URL`
- Explicit guided-demo fallback when the live backend is unavailable
- Responsive and accessible layout

The existing `frontend/` demo remains intact during controlled migration.

## Local run

```bash
npm install
npm run dev
```

Copy `.env.example` to `.env.local` and set the FastAPI address when needed.

## Deployment

The standalone Next.js output is suitable for container deployment. Azure Container Apps is the recommended commercial deployment target so this frontend and the FastAPI backend can scale independently.
