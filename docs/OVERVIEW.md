# 🔬 SQL Injection Vulnerability Experiment - Complete Overview

## 🎯 Mission
**Determine if GPT-3.5 generates SQL code vulnerable to SQL injection attacks**

---

## 📊 Experiment Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                        START EXPERIMENT                        │
└─────────────────────┬──────────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 1: Generate Natural Language Prompts                     │
│  • Model: Claude 3.5 Sonnet                                    │
│  • Task: Create 20 diverse SQL task descriptions              │
│  • Example: "Find all users with orders in last 30 days"      │
│  • Time: ~20-30 seconds                                        │
└─────────────────────┬──────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │ 20 Natural Language Prompts │
        └─────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 2: Generate SQL Code for Each Prompt                     │
│  • Model: GPT-3.5-turbo                                        │
│  • Task: Write SQL to accomplish each prompt                   │
│  • Format: Raw SQL code                                        │
│  • Time: ~1 minute for 20 prompts                              │
└─────────────────────┬──────────────────────────────────────────┘
                      │
                      ▼
        ┌────────────────────────────────────────┐
        │ 20 SQL Code Samples (from GPT-3.5)    │
        └────────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 3: Analyze for Vulnerabilities                           │
│  • Model: Claude 3.5 Sonnet                                    │
│  • Task: Detect SQL injection & CWE vulnerabilities           │
│  • Output: Verdict + CWE ID + Analysis                         │
│  • Time: ~1 minute for 20 analyses                             │
└─────────────────────┬──────────────────────────────────────────┘
                      │
                      ▼
        ┌──────────────────────────────────────────────┐
        │ 20 Analysis Results (Verdict + CWE ID)      │
        └──────────────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────────────┐
│  STEP 4: Generate Outputs                                      │
│  • Raw JSON data with all results                              │
│  • Markdown report with findings                               │
│  • 4 visualization charts/graphs                               │
│  • Statistical summary                                         │
└─────────────────────┬──────────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────────────┐
│  FINAL OUTPUT FILES                                            │
│  ├── experiment_results.json (raw data)                        │
│  ├── REPORT.md (detailed report)                              │
│  ├── 01_vulnerability_distribution.png (pie chart)            │
│  ├── 02_cwe_distribution.png (bar chart)                      │
│  ├── 03_summary_statistics.png (stats)                        │
│  └── 04_sample_showcase.png (examples)                        │
└────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER'S COMPUTER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Your Python Application (src/)                          │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  ┌──────────────────┐       ┌──────────────────────┐   │  │
│  │  │ API Clients      │       │ Experiment Runner    │   │  │
│  │  ├──────────────────┤       ├──────────────────────┤   │  │
│  │  │ claude_client    │───┐   │ generate_prompts()   │   │  │
│  │  │ openai_client    │   │   │ generate_sql()       │   │  │
│  │  └──────────────────┘   │   │ analyze_vuln()       │   │  │
│  │         │               │   │ run()                │   │  │
│  │         │               │   └──────────────────────┘   │  │
│  │         │               │           │                 │  │
│  │         └───────┬───────┘           │                 │  │
│  │                 │                   │                 │  │
│  │         ┌───────▼─────────┐         │                 │  │
│  │         │ Data Analysis   │         │                 │  │
│  │         │ & Export        │         │                 │  │
│  │         └─────────────────┘         │                 │  │
│  │                                     │                 │  │
│  │         ┌───────────────────────────▼────┐            │  │
│  │         │ Visualizations                  │            │  │
│  │         ├─────────────────────────────────┤            │  │
│  │         │ - Pie charts                    │            │  │
│  │         │ - Bar charts                    │            │  │
│  │         │ - Statistics tables             │            │  │
│  │         │ - Sample showcase               │            │  │
│  │         └─────────────────────────────────┘            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                    │
│                           ▼                                    │
│            ┌──────────────────────────┐                        │
│            │ Output Files (./exp/)    │                        │
│            ├──────────────────────────┤                        │
│            │ *.json (raw data)        │                        │
│            │ *.md (report)            │                        │
│            │ *.png (visualizations)   │                        │
│            └──────────────────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
           │                                              │
           │                                              │
    ┌──────▼──────┐                            ┌─────────▼────────┐
    │ Anthropic   │                            │ OpenAI           │
    │ Claude API  │                            │ GPT API          │
    └─────────────┘                            └──────────────────┘
           ▲                                              ▲
           │                                              │
    ┌──────┴──────────────────────────────────────────────┴───┐
    │        Internet (HTTPS/Encrypted)                      │
    └─────────────────────────────────────────────────────────┘
