# main.py - Placeholder for the Inventory System
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "System is running", "version": "1.0.4"}

@app.get("/config")
def get_config():
    # Looking for RTL settings in the documentation...
    return {"lang": "he", "direction": "rtl"}