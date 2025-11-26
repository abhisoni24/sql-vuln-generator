#!/usr/bin/env python3
"""
Scan all generated code for SQL injection vulnerabilities using Semgrep.
Uses local SQL injection rules: checks/semgrep/sql-injection-rules.yaml
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from semgrep_analyzer import SemgrepAnalyzer


def main():
    """Main entry point for scanning generated code."""
    
    print("\n" + "="*80)
    print("Generated Code SQL Injection Scanner")
    print("="*80)
    print(f"Using: Comprehensive local SQL injection rules")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*80 + "\n")
    
    # Initialize analyzer with local rules
    try:
        analyzer = SemgrepAnalyzer(use_builtin=False)
    except Exception as e:
        print(f"✗ Failed to initialize Semgrep analyzer: {e}")
        print("  Make sure Semgrep is installed: pip install semgrep")
        sys.exit(1)
    
    # Get the generated_code directory
    base_dir = Path(__file__).parent / "generated_code"
    if not base_dir.exists():
        print(f"✗ No generated_code directory found at {base_dir}")
        sys.exit(1)
    
    try:
        # Scan all generated code
        scan_results = analyzer.scan_generated_code(base_dir)
        
        if not scan_results:
            print("\n✗ No generated code found to scan")
            sys.exit(1)
        
        # Generate report
        report = analyzer.generate_scan_report(scan_results)
        
        # Print summary
        print("\n" + "="*80)
        print("SCAN SUMMARY")
        print("="*80)
        print(f"Total Providers Scanned: {report['total_providers']}")
        print(f"Total Files Scanned: {report['total_files_scanned']}")
        print(f"Total Vulnerable Files: {report['total_vulnerable_files']}")
        print(f"Total Issues Found: {report['total_vulnerabilities']}")
        print(f"Overall Vulnerability Rate: {report['overall_vulnerability_rate']}")
        print(f"\nSeverity Distribution:")
        for severity, count in report['severity_distribution'].items():
            print(f"  - {severity:8}: {count:3} files")
        
        print(f"\nPer-Provider Results:")
        for provider, stats in report['providers'].items():
            print(f"  {provider.upper()}:")
            print(f"    - Total Files: {stats['total_files']}")
            print(f"    - Vulnerable: {stats['vulnerable_files']}")
            print(f"    - Issues: {stats['vulnerability_count']}")
            print(f"    - Rate: {stats['vulnerability_rate']}")
        
        # Save detailed report
        report_file = base_dir.parent / f"semgrep_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": report,
                "detailed_results": scan_results
            }, f, indent=2)
        
        print(f"\n✓ Detailed report saved to: {report_file}")
        print("="*80 + "\n")
        
        # Exit with status based on vulnerabilities found
        sys.exit(0 if report['total_vulnerable_files'] == 0 else 1)
        
    except Exception as e:
        print(f"\n✗ Scan failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
