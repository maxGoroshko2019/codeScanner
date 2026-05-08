"""Historical trend comparison for code scanner."""

import json
import os


def _history_path(output_dir):
    return os.path.join(output_dir, ".scanner-history.json")


def _build_fingerprints(result):
    fingerprints = set()
    for fn in result["analysis"]["complexity"]["functions"]:
        fingerprints.add(f"complexity:{fn['file']}:{fn['name']}:{fn['complexity']}")
    for issue in result["analysis"]["security"]["issues"]:
        fingerprints.add(f"security:{issue['file']}:{issue['line']}:{issue['category']}")
    for issue in result["analysis"]["smells"]["issues"]:
        fingerprints.add(f"smell:{issue['file']}:{issue['line']}:{issue['type']}")
    return fingerprints


def _build_summary(result):
    smells = result["analysis"]["smells"]
    return {
        "totalFiles": result["repository"]["totalFiles"],
        "totalLines": result["repository"]["totalLines"],
        "totalFunctions": result["analysis"]["complexity"]["totalFunctions"],
        "flaggedFunctions": result["analysis"]["complexity"]["flaggedFunctions"],
        "securityIssues": dict(result["analysis"]["security"]["counts"]),
        "smellCounts": dict(smells["summary"]),
    }


def compare_to_history(result, output_dir):
    path = _history_path(output_dir)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    repo_path = result["repository"]["path"]
    entries = [e for e in history.get("entries", []) if e.get("repositoryPath") == repo_path]
    if not entries:
        return None

    previous = entries[-1]
    current_fingerprints = _build_fingerprints(result)
    previous_fingerprints = set(previous.get("issueFingerprints", []))

    current_security = sum(result["analysis"]["security"]["counts"].values())
    prev_security = sum(previous["summary"]["securityIssues"].values())
    current_smells = sum(result["analysis"]["smells"]["summary"].values())
    prev_smells = sum(previous["summary"]["smellCounts"].values())

    new_issues = list(current_fingerprints - previous_fingerprints)[:20]
    resolved_issues = list(previous_fingerprints - current_fingerprints)[:20]

    return {
        "previousScanId": previous["scanId"],
        "previousTimestamp": previous["timestamp"],
        "scoreDelta": result["qualityScore"] - previous["qualityScore"],
        "issueDelta": (len(current_fingerprints) - len(previous_fingerprints)),
        "details": {
            "complexity": {
                "previous": previous["summary"]["flaggedFunctions"],
                "current": result["analysis"]["complexity"]["flaggedFunctions"],
                "delta": result["analysis"]["complexity"]["flaggedFunctions"] - previous["summary"]["flaggedFunctions"],
            },
            "security": {
                "previous": prev_security,
                "current": current_security,
                "delta": current_security - prev_security,
            },
            "smells": {
                "previous": prev_smells,
                "current": current_smells,
                "delta": current_smells - prev_smells,
            },
        },
        "newIssues": new_issues,
        "resolvedIssues": resolved_issues,
    }


def save_to_history(result, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    path = _history_path(output_dir)

    try:
        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        history = {"schemaVersion": 1, "entries": []}

    fingerprints = list(_build_fingerprints(result))

    entry = {
        "scanId": result["scanId"],
        "timestamp": result["timestamp"],
        "repositoryPath": result["repository"]["path"],
        "qualityScore": result["qualityScore"],
        "grade": result["grade"],
        "summary": _build_summary(result),
        "issueFingerprints": fingerprints,
    }
    history["entries"].append(entry)

    repo_path = result["repository"]["path"]
    repo_entries = [e for e in history["entries"] if e.get("repositoryPath") == repo_path]
    if len(repo_entries) > 20:
        to_remove = repo_entries[:-20]
        history["entries"] = [e for e in history["entries"] if e not in to_remove]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
