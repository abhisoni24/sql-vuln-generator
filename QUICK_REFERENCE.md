# Quick Reference Card

## ⚡ 60-Second Quick Start

### 1. Get API Keys (5 minutes)
```bash
# Claude: https://console.anthropic.com/account/keys
# OpenAI: https://platform.openai.com/account/api-keys
```

### 2. Configure (1 minute)
```bash
cp .env.example .env
# Edit .env with your API keys
nano .env
```

### 3. Verify Setup (30 seconds)
```bash
python setup_check.py
```

### 4. Run Experiment (2-3 minutes)
```bash
python -m src.experiment_main
```

### 5. View Results
```bash
cd experiments
cat REPORT.md          # Markdown report
open *.png             # Visualizations
cat experiment_results.json  # Raw data
```

---

## 🔑 Most Common Commands

```bash
# Full setup
make setup

# Run with different sizes
make run-small         # 5 samples (fast)
make run              # 20 samples (default)
make run-large        # 100 samples (comprehensive)

# Analysis
make analyze          # Analyze latest results
make clean            # Clean temporary files
```

---

## 📊 What Gets Generated

```
experiments/
├── experiment_results.json      # Raw data (JSON)
├── REPORT.md                    # Detailed report (Markdown)
├── 01_vulnerability_distribution.png    # Pie chart
├── 02_cwe_distribution.png              # Bar chart
├── 03_summary_statistics.png            # Statistics
└── 04_sample_showcase.png               # Examples
```

---

## 🐛 Quick Fixes

### API Key Not Found
```bash
# Check .env file exists
ls -la .env

# Fix: Create from template
cp .env.example .env
nano .env  # Add your keys
```

### Dependencies Missing
```bash
pip install -r requirements.txt
```

### Network/Rate Limit Issues
```bash
# Try fewer samples
python -m src.experiment_main 5

# Wait a minute, then try again
```

### ModuleNotFoundError
```bash
# Must use -m flag and run from project root
python -m src.experiment_main  # ✓ Correct
python src/experiment_main.py   # ✗ Wrong
```

---

## 📈 Understanding Results

### Verdict Meanings
- **VULNERABLE** = SQL injection detected
- **NOT VULNERABLE** = Code appears safe
- **ERROR** = Analysis failed

### Key Metrics
- Vulnerability % = Vulnerable count / Total count
- CWE-89 = Most common (SQL injection)

### If You See:
- **>50% vulnerable** → GPT-3.5 generates risky SQL
- **<30% vulnerable** → Generally safe code
- **10+ CWEs found** → Many vulnerability types

---

## 💰 Estimated Costs

Per 20 samples: **$0.03 - $0.06**

- 20 samples: ~$0.05
- 50 samples: ~$0.12
- 100 samples: ~$0.25
- 500 samples: ~$1.25

---

## 📚 Documentation Map

Start → **This File** (you are here)
         ↓
Setup Help → `SETUP_GUIDE.md`
         ↓
Run Experiment → `python -m src.experiment_main`
         ↓
View Results → `experiments/REPORT.md`
         ↓
Deep Dive → `PROJECT_README.md` or `experiments/README.md`

---

## 🎯 Typical Workflow

```
1. python setup_check.py          (Verify setup - 30s)
2. python -m src.experiment_main  (Run experiment - 2-3 min)
3. cd experiments && open REPORT.md        (Review findings)
4. python -m src.utils.analysis experiments/experiment_results.json  (Deep analysis)
```

---

## 🔗 Quick Links

| Item | Where |
|------|-------|
| API Keys | https://console.anthropic.com/account/keys (Claude) |
| | https://platform.openai.com/account/api-keys (OpenAI) |
| Claude Docs | https://docs.anthropic.com/ |
| OpenAI Docs | https://platform.openai.com/docs/ |
| CWE Info | https://cwe.mitre.org/data/definitions/89.html |

---

## ⚠️ Important Notes

- **Never commit .env file** (has API keys!)
- **It's in .gitignore** (safe by default)
- **Delete experiment results before pushing**: `make clean-results`
- **Test with small samples first**: `make run-small`

---

## 🚀 Pro Tips

### Run Multiple Experiments
```bash
python -m src.experiment_main 20
mv experiments/experiment_results.json experiments/run1.json
python -m src.experiment_main 20
# Now have run1.json and latest results
```

### Export for Excel
```python
import pandas as pd
import json
with open("experiments/experiment_results.json") as f:
    df = pd.DataFrame(json.load(f))
df.to_excel("results.xlsx", index=False)
```

### Compare Experiments
```python
from src.utils.analysis import ExperimentAnalyzer
a1 = ExperimentAnalyzer("experiments/run1.json")
a2 = ExperimentAnalyzer("experiments/experiment_results.json")
print(a1.generate_comparison_report(a2))
```

---

## 📞 Need Help?

1. **Setup issues** → Run `python setup_check.py`
2. **API errors** → Check API status pages
3. **Documentation** → Read `SETUP_GUIDE.md`
4. **Deep dive** → Read `PROJECT_README.md`
5. **Results confused** → Check `experiments/README.md`

---

**Remember:** Start simple with `make setup && make run-small` to test!
