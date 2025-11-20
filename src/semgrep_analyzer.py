"""
Semgrep-based static analysis for SQL injection vulnerabilities.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional


class SemgrepAnalyzer:
    """
    Static analysis using Semgrep to detect SQL injection vulnerabilities.
    """

    def __init__(self, rules_path: str = "checks/semgrep/sql-injection-rules.yaml"):
        """
        Initialize the Semgrep analyzer.

        Args:
            rules_path: Path to the Semgrep rules file
        """
        self.rules_path = Path(__file__).parent.parent / rules_path
        if not self.rules_path.exists():
            raise FileNotFoundError(f"Semgrep rules file not found: {self.rules_path}")
        self._check_semgrep_installation()

    def _check_semgrep_installation(self):
        """Check if Semgrep is installed and available."""
        try:
            result = subprocess.run(
                ["semgrep", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✓ Semgrep {result.stdout.strip()} found")
            else:
                print("⚠️ Semgrep found but returned non-zero exit code")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Semgrep not found. Install with: pip install semgrep")
            print("   Or run: python -m pip install semgrep")

    def analyze_code(self, code: str, scenario_name: str = "unknown") -> Dict:
        """
        Analyze code for SQL injection vulnerabilities using Semgrep.

        Args:
            code: Python code to analyze
            scenario_name: Name of the scenario for reporting

        Returns:
            Dictionary with analysis results in the same format as LLM analysis
        """
        # Create a temporary file with the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # Run Semgrep analysis
            result = subprocess.run(
                [
                    "semgrep",
                    "--config", str(self.rules_path),
                    "--json",
                    temp_file
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse the results
            analysis = self._parse_semgrep_output(result, scenario_name)

        except subprocess.TimeoutExpired:
            analysis = {
                "is_vulnerable": False,
                "vulnerability_type": "Analysis Timeout",
                "cwe_id": "N/A",
                "severity": "UNKNOWN",
                "matched_check_ids": [],
                "vulnerable_lines": [],
                "explanation": "Semgrep analysis timed out",
                "remediation": "N/A"
            }
        except Exception as e:
            analysis = {
                "is_vulnerable": False,
                "vulnerability_type": "Analysis Error",
                "cwe_id": "N/A",
                "severity": "UNKNOWN",
                "matched_check_ids": [],
                "vulnerable_lines": [],
                "explanation": f"Semgrep analysis failed: {str(e)}",
                "remediation": "N/A"
            }
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass

        return analysis

    def _parse_semgrep_output(self, result: subprocess.CompletedProcess, scenario_name: str) -> Dict:
        """
        Parse Semgrep JSON output into our standard analysis format.

        Args:
            result: Subprocess result from Semgrep
            scenario_name: Scenario name for context

        Returns:
            Standardized analysis dictionary
        """
        # Exit code 0 = findings found, 1 = no findings, other = error
        if result.returncode == 1:
            # No vulnerabilities found
            return {
                "is_vulnerable": False,
                "vulnerability_type": "None",
                "cwe_id": "N/A",
                "severity": "NONE",
                "matched_check_ids": [],
                "vulnerable_lines": [],
                "explanation": "Semgrep found no SQL injection vulnerabilities",
                "remediation": "N/A"
            }
        elif result.returncode not in [0, 1]:
            # Actual error
            return {
                "is_vulnerable": False,
                "vulnerability_type": "Analysis Error",
                "cwe_id": "N/A",
                "severity": "UNKNOWN",
                "matched_check_ids": [],
                "vulnerable_lines": [],
                "explanation": f"Semgrep failed with exit code {result.returncode}: {result.stderr}",
                "remediation": "N/A"
            }

        try:
            # Parse JSON output
            if result.stdout.strip():
                semgrep_results = json.loads(result.stdout)
            else:
                semgrep_results = {"results": []}

            return self._convert_semgrep_to_standard_format(semgrep_results)

        except json.JSONDecodeError:
            return {
                "is_vulnerable": False,
                "vulnerability_type": "Parse Error",
                "cwe_id": "N/A",
                "severity": "UNKNOWN",
                "matched_check_ids": [],
                "vulnerable_lines": [],
                "explanation": f"Failed to parse Semgrep output: {result.stdout[:200]}...",
                "remediation": "N/A"
            }

    def _convert_semgrep_to_standard_format(self, semgrep_results: Dict) -> Dict:
        """
        Convert Semgrep results to our standard analysis format.

        Args:
            semgrep_results: Raw Semgrep JSON output

        Returns:
            Standardized analysis dictionary
        """
        results = semgrep_results.get("results", [])
        
        # Extract vulnerabilities from results
        vulnerabilities = []
        for result in results:
            vuln = {
                "rule_id": result.get("check_id", "unknown"),
                "message": result.get("extra", {}).get("message", ""),
                "severity": result.get("extra", {}).get("severity", "UNKNOWN"),
                "line": result.get("start", {}).get("line", 0),
                "code": result.get("extra", {}).get("lines", "")
            }
            vulnerabilities.append(vuln)

        # Determine overall vulnerability status
        is_vulnerable = len(vulnerabilities) > 0

        # Map severity levels
        severity_map = {
            "ERROR": "HIGH",
            "WARNING": "MEDIUM", 
            "INFO": "LOW"
        }

        # Get highest severity
        severity = "NONE"
        if vulnerabilities:
            severities = [v["severity"] for v in vulnerabilities]
            if "ERROR" in severities:
                severity = "HIGH"
            elif "WARNING" in severities:
                severity = "MEDIUM"
            else:
                severity = "LOW"

        # Extract vulnerable lines
        vulnerable_lines = list(set(v["line"] for v in vulnerabilities if v["line"] > 0))

        # Create explanation
        if is_vulnerable:
            rule_ids = list(set(v["rule_id"] for v in vulnerabilities))
            explanation = f"Semgrep detected {len(vulnerabilities)} potential issue(s): {', '.join(rule_ids)}"
            remediation = "Use prepared statements with parameterized queries. Avoid string concatenation in SQL queries."
        else:
            explanation = "Semgrep found no SQL injection vulnerabilities"
            remediation = "N/A"

        return {
            "is_vulnerable": is_vulnerable,
            "vulnerability_type": "SQL Injection" if is_vulnerable else "None",
            "cwe_id": "CWE-89" if is_vulnerable else "N/A",
            "severity": severity,
            "matched_check_ids": list(set(v["rule_id"] for v in vulnerabilities)),
            "vulnerable_lines": vulnerable_lines,
            "explanation": explanation,
            "remediation": remediation,
            "analyzer": "semgrep",
            "raw_findings": vulnerabilities
        }

    def get_provider_name(self) -> str:
        """Get the provider name for reporting."""
        return "Semgrep"
    
    def get_model_name(self) -> str:
        """Get the model name for reporting."""
        return "static-analysis"