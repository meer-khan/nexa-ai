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




# HTTP BASED APIs

## API - 1
  END POINT: **http://127.0.0.1:8000/stats/time-range-stats/**

  ### Body Data:
  ```json
{
  "start_time": "2024-09-13T06:02:00",
  "end_time": "2024-09-13T06:35:00"
}
```
  
  ### Data Returned: 
  ```json
{
    "details": {
        "people_still_in_factory": [],
        "workers_on_assembly_line": [
            {
                "name": "Shahmeer-Khan-assembly-line",
                "cameraId": "1",
                "employeeID": "0000",
                "type": "unknown"
            }
        ]
    }
}
```   



## API-2

END POINT: **http://127.0.0.1:8000/employees/register**

Form Data: 
``` json
name: Shahmeer Khan (Text)
employeeID : 0000 (Text)

```

### Data Returned: 
```json
{
    "details": "Employee Added Successfully. ID: 1111"
}
```



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
  End point: **ws://127.0.0.1:8000/ws/stats/assembly-line-and-24hours-logs**

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





## 3- Web Socket: 
  End point: **ws://127.0.0.1:8000/ws/todays-visits/all**

  ### Data Returned: 
  ```json
   {
    "todays_visits": {
        "entry_logs": [
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 19:58:29",
                "cameraID": "2",
                "camera_location": "gate-1"
            },
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:23:36",
                "cameraID": "2",
                "camera_location": "gate-1"
            },
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:24:48",
                "cameraID": "2",
                "camera_location": "gate-1"
            },
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:25:49",
                "cameraID": "2",
                "camera_location": "gate-1"
            },
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:27:45",
                "cameraID": "2",
                "camera_location": "gate-1"
            },
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:30:38",
                "cameraID": "2",
                "camera_location": "gate-1"
            },
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:32:49",
                "cameraID": "2",
                "camera_location": "gate-1"
            }
        ],
        "exit_logs": [
            {
                "name": "Shahmeer-Khan-assembly_line",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:45:38",
                "cameraID": "3",
                "camera_location": "gate-2"
            }
        ],
        "assembly_line_logs": [
            {
                "name": "Shahmeer-Khan-assembly_line",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:33:44",
                "cameraID": "1",
                "camera_location": "assembly_line_1"
            }
        ]
    }
}
```






## 4- Web Socket: 
  End point: **ws://127.0.0.1:8000/ws/emergency/stats**

  ### Data Returned: 
  ```json
   {
    "todays_visits": {
        "people_not_exited": [
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-13 01:02:50",
                "cameraID": "2",
                "camera_location": "gate-1"
            },
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 19:58:29",
                "cameraID": "2",
                "camera_location": "gate-1"
            },
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:23:36",
                "cameraID": "2",
                "camera_location": "gate-1"
            },
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:24:48",
                "cameraID": "2",
                "camera_location": "gate-1"
            },
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:25:49",
                "cameraID": "2",
                "camera_location": "gate-1"
            },
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:27:45",
                "cameraID": "2",
                "camera_location": "gate-1"
            },
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:30:38",
                "cameraID": "2",
                "camera_location": "gate-1"
            },
            {
                "name": "Shahmeer-Khan-gate1",
                "employeeID": "0000",
                "time_in_pst": "2024-09-14 21:32:49",
                "cameraID": "2",
                "camera_location": "gate-1"
            }
        ],
        "people_not_exited_and_not_assembly_line": []
    }
}
```
