from datetime import datetime
from pymongo import ASCENDING
from datetime import datetime
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from pymongo.collection import Collection
from typing_extensions import Dict, List
from db.db_models import create_models
import pytz

router = APIRouter(tags=["within-building-emergency"], prefix="/ws/emergency")
collections: Dict[str, Collection] = create_models()


# # Helper function to convert UTC to Pakistan Standard Time (PST)
# def convert_utc_to_pst(utc_time: datetime):
#     pst_timezone = pytz.timezone("Asia/Karachi")  # Pakistan Standard Time
#     return utc_time.astimezone(pst_timezone)


# # Main function to fetch people who entered and not exited, and exclude assembly_line detections
# def fetch_people_entered_but_not_exited():
#     # Get camera IDs for entry, exit, and assembly line types
#     entry_camera_ids = [
#         cam["cameraId"]
#         for cam in collections.get("cameras").find({"cameraType": "entry"},  {"_id": 0})
#     ]
#     exit_camera_ids = [
#         cam["cameraId"]
#         for cam in collections.get("cameras").find({"cameraType": "exit"},  {"_id": 0})
#     ]
#     assembly_line_camera_ids = [
#         cam["cameraId"]
#         for cam in collections.get("cameras").find({"cameraType": "assembly_line"},  {"_id": 0})
#     ]

#     # Step 1: Find all people who entered the building
#     all_entries = list(
#         collections.get("entry_exit_logs")
#         .find({"cameraId": {"$in": entry_camera_ids}},  {"_id": 0})
#         .sort("createdAt", ASCENDING)
#     )

#     # Step 2: Find all people who exited the building
#     all_exits = list(
#         collections.get("entry_exit_logs").find({"cameraId": {"$in": exit_camera_ids}},  {"_id": 0})
#     )

#     # Step 3: Build a set of people who have exited
#     exited_employee_ids = {log["employeeID"] for log in all_exits}

#     # Step 4: Find all people who were detected at assembly_line cameras
#     assembly_line_logs = list(
#         collections.get("entry_exit_logs").find(
#             {"cameraId": {"$in": assembly_line_camera_ids}},  {"_id": 0}
#         )
#     )
#     assembly_line_employee_ids = {log["employeeID"] for log in assembly_line_logs}

#     # Step 5: Filter people who entered and didn't exit
#     people_not_exited = [
#         entry for entry in all_entries if entry["employeeID"] not in exited_employee_ids
#     ]

#     # Step 6: Filter people who didn't exit and weren't detected at assembly line
#     people_not_exited_and_not_assembly_line = [
#         entry
#         for entry in people_not_exited
#         if entry["employeeID"] not in assembly_line_employee_ids
#     ]

#     # Helper function to fetch camera location by cameraID
#     def get_camera_location(camera_id):
#         camera = collections.get("cameras").find_one({"cameraId": camera_id})
#         return camera["location"] if camera else "Unknown Location"

#     # Helper function to process logs and return relevant data
#     def process_logs(logs):
#         processed_logs = []
#         for log in logs:
#             pst_time = convert_utc_to_pst(log["createdAt"])
#             camera_location = get_camera_location(log["cameraId"])
#             processed_logs.append(
#                 {
#                     "name": log.get("name", "Unknown"),
#                     "employeeID": log.get("employeeID", "Unknown"),
#                     "time_in_pst": pst_time.strftime("%Y-%m-%d %H:%M:%S"),
#                     "cameraID": log.get("cameraId", "Unknown"),
#                     "camera_location": camera_location,
#                 }
#             )
#         return processed_logs

#     # Step 7: Process the logs and return results
#     processed_people_not_exited = process_logs(people_not_exited)
#     processed_people_not_exited_and_not_assembly_line = process_logs(
#         people_not_exited_and_not_assembly_line
#     )

#     return {
#         "people_not_exited": processed_people_not_exited,
#         "people_not_exited_and_not_assembly_line": processed_people_not_exited_and_not_assembly_line,
#     }




