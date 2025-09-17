from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# -----------------------------
# Firebase Initialization
# -----------------------------
cred = credentials.Certificate("serviceAccountKey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# -----------------------------
# Home Page (Frontend)
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -----------------------------
# API Endpoint to Get Sensor Data
# -----------------------------
@app.get("/sensors")
async def get_sensors():
    docs = db.collection("sensors").order_by("timestamp").stream()
    results = []
    for doc in docs:
        d = doc.to_dict()
        d["doc_id"] = doc.id
        if isinstance(d.get("timestamp"), datetime):
            d["timestamp"] = d["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        results.append(d)

    # Debug print to terminal
    print("Fetched Data:", results)

    return JSONResponse(content=results)

