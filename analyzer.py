from pathlib import Path
import json


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_PATH = Path(".")


# ============================================================
# FILE HANDLING
# ============================================================

def read_file(file_path):
    """Read a text file and return its contents."""

    return file_path.read_text(encoding="utf-8")


def find_project_files():
    """
    Automatically discover Dockerfiles,
    GitHub Actions workflows, and Terraform files.
    """

    dockerfiles = []
    workflows = []
    terraform_files = []

    # --------------------------------------------------------
    # Find Dockerfiles
    # --------------------------------------------------------

    for file in PROJECT_PATH.rglob("*"):

        if file.is_file() and file.name.lower() == "dockerfile":
            dockerfiles.append(file)

    # --------------------------------------------------------
    # Find GitHub Actions workflows
    # --------------------------------------------------------

    workflow_directory = (
        PROJECT_PATH / ".github" / "workflows"
    )

    if workflow_directory.exists():

        for file in workflow_directory.rglob("*"):

            if (
                file.is_file()
                and file.suffix.lower() in [".yml", ".yaml"]
            ):
                workflows.append(file)

    # --------------------------------------------------------
    # Find Terraform files
    # --------------------------------------------------------

    for file in PROJECT_PATH.rglob("*.tf"):

        if file.is_file():
            terraform_files.append(file)

    return (
        dockerfiles,
        workflows,
        terraform_files
    )


# ============================================================
# D005 - UNPINNED DOCKER BASE IMAGE
# ============================================================

def detect_unpinned_docker_image(
    dockerfile,
    file_path
):

    findings = []

    for line_number, line in enumerate(
        dockerfile.splitlines(),
        start=1
    ):

        line = line.strip()

        if (
            line.startswith("FROM ")
            and ":latest" in line
        ):

            findings.append({

                "id": "D005",

                "type":
                    "Unpinned Docker Base Image",

                "category":
                    "Docker",

                "file":
                    str(file_path),

                "line":
                    line_number,

                "severity":
                    "Medium",

                "evidence":
                    line,

                "recommendation":
                    "Use a specific and controlled image version."
            })

    return findings


# ============================================================
# D006 - ROOT CONTAINER EXECUTION
# ============================================================

def detect_root_container(
    dockerfile,
    file_path
):

    findings = []

    has_user_instruction = False

    for line in dockerfile.splitlines():

        line = line.strip()

        if line.startswith("USER "):

            has_user_instruction = True

            break

    if not has_user_instruction:

        findings.append({

            "id":
                "D006",

            "type":
                "Root Container Execution",

            "category":
                "Docker",

            "file":
                str(file_path),

            "line":
                1,

            "severity":
                "Medium",

            "evidence":
                "No USER instruction found in Dockerfile.",

            "recommendation":
                "Create and use a dedicated non-root application user."
        })

    return findings


# ============================================================
# D001 - MISSING AUTOMATED TESTING
# ============================================================

def detect_missing_testing(
    workflow,
    file_path
):

    findings = []

    test_found = False

    for line in workflow.splitlines():

        line = line.strip().lower()

        if (
            "pytest" in line
            or "unittest" in line
            or "npm test" in line
            or "mvn test" in line
            or "gradle test" in line
            or "go test" in line
            or line.startswith("- name: test")
            or line.startswith("name: test")
        ):

            test_found = True

            break

    if not test_found:

        findings.append({

            "id":
                "D001",

            "type":
                "Missing Automated Testing",

            "category":
                "CI/CD",

            "file":
                str(file_path),

            "line":
                1,

            "severity":
                "High",

            "evidence":
                "No automated testing step detected.",

            "recommendation":
                "Add automated unit or integration tests before deployment."
        })

    return findings


# ============================================================
# D002 - MISSING SECURITY SCANNING
# ============================================================

