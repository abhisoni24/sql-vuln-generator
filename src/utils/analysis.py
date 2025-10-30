"""Data analysis utilities for experiment results.

Provides functions for analyzing, summarizing, and exporting experiment data.
"""

import json
from typing import List, Dict, Any, Tuple
from collections import Counter
from pathlib import Path


class ExperimentAnalyzer:
    """Analyze and summarize experiment results."""

    def __init__(self, json_path: str):
        """Load results from JSON file."""
        with open(json_path, "r") as f:
            self.results = json.load(f)

    def get_vulnerability_stats(self) -> Dict[str, Any]:
        """Get vulnerability statistics."""
        total = len(self.results)
        vulnerable = sum(1 for r in self.results if r["verdict"] == "VULNERABLE")
        not_vulnerable = sum(1 for r in self.results if r["verdict"] == "NOT VULNERABLE")
        errors = sum(1 for r in self.results if r["verdict"] == "ERROR")

        return {
            "total": total,
            "vulnerable": vulnerable,
            "vulnerable_percentage": (vulnerable / total * 100) if total > 0 else 0,
            "not_vulnerable": not_vulnerable,
            "not_vulnerable_percentage": (not_vulnerable / total * 100) if total > 0 else 0,
            "errors": errors,
            "error_percentage": (errors / total * 100) if total > 0 else 0,
        }

    def get_cwe_distribution(self) -> Dict[str, int]:
        """Get CWE vulnerability distribution."""
        cwes = [r["cwe_id"] for r in self.results if r["cwe_id"] != "UNKNOWN"]
        return dict(Counter(cwes))

    def get_vulnerable_samples(self) -> List[Dict[str, Any]]:
        """Get all vulnerable samples."""
        return [r for r in self.results if r["verdict"] == "VULNERABLE"]

    def get_safe_samples(self) -> List[Dict[str, Any]]:
        """Get all safe samples."""
        return [r for r in self.results if r["verdict"] == "NOT VULNERABLE"]

    def get_error_samples(self) -> List[Dict[str, Any]]:
        """Get all error samples."""
        return [r for r in self.results if r["verdict"] == "ERROR"]

    def find_common_patterns(self) -> Dict[str, List[str]]:
        """Find common patterns in vulnerable SQL code."""
        patterns = {
            "string_concatenation": [],
            "unsanitized_input": [],
            "unescaped_quotes": [],
            "comment_injection": [],
        }

        for sample in self.get_vulnerable_samples():
            sql = (sample.get("sql_code") or "").lower()

            # Look for common injection patterns
            if "'" in sql or '"' in sql:
                patterns["unescaped_quotes"].append(sample["id"])

            if "concatenat" in sample.get("analysis", "").lower():
                patterns["string_concatenation"].append(sample["id"])

            if "input" in sample.get("analysis", "").lower():
                patterns["unsanitized_input"].append(sample["id"])

            if "--" in sql or "/*" in sql:
                patterns["comment_injection"].append(sample["id"])

        return patterns

    def get_sample_by_id(self, sample_id: int) -> Dict[str, Any]:
        """Get a specific sample by ID."""
        for r in self.results:
            if r.get("id") == sample_id:
                return r
        return {}

    def export_to_csv(self, output_path: str) -> None:
        """Export results to CSV file."""
        import csv

        if not self.results:
            print("No results to export")
            return

        fieldnames = list(self.results[0].keys())

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

        print(f"✓ Exported to CSV: {output_path}")

    def export_vulnerable_to_json(self, output_path: str) -> None:
        """Export only vulnerable samples to JSON."""
        vulnerable = self.get_vulnerable_samples()

        with open(output_path, "w") as f:
            json.dump(vulnerable, f, indent=2)

        print(f"✓ Exported {len(vulnerable)} vulnerable samples to: {output_path}")

    def export_summary_text(self, output_path: str) -> None:
        """Export summary statistics as text file."""
        stats = self.get_vulnerability_stats()
        cwes = self.get_cwe_distribution()

        text = "SQL INJECTION VULNERABILITY EXPERIMENT - SUMMARY\n"
        text += "=" * 60 + "\n\n"

        text += "VULNERABILITY STATISTICS\n"
        text += "-" * 60 + "\n"
        text += f"Total Samples: {stats['total']}\n"
        text += f"Vulnerable: {stats['vulnerable']} ({stats['vulnerable_percentage']:.1f}%)\n"
        text += f"Not Vulnerable: {stats['not_vulnerable']} ({stats['not_vulnerable_percentage']:.1f}%)\n"
        text += f"Errors: {stats['errors']} ({stats['error_percentage']:.1f}%)\n\n"

        if cwes:
            text += "CWE DISTRIBUTION\n"
            text += "-" * 60 + "\n"
            for cwe, count in sorted(cwes.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats["total"] * 100) if stats["total"] > 0 else 0
                text += f"{cwe}: {count} ({percentage:.1f}%)\n"

        with open(output_path, "w") as f:
            f.write(text)

        print(f"✓ Exported summary to: {output_path}")

    def print_summary(self) -> None:
        """Print summary to console."""
        stats = self.get_vulnerability_stats()
        cwes = self.get_cwe_distribution()

        print("\n" + "=" * 60)
        print("EXPERIMENT SUMMARY")
        print("=" * 60)

        print(f"\nTotal Samples: {stats['total']}")
        print(f"Vulnerable: {stats['vulnerable']} ({stats['vulnerable_percentage']:.1f}%)")
        print(f"Not Vulnerable: {stats['not_vulnerable']} ({stats['not_vulnerable_percentage']:.1f}%)")
        print(f"Errors: {stats['errors']} ({stats['error_percentage']:.1f}%)")

        if cwes:
            print("\nCWE Distribution:")
            for cwe, count in sorted(cwes.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats["total"] * 100) if stats["total"] > 0 else 0
                print(f"  {cwe}: {count} ({percentage:.1f}%)")

        print()

    def generate_comparison_report(self, other_analyzer: "ExperimentAnalyzer") -> str:
        """Generate comparison report between two experiments."""
        stats1 = self.get_vulnerability_stats()
        stats2 = other_analyzer.get_vulnerability_stats()

        report = "EXPERIMENT COMPARISON REPORT\n"
        report += "=" * 60 + "\n\n"

        report += f"{'Metric':<25} {'Experiment 1':<20} {'Experiment 2':<20}\n"
        report += "-" * 65 + "\n"
        report += f"{'Total Samples':<25} {stats1['total']:<20} {stats2['total']:<20}\n"
        report += f"{'Vulnerable':<25} {stats1['vulnerable']} ({stats1['vulnerable_percentage']:.1f}%) {stats2['vulnerable']} ({stats2['vulnerable_percentage']:.1f}%)\n"
        report += f"{'Not Vulnerable':<25} {stats1['not_vulnerable']} ({stats1['not_vulnerable_percentage']:.1f}%) {stats2['not_vulnerable']} ({stats2['not_vulnerable_percentage']:.1f}%)\n"
        report += f"{'Errors':<25} {stats1['errors']} ({stats1['error_percentage']:.1f}%) {stats2['errors']} ({stats2['error_percentage']:.1f}%)\n"

        return report


def quick_analysis(json_path: str) -> None:
    """Quick analysis of experiment results."""
    try:
        analyzer = ExperimentAnalyzer(json_path)
        analyzer.print_summary()

        # Show first few vulnerable samples
        vulnerable = analyzer.get_vulnerable_samples()
        if vulnerable:
            print("Sample Vulnerable Code:")
            print("-" * 60)
            for sample in vulnerable[:2]:
                print(f"\nPrompt: {sample['original_prompt']}")
                print(f"SQL: {sample['sql_code'][:80]}...")
                print(f"CWE: {sample['cwe_id']}")

    except FileNotFoundError:
        print(f"Error: File not found: {json_path}")
    except Exception as e:
        print(f"Error analyzing: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        json_path = sys.argv[1]
        quick_analysis(json_path)
    else:
        print("Usage: python -m src.utils.analysis <json_path>")
        print("Example: python -m src.utils.analysis experiments/experiment_results.json")
