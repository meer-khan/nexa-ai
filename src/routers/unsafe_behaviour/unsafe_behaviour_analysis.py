from fastapi import HTTPException, APIRouter
from datetime import datetime, timedelta, timezone
from fastapi.responses import JSONResponse
from pymongo.collection import Collection
from typing_extensions import Dict
from db.db_models import create_models
from utils.time_utilities import convert_utc_to_pst
from icecream import ic
import pprint

router = APIRouter(tags=["unsafe-behaviour"], prefix="/violations")
collections: Dict[str, Collection] = create_models()


@router.get("/trends")
async def get_violation_trends():
    """
    API to fetch trends of violations for the last 24 hours, 7 days, and 30 days.

    :return: JSON response with violation trends for the specified time ranges.
    """
    try:
        now = datetime.now(timezone.utc)
        
        # Define time ranges
        ranges = {
            "last_24_hours": now - timedelta(hours=24),
            "last_7_days": now - timedelta(days=7),
            "last_30_days": now - timedelta(days=30),
        }

        # Initialize result
        trends = {}

        # for label, start_time in ranges.items():
        #     pipeline = [
        #         {"$match": {"createdAt": {"$gte": start_time, "$lte": now}}},
        #         {"$group": {"_id": "$violations", "count": {"$sum": 1}}},
        #         {"$sort": {"count": -1}}
        #     ]
        #     result = list(collections.get("violations").aggregate(pipeline))
        #     pprint.pprint(result)
        #     trends[label] = {
        #         "total_violations": sum(r["count"] for r in result),
        #         "breakdown": {r["_id"]: r["count"] for r in result},
        #     }

        #     pprint.pprint(trends)


        result = {}
        for period, start_time in ranges.items():
            # Query for violations in the given time range
            pipeline = [
                {"$match": {"createdAt": {"$gte": start_time, "$lte": now}}},
                {"$unwind": "$violations"},  # Break down array into individual violations
                {"$group": {"_id": "$violations", "count": {"$sum": 1}}},  # Aggregate counts
                {"$sort": {"count": -1}},
            ]
            violations = list(collections.get("violations").aggregate(pipeline))
            if not violations: 
                return JSONResponse(content={})

            # Reformat data for consistency
            breakdown = {}
            for violation in violations:
                key = (
                    ", ".join(violation["_id"])
                    if isinstance(violation["_id"], list)
                    else violation["_id"]
                )
                breakdown[key] = violation["count"]
            
            result[period] = {
                "total_violations": sum(breakdown.values()),
                "breakdown": breakdown,
            }


        return result


        return JSONResponse(content={"message": "Trends retrieved successfully", "data": trends})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trends: {e}")
    






@router.get("/hotspots")
async def get_violation_hotspots():
    """
    API to identify areas or camera locations with the most frequent violations.

    :return: JSON response with the list of locations and violation counts.
    """
    try:
        # Join the `violations` collection with the `cameras` collection to get locations
        pipeline = [
            {
                "$lookup": {
                    "from": "cameras",  # The collection containing camera details
                    "localField": "cameraId",
                    "foreignField": "cameraId",
                    "as": "camera_details"
                }
            },
            {
                "$unwind": "$camera_details"
            },
            {
                "$group": {
                    "_id": "$camera_details.location",  # Group by location
                    "total_violations": {"$sum": 1},
                    "violation_breakdown": {
                        "$push": {
                            "violation_type": "$violations",
                            "count": {"$sum": 1},
                            "timestamp": "$createdAt"
                        }
                    }
                }
            },
            {"$sort": {"total_violations": -1}},  # Sort by highest violations
        ]

        # Execute the aggregation pipeline
        result = list(collections.get("violations").aggregate(pipeline))
        if not result: 
            return JSONResponse(content={})
        # # Format the response
        # hotspots = [
        #     {
        #         "location": entry["_id"],
        #         "total_violations": entry["total_violations"],
        #         "violation_breakdown": entry["violation_breakdown"],
        #     }
        #     for entry in result
        # ]

        hotspots = []
        for entry in result:
            formatted_breakdown = []
            for violation in entry["violation_breakdown"]:
                pst_timestamp = convert_utc_to_pst(violation["timestamp"])
                formatted_breakdown.append({
                    "violation_type": violation["violation_type"],
                    "timestamp": pst_timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Format PST time
                })
            
            hotspots.append({
                "location": entry["_id"],
                "total_violations": entry["total_violations"],
                "violation_breakdown": formatted_breakdown
            })

        return JSONResponse(content={"message": "Hotspots retrieved successfully", "data": hotspots})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving hotspots: {e}")







