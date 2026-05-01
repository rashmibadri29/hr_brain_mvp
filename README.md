# HR Operations Brain MVP

This repository contains the MVP foundation for an HR Operations Brain: a system that turns scattered HR knowledge into approved workflows and AI-ready skill files.

## Phase 1 Status

Implemented foundation:

- Next.js web app shell
- FastAPI backend skeleton
- Core Pydantic schemas for HR workflows, policies, reviews, and skills
- MVP workflow and safety specification
- Initial PostgreSQL schema
- Health and configuration endpoints

## Project Structure

```text
apps/
  api/       FastAPI backend
  web/       Next.js frontend
db/
  schema.sql Initial Postgres schema
docs/
  *.md       Product and implementation plans
```

## Local Development

Create and activate the Conda environment:

```bash
conda env create -f environment.yml
conda activate comp_brain
```

If the environment already exists:

```bash
conda activate comp_brain
pip install -r apps/api/requirements.txt
```

Frontend:

```bash
cd apps/web
npm install
npm run dev
```

Backend:

```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

The web app expects the API at `http://localhost:8000` by default.
