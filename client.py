# import requests
# import json
# data = {"intrustionClass": "HOMOSAPIENS", "cameraId":"123"}
# json_data = json.dumps(data)
# response = requests.post("http://127.0.0.1:8000/intrusion-detection/activity-detected", json=data)
# print(response.text)


# Initial values
initial_investment = 1000000  # PKR
monthly_profit_rate = 0.04  # 10% profit rate per month
months = 10 * 12  # 20 years in months

# Calculate compound profit
total_amount = initial_investment
for _ in range(months):
    total_amount += total_amount * monthly_profit_rate

print(total_amount)


# data = {
#     "cameraId" : "2",
#     "name" : "Shahmeer",
#     "type" : "unknown",
#     "employeeID": "0000"
# }
# url = "http://127.0.0.1:8000/cameras/log-event"

# for i in range(0,100):
#   response = requests.post(url=url, json=data)
# print(response.text)