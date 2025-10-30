#!/usr/bin/env python
"""Setup assistant for the SQL injection vulnerability experiment.

This script helps users:
1. Validate API keys
2. Test API connectivity
3. Generate configuration files
"""

import os
import sys
from pathlib import Path


def check_env_file():
    """Check if .env file exists and is properly configured."""
    print("\n" + "="*60)
    print("Checking .env Configuration")
    print("="*60)
    
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found!")
        print("\nTo fix this:")
        print("1. Copy the template: cp .env.example .env")
        print("2. Edit the file: nano .env")
        print("3. Add your API keys")
        return False
    
    print("✓ .env file exists")
    
    # Read and check content
    with open(env_path, "r") as f:
        content = f.read()
    
    has_claude_key = "CLAUDE_API_KEY=" in content and "sk-ant-" in content
    has_openai_key = "OPENAI_API_KEY=" in content and "sk-" in content
    
    if not has_claude_key:
        print("❌ CLAUDE_API_KEY not set or invalid")
    else:
        print("✓ CLAUDE_API_KEY configured")
    
    if not has_openai_key:
        print("❌ OPENAI_API_KEY not set or invalid")
    else:
        print("✓ OPENAI_API_KEY configured")
    
    return has_claude_key and has_openai_key


def check_dependencies():
    """Check if required Python packages are installed."""
    print("\n" + "="*60)
    print("Checking Python Dependencies")
    print("="*60)
    
    required_packages = {
        "requests": "HTTP library",
        "dotenv": "Environment variables",
        "openai": "OpenAI API client",
    }
    
    optional_packages = {
        "matplotlib": "Visualizations",
        "pandas": "Data processing",
        "numpy": "Numerical computing",
    }
    
    all_installed = True
    
    print("\nRequired packages:")
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"  ✓ {package:<20} ({description})")
        except ImportError:
            print(f"  ❌ {package:<20} ({description})")
            all_installed = False
    
    print("\nOptional packages:")
    for package, description in optional_packages.items():
        try:
            __import__(package)
            print(f"  ✓ {package:<20} ({description})")
        except ImportError:
            print(f"  ⚠ {package:<20} ({description}) - Not installed (can skip)")
    
    if not all_installed:
        print("\n⚠ Some required packages are missing!")
        print("Install with: pip install -r requirements.txt")
    
    return all_installed


def test_api_connectivity():
    """Test if API keys work and APIs are reachable."""
    print("\n" + "="*60)
    print("Testing API Connectivity")
    print("="*60)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    claude_key = os.getenv("CLAUDE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Test Claude
    print("\nTesting Claude API...")
    if not claude_key:
        print("  ⚠ No Claude key configured (skipping)")
    else:
        try:
            import requests
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": claude_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "Say 'ok'"}],
                },
                timeout=10,
            )
            if response.status_code == 200:
                print("  ✓ Claude API is reachable and key is valid")
            else:
                print(f"  ❌ Claude API error: {response.status_code}")
                if response.status_code == 401:
                    print("     Invalid API key")
        except Exception as e:
            print(f"  ❌ Could not reach Claude API: {e}")
    
    # Test OpenAI
    print("\nTesting OpenAI API...")
    if not openai_key:
        print("  ⚠ No OpenAI key configured (skipping)")
    else:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'ok'"}],
                max_tokens=10,
            )
            print("  ✓ OpenAI API is reachable and key is valid")
        except Exception as e:
            print(f"  ❌ Could not reach OpenAI API: {e}")
            if "401" in str(e) or "Unauthorized" in str(e):
                print("     Invalid API key")


def create_experiment_dir():
    """Create the experiments output directory."""
    print("\n" + "="*60)
    print("Setting Up Directory Structure")
    print("="*60)
    
    experiment_dir = Path("experiments")
    if experiment_dir.exists():
        print(f"✓ Directory 'experiments' already exists")
    else:
        experiment_dir.mkdir(exist_ok=True)
        print(f"✓ Created 'experiments' directory")
    
    # Check for README
    readme_path = experiment_dir / "README.md"
    if readme_path.exists():
        print(f"✓ experiments/README.md exists")
    else:
        print(f"⚠ experiments/README.md not found")


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("Next Steps")
    print("="*60)
    print("""
1. If checks passed:
   Run the experiment with: python -m src.experiment_main

2. If dependencies are missing:
   Install with: pip install -r requirements.txt

3. If API keys are invalid:
   - Check your keys at:
     Claude: https://console.anthropic.com/account/keys
     OpenAI: https://platform.openai.com/account/api-keys
   - Update .env file

4. For detailed information:
   - Read: experiments/README.md
   - Read: PROJECT_README.md

5. For help:
   - Check troubleshooting in README files
   - Review the generated REPORT.md after running
""")


def main():
    """Run all checks."""
    print("\n" + "🔬 "*20)
    print("SQL INJECTION VULNERABILITY EXPERIMENT - SETUP CHECK")
    print("🔬 "*20)
    
    try:
        # Run checks
        env_ok = check_env_file()
        deps_ok = check_dependencies()
        create_experiment_dir()
        
        # Only test API connectivity if env is OK
        if env_ok:
            test_api_connectivity()
        
        print_next_steps()
        
        if env_ok and deps_ok:
            print("\n✅ All checks passed! You're ready to run the experiment.")
            return 0
        else:
            print("\n⚠ Some issues were found. Please fix them and try again.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error during setup check: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