def detect_missing_security_scan(
    workflow,
    file_path
):

    findings = []

    security_keywords = [

        "security",

        "security-scan",

        "security_scan",

        "snyk",

        "trivy",

        "dependabot",

        "codeql",

        "dependency-check",

        "dependency_check",

        "bandit",

        "semgrep",

        "gitleaks"
    ]

    security_found = False

    for line in workflow.splitlines():

        line_lower = line.strip().lower()

        for keyword in security_keywords:

            if keyword in line_lower:

                security_found = True

                break

        if security_found:

            break

    if not security_found:

        findings.append({

            "id":
                "D002",

            "type":
                "Missing Security Scanning",

            "category":
                "CI/CD",

            "file":
                str(file_path),

            "line":
                1,

            "severity":
                "High",

            "evidence":
                "No recognizable security scanning step detected.",

            "recommendation":
                "Add an automated security or dependency scanning stage."
        })

    return findings


# ============================================================
# D003 - OUTDATED CI/CD ACTION
# ============================================================

def detect_outdated_action(
    workflow,
    file_path
):

    findings = []

    for line_number, line in enumerate(
        workflow.splitlines(),
        start=1
    ):

        line = line.strip()

        if "uses:" in line:

            if (
                "@v1" in line
                or "@v2" in line
            ):

                findings.append({

                    "id":
                        "D003",

                    "type":
                        "Outdated CI/CD Action",

                    "category":
                        "CI/CD",

                    "file":
                        str(file_path),

                    "line":
                        line_number,

                    "severity":
                        "Medium",

                    "evidence":
                        line,

                    "recommendation":
                        "Review the action version and update it to a supported version."
                })

    return findings


# ============================================================
# D004 - DEPLOYMENT AUTOMATION ISSUE
# ============================================================

def detect_deployment_automation_issue(
    workflow,
    file_path
):

    findings = []

    deployment_found = False

    real_deployment_found = False

    deployment_line = 1

    deployment_keywords = [

        "deploy",

        "deployment"
    ]

    real_deployment_keywords = [

        "aws ",

        "aws/",

        "docker push",

        "kubectl apply",

        "helm upgrade",

        "terraform apply",

        "scp ",

        "ssh ",

        "rsync ",

        "az webapp",

        "gcloud "
    ]

    for line_number, line in enumerate(
        workflow.splitlines(),
        start=1
    ):

        line_lower = line.strip().lower()

        # Check whether a deployment step exists

        if any(
            keyword in line_lower
            for keyword in deployment_keywords
        ):

            deployment_found = True

            deployment_line = line_number

        # Check for recognizable deployment mechanisms

        if any(
            keyword in line_lower
            for keyword in real_deployment_keywords
        ):

            real_deployment_found = True

    if (
        deployment_found
        and not real_deployment_found
    ):

        findings.append({

            "id":
                "D004",

            "type":
                "Deployment Automation Issue",

            "category":
                "CI/CD",

            "file":
                str(file_path),

            "line":
                deployment_line,

            "severity":
                "Medium",

            "evidence":
                (
                    "Deployment step detected, but no recognized "
                    "automated deployment mechanism found."
                ),

            "recommendation":
                (
                    "Use an explicit automated deployment mechanism "
                    "appropriate for the target environment."
                )
        })

    return findings


# ============================================================
# D007 - HARD-CODED SENSITIVE CONFIGURATION
# ============================================================

