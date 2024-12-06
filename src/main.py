from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import logging

app = FastAPI()

# Logging setup
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Create a logs directory if it doesn't exist
log_dir = Path("logs").resolve()
log_dir.mkdir(exist_ok=True)

# Define the log file path
log_file = log_dir / "fetchedlogs.log"

# Data model for the incoming payload
class Payload(BaseModel):
    username: str
    message: str

security = HTTPBasic()

@app.post("/api/endpoint")
async def receive_payload(payload: Payload):
    """
    Endpoint to receive JSON data from a client and log it.
    """
    try:
        # Prepare the log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Username: {payload.username}, Message: {payload.message}\n"

        # Write the log entry to the file
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
    print(f"Received username: {credentials.username}")
    print(f"Received password: {credentials.password}")
    if credentials.username != "admin" or credentials.password != "anpass4":
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not log_file.exists():
        raise HTTPException(status_code=404, detail="Log file not found.")
    return FileResponse(log_file.resolve(), headers={"Content-Disposition": "attachment; filename=fetchedlogs.log"})

