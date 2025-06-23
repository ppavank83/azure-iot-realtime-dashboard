import requests
import time
import json
from datetime import datetime

# 🔹 Prompt for user ID and device IP
user_id = input("Enter your User ID: ").strip()
ip_address = input("Enter your iPhone Phyphox IP (e.g., http://192.168.0.108): ").strip()

# 🔹 Prepare URL
PHYPHOX_URL = ip_address + "/get?"
what_to_get = [
    'acc_time', 'magX', 'magY', 'magZ',
    'accX', 'accY', 'accZ',
    'gyroX', 'gyroY', 'gyroZ',
    'gpsLat', 'gpsLon'
]

# 🔹 Azure Function endpoint (local or cloud)
API_URL = "http://localhost:7071/api/sensor_ingest"

def fetch_and_send_data():
    try:
        # 🔸 Fetch sensor data
        response = requests.get(PHYPHOX_URL + '&'.join(what_to_get))
        data = json.loads(response.text)

        # 🔸 Prepare JSON payload
        payload = {"user": user_id,
                   "timestamp": datetime.utcnow().isoformat()}
        for key in what_to_get:
            value = data['buffer'].get(key, {}).get('buffer', [None])[0]
            payload[key] = value

        print("Sending:", payload)

        # 🔸 Send to Azure Function
        res = requests.post(API_URL, json=payload)
        print("Response:", res.text)

    except Exception as e:
        print(" Error:", e)

# 🔁 Start streaming every second
while True:
    fetch_and_send_data()
    time.sleep(1)