# Helper function to convert UTC to Pakistan Standard Time (PST)
def convert_utc_to_pst(utc_time: datetime):
    pst_timezone = pytz.timezone("Asia/Karachi")  # Pakistan Standard Time
    return utc_time.astimezone(pst_timezone)

# Main function to fetch people who entered, but not exited, and exclude assembly_line detections
def fetch_people_still_in_factory():
    # Get camera IDs for entry, exit, and assembly line types
    entry_camera_ids = [
        cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "entry"}, {"_id": 0})
    ]
    exit_camera_ids = [
        cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "exit"}, {"_id": 0})
    ]
    assembly_line_camera_ids = [
        cam["cameraId"] for cam in collections.get("cameras").find({"cameraType": "assembly_line"}, {"_id": 0})
    ]

    # Step 1: Find all people who entered the building
    all_entries = list(
        collections.get("entry_exit_logs").find({"cameraId": {"$in": entry_camera_ids}}, {"_id": 0}).sort("createdAt", ASCENDING)
    )

    # Step 2: Find all people who exited the building
    all_exits = list(
        collections.get("entry_exit_logs").find({"cameraId": {"$in": exit_camera_ids}}, {"_id": 0}).sort("createdAt", ASCENDING)
    )

    # Step 3: Build a dictionary of people who have exited, indexed by employeeID
    exited_employee_ids = {log["employeeID"]: log["createdAt"] for log in all_exits}

    # Step 4: Find all people who were detected at assembly_line cameras after they entered
    assembly_line_logs = list(
        collections.get("entry_exit_logs").find({"cameraId": {"$in": assembly_line_camera_ids}}, {"_id": 0}).sort("createdAt", ASCENDING)
    )
    assembly_line_employee_times = {log["employeeID"]: log["createdAt"] for log in assembly_line_logs}

    # Step 5: Filter people who entered and didn't exit or weren't detected at the assembly line
    still_in_factory = []
    for entry in all_entries:
        employee_id = entry["employeeID"]
        entry_time = entry["createdAt"]

        # Check if they exited after entry
        if employee_id in exited_employee_ids and exited_employee_ids[employee_id] > entry_time:
            continue  # Person exited after entering, so skip

        # Check if they were detected at assembly line after entry
        if employee_id in assembly_line_employee_times and assembly_line_employee_times[employee_id] > entry_time:
            continue  # Person detected at assembly line after entry, so skip

        # If they neither exited nor detected at assembly line, add them to the list
        still_in_factory.append(entry)

    # Helper function to fetch camera location by cameraID
    def get_camera_location(camera_id):
        camera = collections.get("cameras").find_one({"cameraId": camera_id})
        return camera["location"] if camera else "Unknown Location"

    # Helper function to process logs and return relevant data
    def process_logs(logs):
        processed_logs = []
        for log in logs:
            pst_time = convert_utc_to_pst(log["createdAt"])
            camera_location = get_camera_location(log["cameraId"])
            processed_logs.append({
                "name": log.get("name", "Unknown"),
                "employeeID": log.get("employeeID", "Unknown"),
                "time_in_pst": pst_time.strftime("%Y-%m-%d %H:%M:%S"),
                "cameraID": log.get("cameraId", "Unknown"),
                "camera_location": camera_location,
            })
        return processed_logs

    # Process the logs and return the final list of people still in the factory
    return process_logs(still_in_factory)



active_connections: List[WebSocket] = []


async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)


async def disconnect(websocket: WebSocket):
    active_connections.remove(websocket)


async def broadcast(message: dict):
    for connection in active_connections:
        await connection.send_json(message)


@router.websocket("/stats")
async def websocket_endpoint(websocket: WebSocket):
    await connect(websocket)
    await broadcast_analysis()
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        await disconnect(websocket)


# Function to broadcast analysis results to connected clients
async def broadcast_analysis():
    message = {
        "employees_in_building": fetch_people_still_in_factory(),
    }

    await broadcast(message)
