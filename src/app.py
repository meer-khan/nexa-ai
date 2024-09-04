from fastapi import FastAPI
from icecream import ic
import sys 
import pathlib
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from src.routers import intrusion_detection, person_identification, people_enter_exit
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "http://localhost:3000",  
    "http://localhost:3001", # React development server# Production React app
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
