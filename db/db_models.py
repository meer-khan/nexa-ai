from pymongo import MongoClient
from pymongo.collection import Collection
from typing_extensions import Dict, Any
from decouple import config


def create_models()-> Dict[str, Any]:
    try:
        client = MongoClient(config("CONNMONGO"))
        database_name = "nexaAi"

        # Create or access the specified database
        existing_db = client[database_name]

        # Insert a document into a collection (this will create the database if it doesn't exist)
        collection_intrusion_detection:Collection = existing_db["intrustionDetection"]
        persion_identification:Collection = existing_db["PersonIdentification"]
        cameras = existing_db["cameras"]
        entry_exit_logs = existing_db["entryExitLogs"]

        return {
            "cid": collection_intrusion_detection,
            "pi":persion_identification,
            "cameras": cameras,
            "entry_exit_logs": entry_exit_logs

        }
    except Exception as e:
        print(f"Error: {e}")
