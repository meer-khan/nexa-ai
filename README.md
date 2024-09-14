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

## Web Socket: 
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
