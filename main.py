from fastapi import FastAPI
import json
import os
from datetime import datetime, timezone

app = FastAPI()

FILE = "switches.json"


def load_data():
    if not os.path.exists(FILE):
        return {}
    with open(FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def ensure_switch(name):
    data = load_data()
    if name not in data:
        data[name] = {
            "enabled": False,
            "logs": {
                "count": 0,
                "history": []
            }
        }
        save_data(data)
    return data

@app.get("/switch/{name}/on")
def turn_on(name: str):
    data = ensure_switch(name)
    data[name]["enabled"] = True
    save_data(data)
    return {"switch": name, "status": "ON"}

@app.get("/switch/{name}/off")
def turn_off(name: str):
    data = ensure_switch(name)
    data[name]["enabled"] = False
    save_data(data)
    return {"switch": name, "status": "OFF"}

@app.get("/run/{name}")
def run_switch(name: str):
    data = ensure_switch(name)
    enabled = data[name]["enabled"]
    log_entry = {
        "time": datetime.now(timezone.utc).isoformat(),
        "enabled": enabled
    }
    data[name]["logs"]["count"] += 1
    data[name]["logs"]["history"].append(log_entry)
    save_data(data)
    if not enabled:
        return {"message": f"{name} is OFF"}
    return {"message": f"{name} ran"}