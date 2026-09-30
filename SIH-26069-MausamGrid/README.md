# MausamGrid — SIH 26069

National Weather Big Data Analytics Platform prototype for Smart India Hackathon PSID 26069.

## Features
- Live Indian weather telemetry map
- Open-Meteo live weather data
- Weather-event classification using WMO weather codes
- Verification/confidence indicators
- Emergency information dashboard
- FastAPI REST backend
- Leaflet interactive map
- Backend statistics

## Structure
```text
SIH-26069-MausamGrid/
├── frontend/
│   └── index.html
├── backend/
│   ├── main.py
│   └── requirements.txt
├── README.md
└── .gitignore
```

## Run Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend: http://127.0.0.1:8000  
API docs: http://127.0.0.1:8000/docs

## Run Frontend
Open `frontend/index.html` with VS Code Live Server after starting the backend.

## Technologies
HTML, CSS, JavaScript, Tailwind CSS, Leaflet.js, Python, FastAPI, Uvicorn, Pydantic, Requests, Open-Meteo API.

## SIH
Problem Statement ID: 26069
Project: MausamGrid
