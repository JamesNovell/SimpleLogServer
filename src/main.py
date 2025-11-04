from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import os
import logging

app = FastAPI()

# Authentication credentials
username = os.getenv('USERNAME', 'default_value')
password = os.getenv('PASSWORD', 'default_value')

# Logging setup
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Create a logs directory if it doesn't exist
log_dir = Path("logs").resolve()
log_dir.mkdir(exist_ok=True)

# Define the log file path
log_file = log_dir / "fetchedlogs.log"

# Shared dictionary
shared_dict = {}

# Data models
class Payload(BaseModel):
    username: str
    message: str

class DictPayload(BaseModel):
    data: dict

class KeyPayload(BaseModel):
    key: str

security = HTTPBasic()

@app.post("/update")
async def replace_dict(payload: DictPayload):
    """
    Endpoint to replace the current dictionary with a new one.
    """
    global shared_dict
    try:
        shared_dict = payload.data
        return {"status": "success", "message": "Dictionary replaced successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to replace dictionary: {e}")

@app.get("/pods")
async def get_dict():
    """
    Endpoint to retrieve the current state of the dictionary.
    """
    return {"status": "success", "data": shared_dict}

@app.post("/api/endpoint")
async def receive_payload(payload: Payload):
    """
    Endpoint to receive JSON data from a client and log it.
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Username: {payload.username}, Message: {payload.message}\n"

        with log_file.open("a") as file:
            file.write(log_entry)

        return {"status": "success", "message": "Payload logged successfully."}
    except Exception as e:
        logger.error(f"Error logging payload: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
async def root():
    return {"message": "FastAPI is running!"}

@app.get("/logs")
async def get_logs(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Endpoint to retrieve the log file with basic authentication.
    """
    if credentials.username != username or credentials.password != password:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not log_file.exists():
        raise HTTPException(status_code=404, detail="Log file not found.")
    return FileResponse(log_file.resolve(), headers={"Content-Disposition": "attachment; filename=fetchedlogs.log"})

@app.post("/get_value")
async def get_value(payload: KeyPayload):
    """
    Endpoint to retrieve an individual value from the shared dictionary using a key.
    """
    try:
        key = payload.key
        if key in shared_dict:
            return {"status": "success", "key": key, "value": shared_dict[key]}
        else:
            raise HTTPException(status_code=404, detail=f"Key '{key}' not found in the dictionary.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve value: {e}")