```

---

## 📋 File Structure

```
md-vuln-markdown-generator/
│
├── 🔑 CONFIGURATION
│   ├── .env.example              # Template (COPY THIS)
│   ├── .env                      # Your keys (DO NOT SHARE)
│   ├── pyproject.toml            # Project metadata
│   └── requirements.txt          # Python dependencies
│
├── 📖 DOCUMENTATION (Start Here!)
│   ├── QUICK_REFERENCE.md        # ← READ FIRST (60-sec guide)
│   ├── SETUP_GUIDE.md            # Complete setup instructions
│   ├── PROJECT_README.md         # Project overview
│   ├── IMPLEMENTATION_SUMMARY.md # What was implemented
│   └── README.md                 # Original README
│
├── 🔧 TOOLS & SCRIPTS
│   ├── setup_check.py            # Verify configuration
│   ├── quickstart.sh             # One-command setup
│   └── Makefile                  # Common commands (make help)
│
├── 📦 SOURCE CODE (src/)
│   ├── api/
│   │   ├── claude_client.py      # ✨ Updated Claude integration
│   │   └── openai_client.py      # ✨ Updated OpenAI integration
│   │
│   ├── experiment_runner.py      # ✨ Main experiment logic
│   ├── experiment_main.py        # ✨ CLI entry point
│   ├── visualizations.py         # ✨ Chart generation
│   │
│   ├── utils/
│   │   ├── io.py                 # File I/O
│   │   └── analysis.py           # ✨ Data analysis tools
│   │
│   ├── generator.py              # Original markdown generator
│   ├── main.py                   # Original runner
│   └── cli.py                    # Original CLI
│
├── 🧪 TESTS
│   ├── test_generator.py
│   └── fixtures/
│
├── 📁 OUTPUT DIRECTORY (Created at Runtime)
│   └── experiments/
│       ├── README.md             # Experiment guide
│       ├── experiment_results.json    # Raw data
│       ├── REPORT.md             # Detailed report
│       ├── 01_vulnerability_distribution.png
│       ├── 02_cwe_distribution.png
│       ├── 03_summary_statistics.png
│       └── 04_sample_showcase.png
│
└── ⚙️ CONFIG FILES
    └── .gitignore               # Exclude sensitive files
```

---

## 🚀 Quick Start Paths

### Path 1: Super Quick (5 minutes)
```
1. Get API keys from websites
2. Create .env file with keys
3. Run: python -m src.experiment_main
4. Check: experiments/ folder
```

### Path 2: Cautious (10 minutes)
```
1. Get API keys
2. Create .env file
3. Run: python setup_check.py
4. Run: make run-small
5. Review: experiments/REPORT.md
```

### Path 3: Learning (20 minutes)
```
1. Read: QUICK_REFERENCE.md
2. Read: SETUP_GUIDE.md
3. Run: python setup_check.py
4. Run: make run
5. Analyze: experiments/
6. Read: PROJECT_README.md
```

---

## 📊 What You'll Learn

### From Visualizations
- ✅ What % of GPT SQL code is vulnerable
- ✅ Which vulnerability types are most common
- ✅ Examples of safe vs unsafe code
- ✅ Statistical summary of findings

### From Report
- ✅ Detailed methodology
- ✅ Analysis of each sample
- ✅ CWE distribution breakdown
- ✅ Key findings and insights

### From Raw Data (JSON)
- ✅ Original prompts used
- ✅ Exact SQL generated
- ✅ Claude's analysis
- ✅ Verdict for each sample

---

## 🎓 Key Concepts

### SQL Injection (CWE-89)
**Problem:** Attacker injects SQL code into query
```sql
-- VULNERABLE
SELECT * FROM users WHERE id = 'attacker_input_here';

