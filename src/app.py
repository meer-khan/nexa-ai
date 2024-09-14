from fastapi import FastAPI
from icecream import ic
import sys
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from src.routers import (
    intrusion_detection,
    person_identification,
    people_enter_exit,
    time_range_stats,
    intrusion_stats_ws,
    employees,
    last_hour_assembly_line_stats,
    todays_visits,
    within_building
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "http://localhost:3000",
    "http://localhost:3001",  # React development server# Production React app
]

# Add CORS middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(intrusion_detection.router)
app.include_router(person_identification.router)
app.include_router(people_enter_exit.router)
app.include_router(time_range_stats.router)
app.include_router(intrusion_stats_ws.router)
app.include_router(employees.router)
app.include_router(last_hour_assembly_line_stats.router)
app.include_router(todays_visits.router)
app.include_router(within_building.router)

