# SQL Injection Vulnerability Experiment

## Overview

This experiment tests whether **GPT-3.5-turbo generates SQL code vulnerable to SQL injection attacks**.

### Workflow

```
1. Claude generates 20 natural language prompts for SQL code
                    ↓
2. GPT-3.5-turbo generates SQL code for each prompt
                    ↓
3. Claude analyzes each SQL code for CWE vulnerabilities
                    ↓
4. Results are saved and visualized
```

## Setup

### 1. Get API Keys

#### Claude (Anthropic)
1. Go to [Anthropic Console](https://console.anthropic.com/account/keys)
2. Create/copy your API key
3. Add to `.env` file as `CLAUDE_API_KEY`

#### OpenAI
1. Go to [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Create/copy your API key
3. Add to `.env` file as `OPENAI_API_KEY`

### 2. Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

The `.env` file should look like:
```
CLAUDE_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Experiment

```bash
# Run with default 20 samples
python -m src.experiment_main

# Or run with custom number of samples
python -m src.experiment_main 50
```

## Output Files

After running the experiment, check the `experiments/` directory:

### Data Files
- **`experiment_results.json`** - Raw data in JSON format with all prompts, SQL code, and analysis

### Reports
- **`REPORT.md`** - Comprehensive markdown report with:
  - Executive summary
  - Methodology
  - Statistical summary
  - CWE distribution
  - Detailed analysis for each sample

### Visualizations
- **`01_vulnerability_distribution.png`** - Pie chart showing % vulnerable vs safe code
- **`02_cwe_distribution.png`** - Bar chart of CWE vulnerability types found
- **`03_summary_statistics.png`** - Summary statistics display
- **`04_sample_showcase.png`** - Examples of vulnerable and safe code

## Understanding Results

### Vulnerability Categories

| Verdict | Meaning |
|---------|---------|
| **VULNERABLE** | Claude detected potential SQL injection or CWE vulnerability |
| **NOT VULNERABLE** | Code appears safe from common SQL injection patterns |
| **ERROR** | Analysis failed (API error or timeout) |

### Common CWE IDs Found

| CWE | Description |
|-----|-------------|
| **CWE-89** | SQL Injection |
| **CWE-564** | SQL Injection (variant) |
| **CWE-90** | Improper Neutralization of Special Elements |

## Example Results

### Vulnerable Code Example
```sql
-- VULNERABLE to SQL injection
SELECT * FROM users WHERE id = ?;  -- Parameter not escaped
```

### Safe Code Example
```sql
-- SAFE - using parameterized query
SELECT * FROM users WHERE id = ?;  -- Proper placeholder
```

## Troubleshooting

### "API key not found" error
- Ensure `.env` file exists in project root
- Check that keys are not quoted: `CLAUDE_API_KEY=sk-...` (not `CLAUDE_API_KEY="sk-..."`)
- Verify you're running from the project root: `cd /path/to/project && python -m src.experiment_main`

### "Rate limit exceeded" errors
- Add delays between API calls (already configured in code)
- Reduce number of samples: `python -m src.experiment_main 10`
- Wait before running again

### Missing visualizations
- Install matplotlib: `pip install matplotlib`
- Run again: `python -m src.experiment_main`

### ModuleNotFoundError
- Ensure you're in the project directory
- Run with: `python -m src.experiment_main`
- Not: `python src/experiment_main.py`

## Project Structure

```
md-vuln-markdown-generator/
├── src/
│   ├── api/
│   │   ├── claude_client.py       # Claude API client
│   │   └── openai_client.py       # OpenAI API client
│   ├── experiment_runner.py       # Main experiment logic
│   ├── experiment_main.py         # Entry point
│   ├── visualizations.py          # Chart generation
│   └── utils/
│       └── io.py                  # File I/O utilities
├── experiments/                   # Output directory (created at runtime)
├── .env                          # API keys (create from .env.example)
├── .env.example                  # Template for .env
├── requirements.txt              # Python dependencies
└── README.md                      # This file
```

## API Quotas & Costs

### Claude (Anthropic)
- Model: claude-3-5-sonnet-20241022
- Estimated cost: ~$0.10-0.20 per 20 samples
- Rate limits: Check Anthropic dashboard

### OpenAI (GPT-3.5)
- Model: gpt-3.5-turbo
- Estimated cost: ~$0.10-0.20 per 20 samples
- Rate limits: 3,500 RPM (free tier)

## Key Insights from Experiment

The experiment reveals:

1. **Prevalence**: What % of GPT-generated SQL contains injection vulnerabilities
2. **Common Patterns**: Which vulnerability types appear most frequently
3. **False Positives**: Whether Claude's analysis has false positives/negatives
4. **Best Practices**: Examples of safe vs vulnerable code

## Next Steps

After running the experiment:

1. **Review Visualizations** - Check the PNG charts for patterns
2. **Analyze REPORT.md** - Read detailed findings
3. **Examine Vulnerable Examples** - Look at specific cases in experiment_results.json
4. **Compare Models** - Run with different parameter combinations
5. **Fine-tune Prompts** - Modify `experiment_runner.py` to test different prompt styles

## References

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- [Claude API Docs](https://docs.anthropic.com/)
- [OpenAI API Docs](https://platform.openai.com/docs/)

## Questions & Issues

For issues or questions:

1. Check the troubleshooting section above
2. Review `.env.example` for setup help
3. Check API status pages (Anthropic, OpenAI)
4. Review generated REPORT.md for insights

---

**Experiment Goal**: Determine if LLMs (GPT-3.5) generate SQL injection vulnerable code, and at what rate.
