import json
import xml.etree.ElementTree as ET
import csv
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def get_git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"

def parse_junit_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    total = 0
    failures = 0
    skipped = 0
    
    if root.tag == "testsuites":
        for testsuite in root.findall("testsuite"):
            total += int(testsuite.get("tests", 0))
            failures += int(testsuite.get("failures", 0)) + int(testsuite.get("errors", 0))
            skipped += int(testsuite.get("skipped", 0))
    elif root.tag == "testsuite":
        total = int(root.get("tests", 0))
        failures = int(root.get("failures", 0)) + int(root.get("errors", 0))
        skipped = int(root.get("skipped", 0))
        
    passed = total - failures - skipped
    return total, passed, failures, skipped

def main():
    reports_dir = Path("reports")
    cov_json_path = reports_dir / "coverage.json"
    junit_xml_path = reports_dir / "junit.xml"
    md_out_path = reports_dir / "coverage.md"
    history_csv_path = reports_dir / "coverage_history.csv"

    if not cov_json_path.exists():
        print(f"Error: {cov_json_path} not found.")
        sys.exit(1)
    if not junit_xml_path.exists():
        print(f"Error: {junit_xml_path} not found.")
        sys.exit(1)

    with open(cov_json_path, 'r', encoding='utf-8') as f:
        cov_data = json.load(f)

    total_tests, passed_tests, failed_tests, skipped_tests = parse_junit_xml(junit_xml_path)

    totals = cov_data.get("totals", {})
    percent_covered = totals.get("percent_covered", 0.0)
    covered_lines = totals.get("covered_lines", 0)
    num_statements = totals.get("num_statements", 0)
    missing_lines = totals.get("missing_lines", 0)

    commit_hash = get_git_commit()
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Read previous history to compare
    prev_coverage = None
    if history_csv_path.exists():
        with open(history_csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                prev_coverage = float(rows[-1]['Coverage Percentage'])

    coverage_trend = ""
    if prev_coverage is not None:
        diff = percent_covered - prev_coverage
        if diff > 0:
            coverage_trend = f"(+{diff:.2f}%) [UP]"
        elif diff < 0:
            coverage_trend = f"({diff:.2f}%) [DOWN]"
        else:
            coverage_trend = "(No change) [-]"

    md_content = f"# Test Coverage Report\n\n"
    md_content += f"**Generated:** {timestamp_str} | **Commit:** `{commit_hash}`\n\n"

    md_content += f"## Test Summary\n\n"
    md_content += f"- **Total Tests:** {total_tests}\n"
    md_content += f"- **Passed:** {passed_tests}\n"
    md_content += f"- **Failed:** {failed_tests}\n"
    md_content += f"- **Skipped:** {skipped_tests}\n\n"

    md_content += f"## Coverage Summary\n\n"
    md_content += f"- **Overall Coverage:** {percent_covered:.2f}% {coverage_trend}\n"
    md_content += f"- **Covered Statements:** {covered_lines} / {num_statements}\n"
    md_content += f"- **Missed Statements:** {missing_lines}\n\n"

    md_content += f"## Module Breakdown\n\n"
    md_content += f"| Module | Coverage | Missed Lines |\n"
    md_content += f"|--------|----------|--------------|\n"
    
    files = cov_data.get("files", {})
    for filename, file_data in sorted(files.items()):
        file_pct = file_data.get("summary", {}).get("percent_covered", 0.0)
        missing = file_data.get("missing_lines", [])
        missing_str = ", ".join(map(str, missing)) if missing else "None"
        # truncate missing string if too long
        if len(missing_str) > 50:
            missing_str = missing_str[:47] + "..."
        md_content += f"| `{filename}` | {file_pct:.2f}% | {missing_str} |\n"

    # Recent history table
    if history_csv_path.exists():
        with open(history_csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            history_rows = list(reader)
            if len(history_rows) > 1:
                md_content += f"\n## Recent History\n\n"
                md_content += f"| Timestamp | Commit | Tests | Passed | Coverage |\n"
                md_content += f"|-----------|--------|-------|--------|----------|\n"
                for row in history_rows[-5:]: # last 5 entries
                    if row[0] == "Timestamp": continue # skip header
                    md_content += f"| {row[0]} | `{row[1]}` | {row[2]} | {row[3]} | {row[6]}% |\n"

    with open(md_out_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Generated Markdown report: {md_out_path}")

    # Append to history
    file_exists = history_csv_path.exists()
    with open(history_csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Commit", "Total Tests", "Passed Tests", "Failed Tests", "Skipped Tests", "Coverage Percentage", "Covered Statements", "Total Statements", "Missed Statements"])
        writer.writerow([
            timestamp_str,
            commit_hash,
            total_tests,
            passed_tests,
            failed_tests,
            skipped_tests,
            f"{percent_covered:.2f}",
            covered_lines,
            num_statements,
            missing_lines
        ])
    print(f"Updated coverage history: {history_csv_path}")

if __name__ == "__main__":
    main()
