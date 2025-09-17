from fastapi import FastAPI
from google.cloud import firestore
from google.oauth2 import service_account
import os, json

app = FastAPI()

# --- Firestore Setup ---
try:
    creds_dict = json.loads(os.environ["FIREBASE_CREDENTIALS"])
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    db = firestore.Client(credentials=creds, project=creds.project_id)
except Exception as e:
    print("🔥 Firestore init failed:", e)
    db = None

@app.get("/")
def root():
    return {"message": "Sensor Data Dashboard API running"}

@app.get("/sensors")
def get_sensors():
    if db is None:
        return {"error": "Firestore not initialized"}

    try:
        sensors_ref = db.collection("sensors")
        docs = sensors_ref.stream()

        sensor_data = []
        for doc in docs:
            sensor_data.append({"id": doc.id, **doc.to_dict()})

        return {"sensors": sensor_data}

    except Exception as e:
        print("🔥 Firestore query failed:", e)
        return {"error": str(e)}
