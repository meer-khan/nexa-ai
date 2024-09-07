import datetime
from typing_extensions import Dict, Literal
from db.db_models import create_models
from pymongo.collection import Collection
from icecream import ic
collections: Dict[str,Collection] = create_models()
# Utility function to get current UTC time
def get_current_time():
    return datetime.datetime.now(datetime.timezone.utc)

# Function to calculate the last 24 hours time range
def get_last_24_hours_range():
    current_time = get_current_time()
    return current_time - datetime.timedelta(hours=24), current_time

# 1. How many people entered the factory in the last 24 hours?
# def count_entries_last_24_hours():
#     start_time, end_time = get_last_24_hours_range()
#     records = collections.get("entry_exit_logs").count_documents({"createdAt": {"$gte": start_time, "$lte": end_time}})
#     ic(records)
#     return records

def count_entries_last_24_hours():
    start_time, end_time = get_last_24_hours_range()
    entry_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "entry"})]
    count_entries_last_24_hours = collections.get("entry_exit_logs").count_documents({
        "createdAt": {"$gte": start_time, "$lte": end_time},
        "cameraId": {"$in": entry_camera_ids}
    })
    ic(count_entries_last_24_hours)
    return count_entries_last_24_hours

# 2. How many people exited the factory in the last 24 hours?
# def count_exits_last_24_hours():
#     start_time, end_time = get_last_24_hours_range()
#     return collections.get("entry_exit_logs").count_documents({"createdAt": {"$gte": start_time, "$lte": end_time}, "type": "exit"})

def count_exits_last_24_hours():
    start_time, end_time = get_last_24_hours_range()
    exit_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "exit"})]
    count_exits_last_24_hours = collections.get("entry_exit_logs").count_documents({
        "createdAt": {"$gte": start_time, "$lte": end_time},
        "cameraId": {"$in": exit_camera_ids}
    })
    ic(count_exits_last_24_hours)
    return count_exits_last_24_hours

# 3. How many people are currently in the factory?
# def count_people_in_factory():
#     total_entries = collections.get("entry_exit_logs").count_documents({"type": "entry"})
#     total_exits = collections.get("entry_exit_logs").count_documents({"type": "exit"})
#     return total_entries - total_exits

def count_people_in_factory():
    entry_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "entry"})]
    exit_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "exit"})]
    
    total_entries = collections.get("entry_exit_logs").count_documents({"cameraId": {"$in": entry_camera_ids}})
    total_exits = collections.get("entry_exit_logs").count_documents({"cameraId": {"$in": exit_camera_ids}})
    ic("count_people_in_factory")
    ic(total_entries - total_exits)
    return total_entries - total_exits

# 4. How many known and unknown people are in the factory?
# def count_known_unknown_people():
#     known_entries = collections.get("entry_exit_logs").count_documents({"type": "entry", "name": {"$ne": None}})
#     unknown_entries = collections.get("entry_exit_logs").count_documents({"type": "entry", "name": None})
#     total_exits = collections.get("entry_exit_logs").count_documents({"type": "exit"})
#     ic()
#     return known_entries - total_exits, unknown_entries - total_exits

def count_known_unknown_people():
    known_entries = collections.get("entry_exit_logs").count_documents({
        "type": "known"
    })
    
    unknown_entries = collections.get("entry_exit_logs").count_documents({
        "type": "unknown"
    })
    
    # total_exits = collections.get("entry_exit_logs").count_documents({"cameraId": {"$in": exit_camera_ids}})
    ic(known_entries, unknown_entries)
    return {"known_entries": known_entries , "unknown_entries":  unknown_entries}

# 5. How many people are at a particular location (using camera location)?
# def count_people_by_location(location):
#     camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"location": location})]
#     entries = collections.get("entry_exit_logs").count_documents({"type": "entry", "cameraId": {"$in": camera_ids}})
#     exits = collections.get("entry_exit_logs").count_documents({"type": "exit", "cameraId": {"$in": camera_ids}})
#     return entries - exits

# def count_people_by_location(location):
#     camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"location": location})]
#     entry_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "entry"})]
#     exit_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "exit"})]
    
#     entries = collections.get("entry_exit_logs").count_documents({"cameraId": {"$in": camera_ids, "$in": entry_camera_ids}})
#     exits = collections.get("entry_exit_logs").count_documents({"cameraId": {"$in": camera_ids, "$in": exit_camera_ids}})
    
#     return entries - exits

def count_people_by_location(location: Literal["entry", "exit", "inside"], start_time, end_time):
    # Get all camera IDs at the specified location
    camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"location": location})]

    # Get entry and exit camera IDs for this location
    # TODO: Need to make it more generic to get all the locations and iterate through it.
    entry_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"location": location, "cameraType": "entry"})]
    exit_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"location": location, "cameraType": "exit"})]
    inside_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"location": location, "cameraType": "inside"})]

    # Count entries within the time range
    total_entries = collections.get("entry_exit_logs").count_documents({
        "cameraId": {"$in": entry_camera_ids + inside_camera_ids},
        "createdAt": {"$gte": start_time, "$lte": end_time}
    })

    # Count exits within the time range
    total_exits = collections.get("entry_exit_logs").count_documents({
        "cameraId": {"$in": exit_camera_ids + inside_camera_ids},
        "createdAt": {"$gte": start_time, "$lte": end_time}
    })

    # Calculate the difference to determine people currently detected at this location
    return total_entries - total_exits

# 6. How many people are ther in factory in last 24 hours
def count_people_in_factory_last_24_hours():
    start_time, end_time = get_last_24_hours_range()

    # Get camera IDs for entry and exit types
    entry_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "entry"})]
    exit_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "exit"})]

    # Count entries in the last 24 hours
    total_entries_last_24_hours = collections.get("entry_exit_logs").count_documents({
        "createdAt": {"$gte": start_time, "$lte": end_time},
        "cameraId": {"$in": entry_camera_ids}
    })

    # Count exits in the last 24 hours
    total_exits_last_24_hours = collections.get("entry_exit_logs").count_documents({
        "createdAt": {"$gte": start_time, "$lte": end_time},
        "cameraId": {"$in": exit_camera_ids}
    })

    # The difference gives the number of people currently in the factory in the last 24 hours
    ic("count_people_in_factory_last_24_hours")
    ic(total_entries_last_24_hours - total_exits_last_24_hours)
    return total_entries_last_24_hours - total_exits_last_24_hours


# 7. Known and unknown entries in last 24 hours

def count_known_unknown_people_last_24_hours():
    start_time, end_time = get_last_24_hours_range()
    known_entries_last_24hrs = collections.get("entry_exit_logs").count_documents({
        "createdAt": {"$gte": start_time, "$lte": end_time},
        "type": "known"
    })
    
    unknown_entries_last_24hrs = collections.get("entry_exit_logs").count_documents({
        "createdAt": {"$gte": start_time, "$lte": end_time},
        "type": "unknown"
    })
    ic(known_entries_last_24hrs, unknown_entries_last_24hrs)
    return {"unknown_entries_last_24hrs": known_entries_last_24hrs , "known_entries_last_24hrs":  unknown_entries_last_24hrs}