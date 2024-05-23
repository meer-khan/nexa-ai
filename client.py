import requests
import json
# data = {"intrustionClass": "HOMOSAPIENS", "cameraId":"123"}
# json_data = json.dumps(data)
# response = requests.post("http://127.0.0.1:8000/intrusion-detection/activity-detected", json=data)
# print(response.text)




data = {
  "personId": "00998877",
  "personName": "Shahmeer",
  "location": "COVE i10/3"
}
url = "http://127.0.0.1:8000/person-detection/person"

response = requests.post(url=url, json=data)
print(response.text)