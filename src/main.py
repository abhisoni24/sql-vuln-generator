"""Runner script for the SQL-generation vulnerability experiment.

This script loads API keys from the environment, calls Claude to generate
natural-language prompts, calls OpenAI (gpt-3.5) to produce SQL for each
prompt, asks Claude to analyze the SQL for vulnerabilities, and writes a
markdown results file.
"""

import os
from dotenv import load_dotenv, find_dotenv

# Support running as a module (python -m src.main) and as a script (python src/main.py)
try:
    # when run as `python -m src.main` the package context allows relative imports
    from .api.claude_client import ClaudeClient
    from .api.openai_client import OpenAIClient
    from .generator import run_experiment
    from .utils.io import write_markdown_results
except Exception:
    # fallback to absolute imports when module/package context isn't present
    from api.claude_client import ClaudeClient
    from api.openai_client import OpenAIClient
    from generator import run_experiment
    from utils.io import write_markdown_results


def main():
    # load .env (search up from cwd). This will pick up a .env in project root.
    env_path = find_dotenv() or ""
    if env_path:
        load_dotenv(env_path)
    else:
        # fallback: call load_dotenv() which will try to load .env from cwd
        load_dotenv()

    claude = ClaudeClient()
    try:
        openai = OpenAIClient()
    except RuntimeError as e:
        # provide clearer guidance if keys weren't loaded
        raise RuntimeError(
            str(e)
            + "\nTried to load .env but OPENAI_API_KEY not found. Make sure you have a `.env` file with OPENAI_API_KEY and CLAUDE_API_KEY in the project root, or export the variables in your shell."
        )

    results = run_experiment(claude, openai, n=20)

    out_path = os.path.join(os.path.dirname(__file__), "..", "results.md")
    out_path = os.path.normpath(out_path)
    write_markdown_results(out_path, results)
    print("Done. Results written to", out_path)


if __name__ == "__main__":
    main()