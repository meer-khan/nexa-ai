import datetime
from typing_extensions import Dict
from db.db_models import create_models
from pymongo.collection import Collection

collections: Dict[str,Collection] = create_models()
# Utility function to get current UTC time
def get_current_time():
    return datetime.datetime.now(datetime.timezone.utc)

# Function to calculate the last 24 hours time range
def get_last_24_hours_range():
    current_time = get_current_time()
    return current_time - datetime.timedelta(hours=24), current_time

# 1. How many people entered the factory in the last 24 hours?
def count_entries_last_24_hours():
    start_time, end_time = get_last_24_hours_range()
    return collections.get("entry_exit_logs").count_documents({"createdAt": {"$gte": start_time, "$lte": end_time}, "type": "entry"})

# 2. How many people exited the factory in the last 24 hours?
def count_exits_last_24_hours():
    start_time, end_time = get_last_24_hours_range()
    return collections.get("entry_exit_logs").count_documents({"createdAt": {"$gte": start_time, "$lte": end_time}, "type": "exit"})

# 3. How many people are currently in the factory?
def count_people_in_factory():
    total_entries = collections.get("entry_exit_logs").count_documents({"type": "entry"})
    total_exits = collections.get("entry_exit_logs").count_documents({"type": "exit"})
    return total_entries - total_exits

# 4. How many known and unknown people are in the factory?
def count_known_unknown_people():
    known_entries = collections.get("entry_exit_logs").count_documents({"type": "entry", "name": {"$ne": None}})
    unknown_entries = collections.get("entry_exit_logs").count_documents({"type": "entry", "name": None})
    total_exits = collections.get("entry_exit_logs").count_documents({"type": "exit"})
    return known_entries - total_exits, unknown_entries - total_exits

# 5. How many people are at a particular location (using camera location)?
def count_people_by_location(location):
    camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"location": location})]
    entries = collections.get("entry_exit_logs").count_documents({"type": "entry", "cameraId": {"$in": camera_ids}})
    exits = collections.get("entry_exit_logs").count_documents({"type": "exit", "cameraId": {"$in": camera_ids}})
    return entries - exits