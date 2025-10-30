from dataclasses import dataclass

@dataclass
class PromptResult:
    original_prompt: str
    sql_code: str
    vulnerability_verdict: str
    ground_truth: str