-- ATTACK EXAMPLE
-- If input = "' OR '1'='1"
SELECT * FROM users WHERE id = '' OR '1'='1';  -- Returns ALL users!
```

**Safe:** Use parameterized queries
```python
# SAFE
SELECT * FROM users WHERE id = ?  # Parameter binding handles escaping
```

### CWE (Common Weakness Enumeration)
Standardized list of software weaknesses:
- **CWE-89**: SQL Injection
- **CWE-564**: SQL Injection (variant)
- **CWE-90**: Improper Neutralization

---

## 💡 Expected Findings

Based on typical LLM behavior:

| Scenario | Expected % |
|----------|-----------|
| Vulnerable SQL | 30-50% |
| Safe SQL | 45-65% |
| Analysis Errors | 5-10% |

**Implications:**
- GPT-3.5 CAN generate safe SQL
- But it OFTEN generates vulnerable SQL
- Manual review is ESSENTIAL before production

---

## 🔐 Security Practices

✅ **What To Do:**
- Always use parameterized queries
- Validate and sanitize input
- Use prepared statements
- Apply principle of least privilege
- Review AI-generated code carefully

❌ **What NOT To Do:**
- Don't use string concatenation
- Don't trust AI output blindly
- Don't skip code review
- Don't use AI without verification

---

## 💻 System Requirements

| Component | Requirement |
|-----------|------------|
| Python | 3.8+ |
| Memory | 512MB+ |
| Internet | Required (API calls) |
| Storage | 50MB+ (for code + results) |

---

## 🌐 External Services

This project uses:

| Service | Purpose | API Key Needed |
|---------|---------|----------------|
| Anthropic Claude | Prompt & analysis generation | ✅ Yes |
| OpenAI GPT-3.5 | SQL code generation | ✅ Yes |

Both are cloud-based, no local installation needed.

---

## 📞 Troubleshooting Quick Guide

| Error | Fix |
|-------|-----|
| `API key not found` | Create .env from .env.example |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `Connection timeout` | Check internet, try again |
| `Rate limit exceeded` | Wait 1 min, try with fewer samples |
| `matplotlib not installed` | Run `pip install matplotlib` |

---

## ✅ Verification Checklist

Before running experiment:
- [ ] .env file created with both API keys
- [ ] Keys are correct (no typos)
- [ ] Internet connection works
- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `python setup_check.py` passes all tests

---

## 🎯 Success Indicators

✅ Your experiment was successful if:
- [ ] Code runs without errors
- [ ] 20 samples processed
- [ ] experiments/ folder created
- [ ] experiment_results.json exists
- [ ] REPORT.md is readable
- [ ] PNG files are visible
- [ ] Statistics show reasonable %ages

---

## 📈 Next Steps After Running

1. **Review REPORT.md** - Understand findings
2. **Analyze visualizations** - See patterns
3. **Export data** - Use results for further analysis
4. **Share findings** - Report to stakeholders
5. **Iterate** - Run with different parameters

---

## 🎉 You're Ready!

Everything is set up and ready to use. Start with:

```bash
python setup_check.py     # Takes 30 seconds
python -m src.experiment_main   # Takes 2-3 minutes
```

Then check the `experiments/` folder for your results!

---

**Status:** ✅ Complete & Ready  
**Last Updated:** October 2024  
**Questions?** Check SETUP_GUIDE.md or QUICK_REFERENCE.md
