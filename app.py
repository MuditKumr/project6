from fastapi import FastAPI
from google.cloud import firestore
from google.oauth2 import service_account
import os, json

app = FastAPI()

# --- Firestore Setup ---
# Load service account JSON from Render environment variable
# (set FIREBASE_CREDENTIALS in Render Dashboard → Environment)
creds_dict = json.loads(os.environ["FIREBASE_CREDENTIALS"])
creds = service_account.Credentials.from_service_account_info(creds_dict)

db = firestore.Client(credentials=creds, project=creds.project_id)

# --- Routes ---
@app.get("/")
def root():
    return {"message": "Sensor Data Dashboard API running"}

@app.get("/sensors")
def get_sensors():
    sensors_ref = db.collection("sensors")
    docs = sensors_ref.stream()

    sensor_data = []
    for doc in docs:
        sensor_data.append({"id": doc.id, **doc.to_dict()})

    return {"sensors": sensor_data}
