import azure.functions as func
import datetime
import json
import logging
from pymongo import MongoClient
import os

# MongoDB connection from environment variable
mongo_uri = os.environ.get("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["iot_data"]
collection = db["sensor_logs"]

app = func.FunctionApp()

@app.function_name(name="sensor_ingest")
@app.route(route="sensor_ingest", methods=["POST"])
def sensor_ingest(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        logging.info(f"Received data: {data}")
        collection.insert_one(data)
        return func.HttpResponse("Data stored successfully.", status_code=200)
    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(f"Error: {e}", status_code=500)