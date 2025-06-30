from flask import Flask, jsonify
import pandas as pd
import uuid
import requests
from io import BytesIO
import re

app = Flask(__name__)

SHEET_ID = "1Wrqfp12zqPfdpJWnIEWOsIl4cuFJGEpQokeQjoi9Uv8"
EXCEL_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

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
        # Download Excel file from Google Sheets
        response = requests.get(EXCEL_URL)
        response.raise_for_status()
        # Load workbook from bytes
        xls = pd.ExcelFile(BytesIO(response.content))

        all_events = []
        for sheet_name in xls.sheet_names:
            # Only process sheets whose name is a year (e.g., "1", "2", "3", "4")
            if re.fullmatch(r"\d+", sheet_name.strip()):
                year_of_study = int(sheet_name.strip())
                df = pd.read_excel(xls, sheet_name=sheet_name)
                for _, row in df.iterrows():
                    if pd.isna(row.get("Nume", "")):
                        continue
                    all_events.append({
                        "id": str(uuid.uuid4()),
                        "title": row["Nume"],
                        "location": row["Locatie"],
                        "startTime": f"{int(row['startTime']):02d}:00",
                        "endTime": f"{int(row['endTime']):02d}:00",
                        "day": DAY_MAP.get(str(row["day"]).strip(), 1),
                        "courseType": row["courseType"],
                        "teacher": row["teacher"],
                        "year": year_of_study
                    })
        return jsonify(all_events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

