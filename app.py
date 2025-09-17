from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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
    """Return sensor data in JSON format"""
    if db is None:
        return {"error": "Firestore not initialized"}

    try:
        sensors_ref = db.collection("sensors").order_by("timestamp", direction=firestore.Query.DESCENDING)
        docs = sensors_ref.stream()

        sensor_data = []
        for doc in docs:
            sensor_data.append({"id": doc.id, **doc.to_dict()})

        return {"sensors": sensor_data}

    except Exception as e:
        print("🔥 Firestore query failed:", e)
        return {"error": str(e)}


@app.get("/sensors/dashboard")
def dashboard():
    """Return sensor data in a clean HTML table"""
    if db is None:
        return HTMLResponse("<h3>❌ Firestore not initialized</h3>")

    try:
        sensors_ref = db.collection("sensors").order_by("timestamp", direction=firestore.Query.DESCENDING)
        docs = sensors_ref.stream()

        rows = ""
        for doc in docs:
            data = doc.to_dict()
            rows += f"""
            <tr>
                <td>{doc.id}</td>
                <td>{data.get('sensor_id', '')}</td>
                <td>{data.get('temperature', '')} °C</td>
                <td>{data.get('humidity', '')} %</td>
                <td>{data.get('timestamp', '')}</td>
            </tr>
            """

        html = f"""
        <html>
        <head>
            <title>Sensor Data Dashboard</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                }}
                th {{
                    background-color: #4CAF50;
                    color: white;
                }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h2>📊 Sensor Data Dashboard</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Sensor ID</th>
                    <th>Temperature</th>
                    <th>Humidity</th>
                    <th>Timestamp</th>
                </tr>
                {rows}
            </table>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

    except Exception as e:
        return HTMLResponse(f"<h3>🔥 Firestore query failed: {e}</h3>")
