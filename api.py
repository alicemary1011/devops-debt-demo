from fastapi import FastAPI
import subprocess
import json
import os

app = FastAPI(title="DevOps Technical Debt Analyzer")


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