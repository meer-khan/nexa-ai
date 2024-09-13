import datetime
from typing_extensions import Dict, Literal
from db.db_models import create_models
from pymongo.collection import Collection
from icecream import ic
import pytz
collections: Dict[str,Collection] = create_models()
# Utility function to get current UTC time
def get_current_time():
    return datetime.datetime.now(datetime.timezone.utc)

# Function to calculate the last 24 hours time range
def get_last_24_hours_range():
    current_time = get_current_time()
    return current_time - datetime.timedelta(hours=24), current_time


def count_entries_last_24_hours():
    start_time, end_time = get_last_24_hours_range()
    entry_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "entry"})]
    count_entries_last_24_hours = collections.get("entry_exit_logs").count_documents({
        "createdAt": {"$gte": start_time, "$lte": end_time},
        "cameraId": {"$in": entry_camera_ids}
    })
    ic(count_entries_last_24_hours)
    return count_entries_last_24_hours

def count_exits_last_24_hours():
    start_time, end_time = get_last_24_hours_range()
    exit_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "exit"})]
    count_exits_last_24_hours = collections.get("entry_exit_logs").count_documents({
        "createdAt": {"$gte": start_time, "$lte": end_time},
        "cameraId": {"$in": exit_camera_ids}
    })
    ic(count_exits_last_24_hours)
    return count_exits_last_24_hours

def count_people_in_factory():
    entry_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "entry"})]
    exit_camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "exit"})]

    # Count the total number of entries recorded by entry cameras
    total_entries = collections.get("entry_exit_logs").count_documents({"cameraId": {"$in": entry_camera_ids}})
    
    # Count the total number of exits recorded by exit cameras
    total_exits = collections.get("entry_exit_logs").count_documents({"cameraId": {"$in": exit_camera_ids}})
    # Make sure to avoid negative counts
    people_in_factory = total_entries - total_exits

    if people_in_factory < 0:
        ic("Warning: Negative people count detected. Please check the logs and data consistency.")
        people_in_factory = 0  # Set to 0 to avoid negative results
    
    return people_in_factory

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
# Utility function to count people by location within the specified time range
# def count_people_by_location(location, start_time_utc: datetime, end_time_utc: datetime):
#     # Find all cameras at the specified location
#     camera_ids = [cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": location})]
    
#     # Count entries for those cameras within the specified time range
#     entries = collections.get("entry_exit_logs").count_documents({
#         "cameraId": {"$in": camera_ids},
#         "createdAt": {"$gte": start_time_utc, "$lte": end_time_utc}
#     })
    
#     return entries



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

    # Calculate the number of people in the factory in the last 24 hours
    people_in_factory_last_24_hours = total_entries_last_24_hours - total_exits_last_24_hours
    ic(people_in_factory_last_24_hours)
    # Ensure that the count is not negative
    if people_in_factory_last_24_hours < 0:
        ic("Warning: Negative people count detected. Adjusting to 0.")
        people_in_factory_last_24_hours = 0  # Set to 0 to avoid negative results

    return people_in_factory_last_24_hours

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
    return {"known_entries_last_24hrs": known_entries_last_24hrs , "unknown_entries_last_24hrs":  unknown_entries_last_24hrs}