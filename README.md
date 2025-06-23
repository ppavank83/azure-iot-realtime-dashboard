#  Azure IoT Realtime Dashboard (Multi-User)

Stream real-time sensor data from mobile devices (e.g., iPhones via Phyphox) to a live web dashboard using Dash, MongoDB (Cosmos DB API), and Azure Functions.

---

## Project Structure

```
azure-iot-realtime/
│
├── dashboard/                # Dash-based live dashboard
│   └── dashboard.py
│
├── ingestion/                #  Azure Function for MongoDB ingestion
│   ├── function_app.py
│   ├── host.json
│   ├── local.settings.json  #  IGNORED IN GIT
│
├── sensors/                  #  Mobile Sensor data streaming scripts
│   └── phone_sensor_data_local.py
│
├── requirements.txt         # Python dependencies
├── .gitignore               # Clean and secure ignore list
└── README.md
```

---

##  How It Works

1. **Sensor App** (Phyphox on iPhone) → Streams data over WiFi
2. **Local Python Script** → Sends data with `userId` to Azure Function
3. **Azure Function** → Writes data to Cosmos DB (MongoDB API)
4. **Dash Web App** → Pulls live data and visualizes:
   - Acceleration (X/Y/Z)
   - Gyroscope (X/Y/Z)
   - 3D phone orientation block (pitch/roll/yaw)
   - GPS location

---

##  Setup

### 1. Clone the Repo
```bash
git clone https://github.com/your-username/azure-iot-realtime.git
cd azure-iot-realtime
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run Azure Function Locally
```bash
cd ingestion
func start
```

### 4. Start Dashboard
```bash
cd dashboard
python dashboard.py
```

### 5. Start Streaming Sensor Data
```bash
cd sensors
python phone_sensor_data_local.py
```

---

## Features

- Multi-user support via `userId`
- Cosmos DB (Mongo API) with partitioning
- 3D orientation visualization
- Live GPS tracking on map
- Real-time acceleration & gyroscope charts

---

## To Do

- [ ] Add dropdown for userId selection in dashboard
- [ ] Deploy Dash app to Azure App Service
- [ ] Optional: Add MQTT/WebSocket support for lower-latency updates

---

## License

MIT License


---

## 🗄️ How to Set Up MongoDB on Azure Cosmos DB

1. **Go to [Azure Portal](https://portal.azure.com/)**
   - Search for **"Cosmos DB"** and click **"Create"**

2. **Choose API**
   - Select **"Azure Cosmos DB for MongoDB"** API

3. **Configure Database**
   - Create a new resource group and name your account (e.g., `iot-cosmos-db-pavan`)
   - Choose a region (e.g., Canada Central)

4. **Create Database + Container**
   - Go to the created Cosmos DB account
   - Click on **"Data Explorer" → "New Database"**
     - Database name: `iot_data`
     - Container name: `sensor_logs`
     - Partition key: `/userId`

5. **Connection String**
   - Under **"Connection String"**, copy the **PRIMARY CONNECTION STRING**
   - Paste it in your `local.settings.json`:
     ```json
     {
       "Values": {
         "MONGO_URI": "<your-connection-string-here>"
       }
     }
     ```

6. **You're Done!**
   - Data sent via the Azure Function will be stored in Cosmos DB under `iot_data.sensor_logs`
   - Use `userId` to query/filter in Dash

