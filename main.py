from fastapi import FastAPI
from datetime import datetime, timezone
from pymongo import MongoClient
import os

app = FastAPI()
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["switchdb"]
collection = db["switch"]

def ensure_switch(name):
    switch = collection.find_one({"name": name})
    if not switch:
        collection.insert_one({
            "name": name,
            "enabled": False,
            "logs": {"count": 0, "history": []}
        })
    return switch

@app.get("/switch")
def view_switches():
    switches = {}
    for doc in collection.find():
        switches[doc["name"]] = {"enabled": doc["enabled"], "logs": doc["logs"]}
    return switches

@app.post("/switch/{name}/on")
def turn_on(name: str):
    ensure_switch(name)
    collection.update_one({"name": name}, {"$set": {"enabled": True}}, upsert=True)
    return {"switch": name, "enabled": "ON"}

@app.post("/switch/{name}/off")
def turn_off(name: str):
    ensure_switch(name)
    collection.update_one({"name": name}, {"$set": {"enabled": False}}, upsert=True)
    return {"switch": name, "enabled": "OFF"}

@app.post("/switch/{name}/check")
def run_switch(name: str):
    ensure_switch(name)
    switch = collection.find_one({"name": name})
    enabled = switch["enabled"]
    log_entry = {"time": datetime.now(timezone.utc).isoformat(), "enabled": enabled}
    collection.update_one(
        {"name": name},
        {"$inc": {"logs.count": 1}, "$push": {"logs.history": log_entry}}
    )
    return {"enabled": enabled}
