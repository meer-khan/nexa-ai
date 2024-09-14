# nexa-ai


#Instructions to run backend

##Navigate to directory "~/Desktop/nexa-ai$" and type command: 

`uvicorn src.app:app --reload`


if some error occurs on database side and get to your linux terminal and type 
`sudo systemctl start mongod`

after start mongodb server check its status 

`sudo systemctl status mongod`

NOTE: Ubuntu shuts down mongodb server automatically after machine shutdown


Hit first command again, backend will start working










Updated: 


# WebSockets: 

## 1- Web Socket: 
  End point: **ws://127.0.0.1:8000/ws/intrusion/stats**

  ### Data Returned: 
  ```json
    {
    "entries_last_24_hours": 7,
    "exits_last_24_hours": 1,
    "people_in_factory": 7,
    "known_unknown_people_in_factory": {
        "known_entries": 0,
        "unknown_entries": 11
    },
    "known_unknown_people_in_factory_last_24_hours": {
        "known_entries_last_24hrs": 0,
        "unknown_entries_last_24hrs": 9
    },
    "people_in_factory_last_24_hours": 6
}
```





## 2- Web Socket: 
  End point: **ws://127.0.0.1:8000/ws/stats/assembly_line_and_24hours_logs**

  ### Data Returned: 
  ```json
{
    "60_minutes_assembly_line_results": {
        "workers_detected_last_60_minutes": [
            {
                "employeeID": "0000",
                "name": "Shahmeer-Khan-assembly_line",
                "timestamp": "2024-09-14 21:33:44"
            }
        ],
        "entries_last_24_hours": [
            {
                "employeeID": "0000",
                "name": "Shahmeer-Khan-gate1",
                "timestamp": "2024-09-14 19:58:29"
            },
            {
                "employeeID": "0000",
                "name": "Shahmeer-Khan-gate1",
                "timestamp": "2024-09-14 21:23:36"
            },
            {
                "employeeID": "0000",
                "name": "Shahmeer-Khan-gate1",
                "timestamp": "2024-09-14 21:24:48"
            },
            {
                "employeeID": "0000",
                "name": "Shahmeer-Khan-gate1",
                "timestamp": "2024-09-14 21:25:49"
            },
            {
                "employeeID": "0000",
                "name": "Shahmeer-Khan-gate1",
                "timestamp": "2024-09-14 21:27:45"
            },
            {
                "employeeID": "0000",
                "name": "Shahmeer-Khan-gate1",
                "timestamp": "2024-09-14 21:30:38"
            },
            {
                "employeeID": "0000",
                "name": "Shahmeer-Khan-gate1",
                "timestamp": "2024-09-14 21:32:49"
            }
        ],
        "exits_last_24_hours": [
            {
                "employeeID": "0000",
                "name": "Shahmeer-Khan-assembly_line",
                "timestamp": "2024-09-14 21:45:38"
            }
        ],
        "assembly_line_logs_last_24_hours": [
            {
                "employeeID": "0000",
                "name": "Shahmeer-Khan-assembly_line",
                "timestamp": "2024-09-14 21:33:44"
            }
        ]
    }
}
```





## 1- Web Socket: 
  End point: ws://127.0.0.1:8000/ws/intrusion/stats

  ### Data Returned: 
  ```json
    {
    "entries_last_24_hours": 7,
    "exits_last_24_hours": 1,
    "people_in_factory": 7,
    "known_unknown_people_in_factory": {
        "known_entries": 0,
        "unknown_entries": 11
    },
    "known_unknown_people_in_factory_last_24_hours": {
        "known_entries_last_24hrs": 0,
        "unknown_entries_last_24hrs": 9
    },
    "people_in_factory_last_24_hours": 6
}
```






## 1- Web Socket: 
  End point: ws://127.0.0.1:8000/ws/intrusion/stats

  ### Data Returned: 
  ```json
    {
    "entries_last_24_hours": 7,
    "exits_last_24_hours": 1,
    "people_in_factory": 7,
    "known_unknown_people_in_factory": {
        "known_entries": 0,
        "unknown_entries": 11
    },
    "known_unknown_people_in_factory_last_24_hours": {
        "known_entries_last_24hrs": 0,
        "unknown_entries_last_24hrs": 9
    },
    "people_in_factory_last_24_hours": 6
}
```
