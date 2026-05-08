"""Remediation roadmap generator for code scanner."""


def generate_roadmap(result):
    items = []
    complexity = result["analysis"]["complexity"]
    security = result["analysis"]["security"]
    smells = result["analysis"]["smells"]
    duplicates = result["analysis"].get("duplicates", {})
    unused = result["analysis"].get("unusedImports", {})

    if complexity["functions"]:
        top_fn = complexity["functions"][0]
        total_funcs = complexity["totalFunctions"]
        estimated_gain = min(15, round(top_fn["complexity"] / 5))
        items.append({
            "priority": 0,
            "action": f"Refactor {top_fn['name']}() in {top_fn['file']} (complexity {top_fn['complexity']})",
            "category": "complexity",
            "currentValue": top_fn["complexity"],
            "estimatedScoreGain": estimated_gain,
            "effort": "medium" if top_fn["complexity"] < 30 else "high",
            "rationale": f"Highest complexity function; splitting would reduce flagged count ({complexity['flaggedFunctions']}/{total_funcs})",
        })

    high_sec = security["counts"]["high"]
    if high_sec > 0:
        items.append({
            "priority": 0,
            "action": f"Resolve {high_sec} high-severity security issue{'s' if high_sec > 1 else ''}",
            "category": "security",
            "currentValue": high_sec,
            "estimatedScoreGain": min(10, high_sec * 3),
            "effort": "low",
            "rationale": "High-severity issues carry the heaviest scoring penalty (10 pts each)",
        })

    if unused.get("totalUnused", 0) > 0:
        items.append({
            "priority": 0,
            "action": f"Remove {unused['totalUnused']} unused imports across {unused['totalFiles']} files",
            "category": "unused_imports",
            "currentValue": unused["totalUnused"],
            "estimatedScoreGain": 0,
            "effort": "low",
            "rationale": "Quick cleanup that improves maintainability; auto-fixable with IDE tools",
        })

    if duplicates.get("totalGroups", 0) > 0:
        items.append({
            "priority": 0,
            "action": f"Consolidate {duplicates['totalGroups']} duplicate code blocks ({duplicates['totalDuplicateLines']} lines)",
            "category": "duplicates",
            "currentValue": duplicates["totalGroups"],
            "estimatedScoreGain": 2,
            "effort": "medium",
            "rationale": "Reducing duplication simplifies maintenance and reduces bug surface area",
        })

    long_funcs = smells["summary"]["long_functions"]
    if long_funcs > 5:
        items.append({
            "priority": 0,
            "action": f"Break down {long_funcs} long functions (>50 lines each)",
            "category": "smells",
            "currentValue": long_funcs,
            "estimatedScoreGain": min(10, long_funcs // 5),
            "effort": "medium",
            "rationale": "Long functions correlate with complexity; splitting improves both smell and complexity scores",
        })

    items.sort(key=lambda x: x["estimatedScoreGain"], reverse=True)
    for i, item in enumerate(items[:5], 1):
        item["priority"] = i

    return items[:5]
