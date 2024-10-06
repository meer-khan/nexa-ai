import requests
import json
# data = {"intrustionClass": "HOMOSAPIENS", "cameraId":"123"}
# json_data = json.dumps(data)
# response = requests.post("http://127.0.0.1:8000/intrusion-detection/activity-detected", json=data)
# print(response.text)




data = {
    "cameraId" : "2",
    "name" : "Shahmeer",
    "type" : "unknown",
    "employeeID": "0000"
}
url = "http://127.0.0.1:8000/cameras/log-event"

for i in range(0,100):
  response = requests.post(url=url, json=data)
# print(response.text)