def detect_hardcoded_secrets(
    terraform,
    file_path
):

    findings = []

    sensitive_keywords = [

        "password",

        "passwd",

        "secret",

        "api_key",

        "apikey",

        "access_key",

        "private_key",

        "token"
    ]

    for line_number, line in enumerate(
        terraform.splitlines(),
        start=1
    ):

        line_stripped = line.strip()

        line_lower = line_stripped.lower()

        for keyword in sensitive_keywords:

            if (
                keyword in line_lower
                and "=" in line_stripped
            ):

                # Ignore variable declarations

                if line_lower.startswith("variable "):

                    continue

                value = line_stripped.split(
                    "=",
                    1
                )[1].strip()

                if (
                    value
                    and value not in [
                        "null",
                        "var."
                    ]
                ):

                    findings.append({

                        "id":
                            "D007",

                        "type":
                            "Hard-coded Sensitive Configuration",

                        "category":
                            "Terraform",

                        "file":
                            str(file_path),

                        "line":
                            line_number,

                        "severity":
                            "High",

                        "evidence":
                            line_stripped,

                        "recommendation":
                            (
                                "Use a secure secret-management "
                                "mechanism instead of storing "
                                "sensitive values in source code."
                            )
                    })

                break

    return findings


# ============================================================
# D008 - MISSING INFRASTRUCTURE METADATA
# ============================================================

def detect_missing_infrastructure_metadata(
    terraform,
    file_path
):

    findings = []

    resource_found = False

    tags_found = False

    resource_line = 1

    for line_number, line in enumerate(
        terraform.splitlines(),
        start=1
    ):

        line_stripped = line.strip()

        line_lower = line_stripped.lower()

        # Detect Terraform resources

        if line_lower.startswith("resource "):

            resource_found = True

            resource_line = line_number

        # Detect tags

        if (
            line_lower.startswith("tags")
            or line_lower.startswith("tags =")
        ):

            tags_found = True

    if (
        resource_found
        and not tags_found
    ):

        findings.append({

            "id":
                "D008",

            "type":
                "Missing Infrastructure Metadata",

            "category":
                "Terraform",

            "file":
                str(file_path),

            "line":
                resource_line,

            "severity":
                "Low",

            "evidence":
                "No tags block detected for infrastructure resources.",

            "recommendation":
                (
                    "Add useful metadata such as Environment, "
                    "Project, Owner, and Application tags."
                )
        })

    return findings


# ============================================================
# SUMMARY GENERATION
# ============================================================

def generate_summary(findings):

    severity_summary = {

        "High": 0,

        "Medium": 0,

        "Low": 0
    }

    category_summary = {

        "CI/CD": 0,

        "Docker": 0,

        "Terraform": 0
    }

    for finding in findings:

        severity = finding["severity"]

        category = finding["category"]

        if severity in severity_summary:

            severity_summary[severity] += 1

        if category in category_summary:

            category_summary[category] += 1

    return {

        "total_findings":
            len(findings),

        "severity":
            severity_summary,

        "category":
            category_summary
    }


# ============================================================
# DISPLAY SUMMARY
# ============================================================

def display_summary(summary):

    print("\n==========================================")

    print("           DEVOPS DEBT SUMMARY")

    print("==========================================")

    print(
        f"\nTotal Findings : "
        f"{summary['total_findings']}"
    )

    print("\nSeverity")

    print("------------------------------------------")

    print(
        f"High           : "
        f"{summary['severity']['High']}"
    )

    print(
        f"Medium         : "
        f"{summary['severity']['Medium']}"
    )

    print(
        f"Low            : "
        f"{summary['severity']['Low']}"
    )

    print("\nCategory")

    print("------------------------------------------")

    print(
        f"CI/CD          : "
        f"{summary['category']['CI/CD']}"
    )

    print(
        f"Docker         : "
        f"{summary['category']['Docker']}"
    )

    print(
        f"Terraform      : "
        f"{summary['category']['Terraform']}"
    )

    print("\n==========================================")


# ============================================================
# JSON REPORT
# ============================================================

