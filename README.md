# StepOne AI - Content & Design Engine

AI-powered automated content generation for experiential marketing events.

## Overview

Transform raw event media (50-150 mixed images/videos) into platform-ready marketing assets:

- LinkedIn posts with collages
- Instagram stories and reels
- Case study drafts
- Social media captions

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │         │    Backend      │
│   (React)       │◄────────►│   (FastAPI)     │
│                 │  HTTP   │                 │
│  - Dashboard    │         │  - API Routes   │
│  - Upload      │         │  - Task Queue   │
│  - Sessions    │         │  - File Storage │
│  - Outputs     │         │                 │
└─────────────────┘         └────────┬────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
              ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
              │  MongoDB  │   │   Redis   │   │  AWS S3   │
              │           │   │           │   │           │
              │ Sessions  │   │  Cache    │   │  Files    │
              │ Assets    │   │  Queue    │   │  Media    │
              └───────────┘   └───────────┘   └───────────┘

                    AI Processing Pipeline
                    ──────────────────────
                    1. Object Detection (YOLO)
                    2. Emotion Recognition (FER)
                    3. Image Embeddings (CLIP)
                    4. Content Generation (Gemini/Claude)
                    5. Video Processing (FFmpeg)
```

## Tech Stack

### Backend

- FastAPI - Web framework
- MongoDB - Database
- Redis - Cache and task queue
- Celery - Background tasks
- OpenCV - Image processing
- FFmpeg - Video processing
- YOLO - Object detection
- CLIP - Image embeddings
- Gemini/Claude - AI content generation

### Frontend

- React 19 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- TailwindCSS - Styling
- shadcn/ui - Components

## Project Structure

```
stepone-ai/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── services/     # Business logic
│   │   └── models/       # Data models
│   ├── outputs/          # Generated assets
│   └── event_datasets/   # Input datasets
├── frontend/
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── components/   # Reusable components
│   │   └── lib/          # Utilities
│   └── public/
├── IDEA.md              # Architecture details
├── PRD.md               # Product requirements
└── README.md            # This file
```

## Quick Start

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python -m app.main
```

Backend runs on http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend runs on http://localhost:3000

## Usage

1. Upload event images/videos through the dashboard
2. Select the dataset to process
3. Start the AI processing pipeline
4. Monitor progress in the Sessions view
5. Download generated assets from Outputs

## API Endpoints

- `POST /api/v1/process/{dataset_name}` - Start processing
- `GET /api/v1/sessions` - List all sessions
- `GET /api/v1/sessions/{id}` - Get session details
- `GET /api/v1/sessions/{id}/outputs` - Get generated assets
- `GET /health` - Health check

## Documentation

- [Architecture](IDEA.md) - Detailed system architecture
- [PRD](PRD.md) - Product requirements document

## Team

- Priyansh Narang
- Kaushal Loya
- Shivame Kharat

## License

Proprietary - StepOne AI Buildathon 2026
