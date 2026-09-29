import subprocess
import json
from pathlib import Path


PROJECT_PATH = Path(".").resolve()
REPORT_FILE = PROJECT_PATH / "devops_debt_report.json"


def run_command(command):
    """Run a shell command and return its output."""
    result = subprocess.run(
        command,
        cwd=PROJECT_PATH,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"Command failed: {' '.join(command)}")

    return result.stdout


def get_commits():
    """Get commits in chronological order."""
    output = run_command(
        ["git", "log", "--oneline", "--reverse"]
    )

    commits = []

    for line in output.strip().splitlines():
        if not line.strip():
            continue

        commit_hash, message = line.split(" ", 1)

        commits.append({
            "hash": commit_hash,
            "message": message
        })

    return commits


def analyze_commit(commit_hash):
    """Checkout a commit and run the debt analyzer."""
    print()
    print("=" * 60)
    print(f"Analyzing commit: {commit_hash}")
    print("=" * 60)

    run_command(["git", "checkout", "--quiet", commit_hash])

    # Remove an old report so that stale data cannot be used.
    if REPORT_FILE.exists():
        REPORT_FILE.unlink()

    run_command(["python", "analyzer.py"])

    if not REPORT_FILE.exists():
        raise RuntimeError(
            "Analyzer did not generate devops_debt_report.json"
        )

    with open(REPORT_FILE, "r", encoding="utf-8") as file:
        report = json.load(file)

    return report


def restore_original_branch():
    """Return to the branch that was active before analysis."""
    branch = run_command(
        ["git", "branch", "--show-current"]
    ).strip()

    return branch


def main():
    print("=" * 60)
    print("DEVOPS TECHNICAL DEBT HISTORY ANALYZER")
    print("=" * 60)

    original_branch = restore_original_branch()

    if not original_branch:
        raise RuntimeError(
            "Could not determine the current Git branch."
        )

    print(f"\nOriginal branch: {original_branch}")

    commits = get_commits()

    if not commits:
        print("No Git commits found.")
        return

    print(f"Commits found: {len(commits)}")

    history = []

    try:
        for commit in commits:
            report = analyze_commit(commit["hash"])

            summary = report.get("summary", {})

            history_entry = {
                "commit": commit["hash"],
                "message": commit["message"],
                "total_findings": summary.get("total_findings", 0),
                "severity": summary.get("severity", {}),
                "category": summary.get("category", {})
            }

            history.append(history_entry)

    finally:
        print()
        print("Restoring original branch...")
        run_command(["git", "checkout", "--quiet", original_branch])

    # Save historical analysis
    history_file = PROJECT_PATH / "devops_debt_history.json"

    with open(history_file, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)

    print()
    print("=" * 60)
    print("DEBT HISTORY")
    print("=" * 60)

    for entry in history:
        print()
        print(f"Commit : {entry['commit']}")
        print(f"Message: {entry['message']}")
        print(f"Debts  : {entry['total_findings']}")

        severity = entry["severity"]

        print(
            f"High={severity.get('High', 0)} | "
            f"Medium={severity.get('Medium', 0)} | "
            f"Low={severity.get('Low', 0)}"
        )

    print()
    print("=" * 60)
    print(f"History saved to: {history_file.name}")
    print("=" * 60)


if __name__ == "__main__":
    main()