def save_json_report(
    findings,
    summary
):

    report = {

        "project":
            "DevOps Debt Demo",

        "analyzer_version":
            "1.2",

        "summary":
            summary,

        "findings":
            findings
    }

    output_file = (
        PROJECT_PATH
        / "devops_debt_report.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print(
        f"\nJSON report saved to: "
        f"{output_file}"
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    # ========================================================
    # DISCOVER PROJECT FILES
    # ========================================================

    (
        dockerfiles,
        workflows,
        terraform_files
    ) = find_project_files()

    # ========================================================
    # DISPLAY DISCOVERED FILES
    # ========================================================

    print("\n==========================================")

    print("          PROJECT FILE DISCOVERY")

    print("==========================================")

    print(
        f"\nDockerfiles found   : "
        f"{len(dockerfiles)}"
    )

    for file in dockerfiles:

        print(
            f"  - {file}"
        )

    print(
        f"\nWorkflows found     : "
        f"{len(workflows)}"
    )

    for file in workflows:

        print(
            f"  - {file}"
        )

    print(
        f"\nTerraform files     : "
        f"{len(terraform_files)}"
    )

    for file in terraform_files:

        print(
            f"  - {file}"
        )

    print("\n==========================================")

    # ========================================================
    # READ DISCOVERED FILES
    # ========================================================

    dockerfile_contents = []

    for file_path in dockerfiles:

        try:

            content = read_file(file_path)

            dockerfile_contents.append(
                (
                    file_path,
                    content
                )
            )

        except Exception as error:

            print(
                f"Could not read {file_path}: "
                f"{error}"
            )


    workflow_contents = []

    for file_path in workflows:

        try:

            content = read_file(file_path)

            workflow_contents.append(
                (
                    file_path,
                    content
                )
            )

        except Exception as error:

            print(
                f"Could not read {file_path}: "
                f"{error}"
            )


    terraform_contents = []

    for file_path in terraform_files:

        try:

            content = read_file(file_path)

            terraform_contents.append(
                (
                    file_path,
                    content
                )
            )

        except Exception as error:

            print(
                f"Could not read {file_path}: "
                f"{error}"
            )


    # ========================================================
    # STORE FINDINGS
    # ========================================================

    findings = []


    # ========================================================
    # DOCKER ANALYSIS
    # ========================================================

    for file_path, content in dockerfile_contents:

        findings += detect_unpinned_docker_image(
            content,
            file_path
        )

        findings += detect_root_container(
            content,
            file_path
        )


    # ========================================================
    # CI/CD ANALYSIS
    # ========================================================

    for file_path, content in workflow_contents:

        findings += detect_missing_testing(
            content,
            file_path
        )

        findings += detect_missing_security_scan(
            content,
            file_path
        )

        findings += detect_outdated_action(
            content,
            file_path
        )

        findings += detect_deployment_automation_issue(
            content,
            file_path
        )


    # ========================================================
    # TERRAFORM ANALYSIS
    # ========================================================

    for file_path, content in terraform_contents:

        findings += detect_hardcoded_secrets(
            content,
            file_path
        )

        findings += detect_missing_infrastructure_metadata(
            content,
            file_path
        )


    # ========================================================
    # DISPLAY FINDINGS
    # ========================================================

    print("\n==========================================")

    print("       DEVOPS TECHNICAL DEBT ANALYZER")

    print("==========================================")

    print(
        f"\nTotal Debt Detected: "
        f"{len(findings)}"
    )


    for finding in findings:

        print("\n------------------------------------------")

        print(
            "Debt ID:",
            finding["id"]
        )

        print(
            "Type:",
            finding["type"]
        )

        print(
            "Category:",
            finding["category"]
        )

        print(
            "File:",
            finding["file"]
        )

        print(
            "Line:",
            finding["line"]
        )

        print(
            "Severity:",
            finding["severity"]
        )

        print(
            "Evidence:",
            finding["evidence"]
        )

        print(
            "Recommendation:",
            finding["recommendation"]
        )


    # ========================================================
    # GENERATE SUMMARY
    # ========================================================

    summary = generate_summary(
        findings
    )

    display_summary(
        summary
    )


    # ========================================================
    # SAVE JSON REPORT
    # ========================================================

    save_json_report(
        findings,
        summary
    )