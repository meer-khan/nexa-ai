from pymongo import MongoClient
from pymongo.collection import Collection
from typing_extensions import Dict, Any
from decouple import config


CLIENT = None

def create_models()-> Dict[str, Any]:
    global CLIENT
    try:

        if not CLIENT:
            CLIENT = MongoClient(config("DB_CONN"))

        database_name = "nexaAi"

        # Create or access the specified database
        existing_db = CLIENT[database_name]

        # Insert a document into a collection (this will create the database if it doesn't exist)
        collection_intrusion_detection:Collection = existing_db["intrustionDetection"]
        persion_identification:Collection = existing_db["PersonIdentification"]
        cameras = existing_db["cameras"]
        entry_exit_logs = existing_db["entryExitLogs"]
        employees = existing_db["employees"]
        accounts = existing_db['accounts']

        return  {
            "cid": collection_intrusion_detection,
            "pi":persion_identification,
            "cameras": cameras,
            "entry_exit_logs": entry_exit_logs,
            "employees": employees,
            "accounts": accounts
        }
    except Exception as e:
        print(f"Error: {e}")
