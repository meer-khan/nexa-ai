from pymongo import MongoClient
from datetime import datetime, timedelta
import random
from decouple import config

# MongoDB connection
client = MongoClient(config("DB_CONN"))
db = client["nexaAi"]

# Collections
violations_collection = db["violations"]
cameras_collection = db["cameras"]

# Define constants
VIOLATION_TYPES = [
    "Running(Pathway)",
    "Running(Staris)",
    "Mobile(Pathway)",
    "Mobile(Stairs)", 
    "Pathway(OffLines)",
    "Railing(Stairs)"
]
LOCATIONS = ["Main Staircase", "Lobby Area", "Emergency Exit", "Corridor A", "Corridor B"]
CAMERA_TYPES = ["entry", "exit", "assembly_line"]
CAMERA_IDS = [f"CAM-{i:03}" for i in range(1, len(LOCATIONS) + 1)]
START_DATE = datetime.now() - timedelta(days=30)

# Helper to generate random timestamps
def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

# Insert camera data
def insert_camera_data():
    cameras = []
    for i, location in enumerate(LOCATIONS):
        cameras.append({
            "cameraId": CAMERA_IDS[i],
            "location": location,
            "cameraType": random.sample(CAMERA_TYPES, k=1 )[0],
        })
    cameras_collection.insert_many(cameras)
    print(f"{len(cameras)} cameras inserted.")

# Insert violation data
def insert_violation_data():
    violations = []
    for _ in range(1000):  # Generate 1000 random violation records
        camera_id = random.choice(CAMERA_IDS)
        violations.append({
            "cameraId": camera_id,
            "violations": random.sample(VIOLATION_TYPES, k=random.randint(1, len(VIOLATION_TYPES))),
            "createdAt": random_date(START_DATE, datetime.now())
        })
    violations_collection.insert_many(violations)
    print(f"{len(violations)} violations inserted.")

# Main function
def main():
    # Clear existing data
    cameras_collection.delete_many({})
    violations_collection.delete_many({})

    # Insert new dummy data
    insert_camera_data()
    insert_violation_data()

    print("Dummy data generation completed.")

if __name__ == "__main__":
    main()
