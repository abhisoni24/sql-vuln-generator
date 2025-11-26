"""
Semgrep-based static analysis for SQL injection vulnerabilities.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SemgrepAnalyzer:
    """
    Static analysis using Semgrep to detect SQL injection vulnerabilities.
    """

    def __init__(self, rules_path: str = "checks/semgrep/sql-injection-rules.yaml", use_builtin: bool = False):
        """
        Initialize the Semgrep analyzer.

        Args:
            rules_path: Path to the Semgrep rules file (local rules)
            use_builtin: If True, use Semgrep's built-in SQL injection rules (p/sql-injection)
        """
        self.use_builtin = use_builtin
        if not use_builtin:
            self.rules_path = Path(__file__).parent.parent / rules_path
            if not self.rules_path.exists():
                raise FileNotFoundError(f"Semgrep rules file not found: {self.rules_path}")
        else:
            self.rules_path = None
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
            if self.use_builtin:
                cmd = [
                    "semgrep",
                    "--config", "p/sql-injection",
                    "--json",
                    temp_file
                ]
            else:
                cmd = [
                    "semgrep",
                    "--config", str(self.rules_path),
                    "--json",
                    temp_file
                ]
            
            result = subprocess.run(
                cmd,
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
    
    def scan_directory(self, directory: Path, recursive: bool = True) -> Dict[str, Dict]:
        """
        Scan all Python files in a directory for SQL injection vulnerabilities.
        
        Args:
            directory: Path to the directory to scan
            recursive: If True, scan subdirectories recursively
            
        Returns:
            Dictionary mapping file paths to analysis results
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        results = {}
        
        # Find all Python files
        if recursive:
            py_files = list(directory.glob("**/*.py"))
        else:
            py_files = list(directory.glob("*.py"))
        
        print(f"\n{'='*80}")
        print(f"Scanning {len(py_files)} Python files in {directory}")
        print(f"Using: {'Semgrep built-in SQL injection rules' if self.use_builtin else 'Local SQL injection rules'}")
        print(f"{'='*80}\n")
        
        for i, py_file in enumerate(py_files, 1):
            try:
                # Read the file
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                
                # Analyze
                scenario_name = py_file.stem
                analysis = self.analyze_code(code, scenario_name)
                results[str(py_file)] = analysis
                
                # Print progress
                status = "✓ VULNERABLE" if analysis["is_vulnerable"] else "✓ CLEAN"
                severity = analysis.get("severity", "NONE")
                print(f"[{i:3d}/{len(py_files)}] {status:15} [{severity:8}] {py_file.name}")
                
            except Exception as e:
                print(f"[{i:3d}/{len(py_files)}] ✗ ERROR       [UNKNOWN] {py_file.name}: {e}")
                results[str(py_file)] = {
                    "is_vulnerable": False,
                    "vulnerability_type": "Scan Error",
                    "cwe_id": "N/A",
                    "severity": "UNKNOWN",
                    "matched_check_ids": [],
                    "vulnerable_lines": [],
                    "explanation": f"Failed to scan: {str(e)}",
                    "remediation": "N/A"
                }
        
        return results
    
    def scan_generated_code(self, base_directory: Optional[Path] = None) -> Dict[str, Dict]:
        """
        Scan all generated code from LLM providers.
        
        Args:
            base_directory: Base directory containing generated_code folders
                           (defaults to ./generated_code from current directory)
        
        Returns:
            Dictionary mapping provider directories to scan results
        """
        if base_directory is None:
            base_directory = Path.cwd() / "generated_code"
        else:
            base_directory = Path(base_directory)
        
        if not base_directory.exists():
            raise FileNotFoundError(f"Generated code directory not found: {base_directory}")
        
        all_results = {}
        
        # Find all provider-specific directories (pattern: provider_timestamp)
        provider_dirs = sorted([
            d for d in base_directory.iterdir() 
            if d.is_dir() and '_' in d.name
        ])
        
        if not provider_dirs:
            print(f"No generated code directories found in {base_directory}")
            return all_results
        
        print(f"\n{'='*80}")
        print(f"Scanning generated code from {len(provider_dirs)} provider(s)")
        print(f"{'='*80}")
        
        for provider_dir in provider_dirs:
            provider_name = provider_dir.name.rsplit('_', 1)[0]  # Extract provider name before timestamp
            print(f"\n--- Provider: {provider_name.upper()} ({provider_dir.name}) ---")
            
            # Scan the directory
            results = self.scan_directory(provider_dir, recursive=False)
            all_results[provider_name] = {
                "directory": str(provider_dir),
                "results": results
            }
        
        return all_results
    
    def generate_scan_report(self, scan_results: Dict[str, Dict]) -> Dict:
        """
        Generate a summary report from scan results.
        
        Args:
            scan_results: Results from scan_generated_code()
            
        Returns:
            Dictionary with summary statistics and details
        """
        report = {
            "total_providers": len(scan_results),
            "total_files_scanned": 0,
            "total_vulnerable_files": 0,
            "total_vulnerabilities": 0,
            "providers": {}
        }
        
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "NONE": 0}
        
        for provider_name, provider_data in scan_results.items():
            results = provider_data.get("results", {})
            
            vulnerable_count = 0
            vuln_count = 0
            
            for file_path, analysis in results.items():
                report["total_files_scanned"] += 1
                
                if analysis.get("is_vulnerable", False):
                    vulnerable_count += 1
                    report["total_vulnerable_files"] += 1
                    vuln_count += len(analysis.get("matched_check_ids", []))
                
                severity = analysis.get("severity", "NONE")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            report["total_vulnerabilities"] += vuln_count
            
            report["providers"][provider_name] = {
                "total_files": len(results),
                "vulnerable_files": vulnerable_count,
                "vulnerability_count": vuln_count,
                "vulnerability_rate": f"{(vulnerable_count / len(results) * 100):.1f}%" if results else "N/A"
            }
        
        report["severity_distribution"] = severity_counts
        report["overall_vulnerability_rate"] = f"{(report['total_vulnerable_files'] / report['total_files_scanned'] * 100):.1f}%" if report['total_files_scanned'] > 0 else "N/A"
        
        return report