from flask import Flask, jsonify
import pandas as pd
import uuid
import requests
from io import BytesIO

app = Flask(__name__)

# Google Sheets configuration
SHEET_ID = "1Wrqfp12zqPfdpJWnIEWOsIl4cuFJGEpQokeQjoi9Uv8"
SHEET_NAME = "Automatica"  # Name of the sheet tab
EXPORT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# Map day names to numbers
DAY_MAP = {
    "Luni": 1, "Monday": 1,
    "Marti": 2, "Tuesday": 2,
    "Miercuri": 3, "Wednesday": 3,
    "Joi": 4, "Thursday": 4,
    "Vineri": 5, "Friday": 5,
    "Sambata": 6, "Saturday": 6,
    "Duminica": 7, "Sunday": 7
}

@app.route("/timetable", methods=["GET"])
def get_timetable():
    try:
        # Download CSV data from Google Sheets
        response = requests.get(EXPORT_URL)
        response.raise_for_status()  # Check for HTTP errors
        
        # Read CSV data into DataFrame
        df = pd.read_csv(BytesIO(response.content))
        
        # Process data
        timetable_data = []
        for _, row in df.iterrows():
            if pd.isna(row.get("Nume", "")):
                continue
                
            timetable_data.append({
                "id": str(uuid.uuid4()),
                "title": row["Nume"],
                "location": row["Locatie"],
                "startTime": f"{int(row['startTime'])}:00",
                "endTime": f"{int(row['endTime'])}:00",
                "day": DAY_MAP.get(str(row["day"]).strip(), 1),
                "courseType": row["courseType"],
                "teacher": row["teacher"],
            })
            
        return jsonify(timetable_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
