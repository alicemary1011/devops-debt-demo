import subprocess
import json
from pathlib import Path


PROJECT_PATH = Path(".").resolve()
REPORT_FILE = PROJECT_PATH / "devops_debt_report.json"
HISTORY_FILE = PROJECT_PATH / "devops_debt_history.json"


def run_command(command):
    """Run a Git/system command and return its output."""
    result = subprocess.run(
        command,
        cwd=PROJECT_PATH,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(
            f"Command failed: {' '.join(command)}"
        )

    return result.stdout


def get_current_branch():
    """Return the currently active Git branch."""
    branch = run_command(
        ["git", "branch", "--show-current"]
    ).strip()

    if not branch:
        raise RuntimeError(
            "Could not determine the current Git branch."
        )

    return branch


def get_commits():
    """Return Git commits in chronological order."""
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

    run_command(
        ["git", "checkout", "--quiet", commit_hash]
    )

    # Remove old generated report.
    if REPORT_FILE.exists():
        REPORT_FILE.unlink()

    # Run the main analyzer.
    run_command(
        ["python", "analyzer.py"]
    )

    if not REPORT_FILE.exists():
        raise RuntimeError(
            "Analyzer did not generate devops_debt_report.json"
        )

    with open(
        REPORT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        report = json.load(file)

    return report


def extract_debt_ids(report):
    """Extract individual debt IDs from a report."""

    findings = report.get(
        "findings",
        []
    )

    debt_ids = set()

    for finding in findings:

        debt_id = finding.get("id")

        if debt_id:
            debt_ids.add(debt_id)

    return debt_ids


def build_debt_lifecycle(history):
    """
    Track when each debt first appeared,
    how often it appeared, and whether
    it was later remediated.
    """

    lifecycle = {}

    for index, commit in enumerate(history):

        current_debts = set(
            commit["debt_ids"]
        )

        # ----------------------------------
        # Detect newly observed debts
        # ----------------------------------

        for debt_id in current_debts:

            if debt_id not in lifecycle:

                lifecycle[debt_id] = {
                    "debt_id": debt_id,
                    "introduced_commit":
                        commit["commit"],
                    "introduced_message":
                        commit["message"],
                    "last_seen_commit":
                        commit["commit"],
                    "occurrences": 1,
                    "remediated_commit": None,
                    "status": "Active"
                }

            else:

                lifecycle[debt_id][
                    "last_seen_commit"
                ] = commit["commit"]

                lifecycle[debt_id][
                    "occurrences"
                ] += 1

        # ----------------------------------
        # Detect debts that disappeared
        # ----------------------------------

        if index > 0:

            previous_debts = set(
                history[index - 1]["debt_ids"]
            )

            disappeared = (
                previous_debts - current_debts
            )

            for debt_id in disappeared:

                if debt_id in lifecycle:

                    lifecycle[debt_id][
                        "remediated_commit"
                    ] = commit["commit"]

                    lifecycle[debt_id][
                        "status"
                    ] = "Remediated"

    return lifecycle


def main():

    print("=" * 60)
    print("DEVOPS TECHNICAL DEBT HISTORY ANALYZER")
    print("=" * 60)

    original_branch = get_current_branch()

    print()
    print(
        f"Original branch: {original_branch}"
    )

    commits = get_commits()

    if not commits:

        print("No Git commits found.")
        return

    print(
        f"Commits found: {len(commits)}"
    )

    history = []

    try:

        for commit in commits:

            report = analyze_commit(
                commit["hash"]
            )

            summary = report.get(
                "summary",
                {}
            )

            debt_ids = extract_debt_ids(
                report
            )

            history.append({

                "commit":
                    commit["hash"],

                "message":
                    commit["message"],

                "total_findings":
                    summary.get(
                        "total_findings",
                        len(debt_ids)
                    ),

                "severity":
                    summary.get(
                        "severity",
                        {}
                    ),

                "category":
                    summary.get(
                        "category",
                        {}
                    ),

                "debt_ids":
                    sorted(debt_ids)
            })

    finally:

        print()
        print(
            "Restoring original branch..."
        )

        run_command(
            [
                "git",
                "checkout",
                "--quiet",
                original_branch
            ]
        )

    # --------------------------------------
    # Build lifecycle information
    # --------------------------------------

    lifecycle = build_debt_lifecycle(
        history
    )

    # --------------------------------------
    # Create final history report
    # --------------------------------------

    final_report = {

        "project":
            "DevOps Technical Debt Analyzer",

        "analyzer_version":
            "1.3",

        "commit_history":
            history,

        "debt_lifecycle":
            list(
                lifecycle.values()
            )
    }

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            final_report,
            file,
            indent=2
        )

    # --------------------------------------
    # Display commit history
    # --------------------------------------

    print()
    print("=" * 60)
    print("DEBT HISTORY")
    print("=" * 60)

    for entry in history:

        print()
        print(
            f"Commit : {entry['commit']}"
        )

        print(
            f"Message: {entry['message']}"
        )

        print(
            f"Debts  : {entry['total_findings']}"
        )

        print(
            "Debt IDs: "
            + ", ".join(
                entry["debt_ids"]
            )
        )

        severity = entry["severity"]

        print(
            f"High={severity.get('High', 0)} | "
            f"Medium={severity.get('Medium', 0)} | "
            f"Low={severity.get('Low', 0)}"
        )

    # --------------------------------------
    # Display debt lifecycle
    # --------------------------------------

    print()
    print("=" * 60)
    print("DEBT LIFECYCLE")
    print("=" * 60)

    for debt_id, data in lifecycle.items():

        print()
        print(
            f"Debt ID       : {debt_id}"
        )

        print(
            f"Introduced    : "
            f"{data['introduced_commit']}"
        )

        print(
            f"Last Seen     : "
            f"{data['last_seen_commit']}"
        )

        print(
            f"Occurrences   : "
            f"{data['occurrences']}"
        )

        print(
            f"Status        : "
            f"{data['status']}"
        )

        if data["remediated_commit"]:

            print(
                f"Remediated In : "
                f"{data['remediated_commit']}"
            )

    print()
    print("=" * 60)

    print(
        f"History saved to: "
        f"{HISTORY_FILE.name}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()