from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import os

app = FastAPI(title="DevOps Technical Debt Analyzer")

# Allow the React dashboard to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "application": "DevOps Technical Debt Analyzer",
        "status": "running"
    }


@app.get("/analyze")
def analyze():
    result = subprocess.run(
        ["python", "analyzer.py"],
        capture_output=True,
        text=True
    )

    report_path = "devops_debt_report.json"

    if not os.path.exists(report_path):
        return {
            "status": "error",
            "message": "Analyzer did not generate a report.",
            "output": result.stdout,
            "error": result.stderr
        }

    with open(report_path, "r") as file:
        report = json.load(file)

    return {
        "status": "success",
        "analysis": report
    }