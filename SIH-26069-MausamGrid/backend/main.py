from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import requests

app = FastAPI(title="National Weather Big Data Analytics Platform - SIH 26069")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class WeatherReport(BaseModel):
    id: int
    source: str
    hashtag: str
    timestamp: datetime
    city: str
    state: str
    lat: float
    lng: float
    event_category: str
    is_verified: bool
    confidence_score: float
    nlp_sentiment: str
    temperature_c: float

class SystemStats(BaseModel):
    total_signals: int
    verified_count: int
    pending_count: int
    avg_confidence: float

CITIES = [
    {"city":"Mumbai","state":"Maharashtra","lat":19.0760,"lng":72.8777},
    {"city":"Delhi","state":"Delhi","lat":28.7041,"lng":77.1025},
    {"city":"Chennai","state":"Tamil Nadu","lat":13.0827,"lng":80.2707},
    {"city":"Kolkata","state":"West Bengal","lat":22.5726,"lng":88.3639},
    {"city":"Jaipur","state":"Rajasthan","lat":26.9124,"lng":75.7873},
    {"city":"Hyderabad","state":"Telangana","lat":17.3850,"lng":78.4867},
    {"city":"Bengaluru","state":"Karnataka","lat":12.9716,"lng":77.5946},
    {"city":"Guwahati","state":"Assam","lat":26.1445,"lng":91.7362},
    {"city":"Srinagar","state":"Jammu & Kashmir","lat":34.0837,"lng":74.7973},
    {"city":"Ahmedabad","state":"Gujarat","lat":23.0225,"lng":72.5714},
]

def categorize_weather(wmo_code: int, temperature: float) -> str:
    if temperature > 40.0: return "Heatwave"
    if wmo_code in [0,1,2,3]: return "Clear/Normal"
    if wmo_code in [45,48]: return "Dense Fog"
    if wmo_code in [51,53,55,56,57]: return "Drizzle"
    if wmo_code in [61,63,65,66,67]: return "Heavy Rainfall"
    if wmo_code in [71,73,75,77]: return "Snowfall / Cold Wave"
    if wmo_code in [80,81,82]: return "Violent Showers / Flooding Risk"
    if wmo_code in [95,96,99]: return "Severe Thunderstorms"
    return "Normal"

@app.get("/")
def root():
    return {"project":"MausamGrid","sih_psid":"26069","status":"online"}

@app.get("/api/reports", response_model=List[WeatherReport])
def get_reports(event_category: Optional[str]=None, is_verified: Optional[bool]=None):
    lats=",".join(str(c["lat"]) for c in CITIES)
    lngs=",".join(str(c["lng"]) for c in CITIES)
    url=f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lngs}&current=temperature_2m,weather_code"
    try:
        response=requests.get(url, timeout=15)
        response.raise_for_status()
        data=response.json()
        live_reports=[]
        for i,city in enumerate(CITIES):
            current=data[i]["current"]
            temp=current["temperature_2m"]
            code=current["weather_code"]
            category=categorize_weather(code,temp)
            verified=category!="Clear/Normal"
            confidence=0.95 if verified else 0.42
            sentiment="Verified Telemetry Match" if verified else "Unconfirmed Anomaly / Low Threat"
            live_reports.append(WeatherReport(
                id=i+1,source="Open-Meteo Live API",
                hashtag="#LiveUpdate" if verified else "#UnverifiedAlert",
                timestamp=datetime.now(),city=city["city"],state=city["state"],
                lat=city["lat"],lng=city["lng"],event_category=category,
                is_verified=verified,confidence_score=confidence,
                nlp_sentiment=sentiment,temperature_c=temp
            ))
        if event_category:
            live_reports=[r for r in live_reports if r.event_category==event_category]
        if is_verified is not None:
            live_reports=[r for r in live_reports if r.is_verified==is_verified]
        return live_reports
    except Exception as e:
        print("Error fetching live data:",e)
        return []

@app.get("/api/stats", response_model=SystemStats)
def get_system_stats():
    reports=get_reports()
    total=len(reports)
    verified=sum(r.is_verified for r in reports)
    pending=total-verified
    avg=sum(r.confidence_score for r in reports)/total if total else 0
    return SystemStats(total_signals=total,verified_count=verified,
                       pending_count=pending,avg_confidence=round(avg*100,1))