@router.get("/distribution")
async def get_violation_distribution():
    """
    API to provide the distribution of behaviors for chart visualization.

    :return: JSON response with violation types and their percentages.
    """
    try:
        # Aggregation pipeline to calculate distribution
        pipeline = [
            {
                "$unwind": "$violations"  # Flatten the array of violations
            },
            {
                "$group": {
                    "_id": "$violations",  # Group by violation type
                    "count": {"$sum": 1}  # Count occurrences of each type
                }
            },
            {
                "$group": {
                    "_id": None,  # Prepare for percentage calculation
                    "total_count": {"$sum": "$count"},
                    "details": {
                        "$push": {
                            "violation_type": "$_id",
                            "count": "$count"
                        }
                    }
                }
            },
            {
                "$unwind": "$details"  # Break down details for percentage calculation
            },
            {
                "$project": {
                    "_id": 0,
                    "violation_type": "$details.violation_type",
                    "count": "$details.count",
                    "percentage": {
                        "$multiply": [
                            {"$divide": ["$details.count", "$total_count"]},
                            100
                        ]
                    }
                }
            },
            {
                "$sort": {"count": -1}  # Sort by count in descending order
            }
        ]

        # Execute the aggregation pipeline
        result = list(collections.get("violations").aggregate(pipeline))

        return JSONResponse(content={"message": "Violation distribution retrieved successfully", "data": result})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving distribution: {e}")
    




@router.get("/frequency-by-interval")
async def get_violation_frequency_by_interval():
    """
    API to fetch non-compliance frequency during specific time intervals.

    :return: JSON response with time intervals and their corresponding violation counts.
    """
    try:
        # Define time intervals (adjust as needed)
        time_intervals = [
            {"label": "Morning", "start": 6, "end": 9},
            {"label": "Midday", "start": 9, "end": 12},
            {"label": "Lunch Break", "start": 12, "end": 14},
            {"label": "Afternoon", "start": 14, "end": 17},
            {"label": "Evening", "start": 17, "end": 21},
            {"label": "Night", "start": 21, "end": 6}
        ]

        # Convert intervals into aggregation stages
        interval_cases = {
            interval["label"]: {
                "$and": [
                    {"$gte": [{"$hour": "$createdAt"}, interval["start"]]},
                    {"$lt": [{"$hour": "$createdAt"}, interval["end"]]}
                ]
            }
            for interval in time_intervals if interval["start"] < interval["end"]
        }

        # Handle night interval separately (spanning two days)
        interval_cases["Night"] = {
            "$or": [
                {"$gte": [{"$hour": "$createdAt"}, 21]},
                {"$lt": [{"$hour": "$createdAt"}, 6]}
            ]
        }

        # MongoDB aggregation pipeline
        pipeline = [
            {
                "$project": {
                    "createdAt": 1,
                    "violations": 1,
                    "interval": {
                        "$switch": {
                            "branches": [
                                {"case": case, "then": label}
                                for label, case in interval_cases.items()
                            ],
                            "default": "Unknown"
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$interval",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}  # Sort intervals by frequency
            }
        ]

        # Execute the pipeline
        result = list(collections.get("violations").aggregate(pipeline))

        # Format the response
        formatted_result = [
            {"time_interval": record["_id"], "violation_count": record["count"]}
            for record in result
        ]

        return JSONResponse(content={
            "message": "Violation frequency by time interval retrieved successfully",
            "data": formatted_result
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving frequency data: {e}")



@router.get("/railing-usage")
async def get_railing_usage_by_location():
    """
    API to fetch railing usage vs. non-usage statistics for each camera location.

    :return: JSON response with camera locations and statistics.
    """
    try:
        # MongoDB aggregation pipeline
        pipeline = [
            # Lookup to join with the cameras collection to get location info
            {
                "$lookup": {
                    "from": "cameras",  # Cameras collection
                    "localField": "cameraId",  # Field in violations
                    "foreignField": "cameraId",  # Field in cameras
                    "as": "camera_details"
                }
            },
            # Unwind the joined array
            {"$unwind": "$camera_details"},
            # Ensure violations field is always an array
            {
                "$project": {
                    "location": "$camera_details.location",
                    "violations": {
                        "$cond": {
                            "if": {"$isArray": "$violations"},
                            "then": "$violations",
                            "else": ["$violations"]
                        }
                    }
                }
            },
            # Group by location and categorize railing usage
            {
                "$group": {
                    "_id": "$location",
                    "railing_usage": {
                        "$sum": {
                            "$cond": [
                                {"$not": {"$in": ["not holding railings", "$violations"]}},
                                1,  # Railing used
                                0   # Railing not used
                            ]
                        }
                    },
                    "non_railing_usage": {
                        "$sum": {
                            "$cond": [
                                {"$in": ["not holding railings", "$violations"]},
                                1,  # Railing not used
                                0   # Railing used
                            ]
                        }
                    }
                }
            },
            # Sort locations by non-railing usage in descending order
            {"$sort": {"non_railing_usage": -1}}
        ]

        # Execute the aggregation pipeline
        result = list(collections.get("violations").aggregate(pipeline))

        # Format the response
        formatted_result = [
            {
                "location": record["_id"],
                "railing_usage": record["railing_usage"],
                "non_railing_usage": record["non_railing_usage"]
            }
            for record in result
        ]

        return JSONResponse(content={
            "message": "Railing usage statistics retrieved successfully",
            "data": formatted_result
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving railing usage data: {e}")
