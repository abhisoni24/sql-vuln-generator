"""Visualization utilities for experiment results.

Generates comprehensive visualizations including:
- Vulnerability distribution pie chart
- CWE distribution bar chart
- Sample analysis heatmap
- Summary statistics table
"""

import json
import os
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter


def load_results(json_path: str) -> List[Dict[str, Any]]:
    """Load experiment results from JSON file."""
    with open(json_path, "r") as f:
        return json.load(f)


def create_vulnerability_distribution_chart(results: List[Dict], output_path: str):
    """Create a pie chart showing vulnerability distribution."""
    verdicts = [r["verdict"] for r in results]
    verdict_counts = Counter(verdicts)
    
    # Prepare data
    labels = []
    sizes = []
    colors = []
    color_map = {
        "VULNERABLE": "#FF6B6B",
        "NOT VULNERABLE": "#51CF66",
        "ERROR": "#868E96",
        "UNKNOWN": "#FFD93D",
    }
    
    for verdict, count in sorted(verdict_counts.items()):
        labels.append(f"{verdict}\n({count})")
        sizes.append(count)
        colors.append(color_map.get(verdict, "#999999"))
    
    # Create pie chart
    fig, ax = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 12, "weight": "bold"},
    )
    
    # Enhance appearance
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontsize(11)
        autotext.set_weight("bold")
    
    ax.set_title(
        "SQL Code Vulnerability Distribution\n(GPT-3.5 Generated Code)",
        fontsize=16,
        weight="bold",
        pad=20,
    )
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Saved vulnerability distribution chart: {output_path}")
    plt.close()


def create_cwe_distribution_chart(results: List[Dict], output_path: str):
    """Create a bar chart showing CWE ID distribution."""
    cwe_ids = []
    for r in results:
        if r.get("cwe_id") and r["cwe_id"] != "UNKNOWN":
            cwe_ids.append(r["cwe_id"])
    
    if not cwe_ids:
        print("  (No CWE data to visualize)")
        return
    
    cwe_counts = Counter(cwe_ids)
    
    # Sort by count
    sorted_cwes = sorted(cwe_counts.items(), key=lambda x: x[1], reverse=True)
    cwes, counts = zip(*sorted_cwes)
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(cwes, counts, color="#FF6B6B", edgecolor="black", linewidth=1.5)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{int(height)}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )
    
    ax.set_xlabel("CWE ID", fontsize=13, weight="bold")
    ax.set_ylabel("Count", fontsize=13, weight="bold")
    ax.set_title(
        "CWE Vulnerability Distribution in Generated SQL Code",
        fontsize=14,
        weight="bold",
        pad=20,
    )
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Saved CWE distribution chart: {output_path}")
    plt.close()


def create_summary_statistics_table(results: List[Dict], output_path: str):
    """Create and save a summary statistics visualization."""
    # Calculate statistics
    total = len(results)
    vulnerable = sum(1 for r in results if r["verdict"] == "VULNERABLE")
    not_vulnerable = sum(1 for r in results if r["verdict"] == "NOT VULNERABLE")
    errors = sum(1 for r in results if r["verdict"] == "ERROR")
    
    vulnerable_pct = (vulnerable / total * 100) if total > 0 else 0
    not_vulnerable_pct = (not_vulnerable / total * 100) if total > 0 else 0
    error_pct = (errors / total * 100) if total > 0 else 0
    
    # Count unique CWEs
    unique_cwes = len(set(r["cwe_id"] for r in results if r["cwe_id"] != "UNKNOWN"))
    
    # Create figure with text
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis("off")
    
    # Title
    title_text = "SQL Injection Vulnerability Experiment\nSummary Statistics"
    ax.text(
        0.5,
        0.95,
        title_text,
        ha="center",
        va="top",
        fontsize=18,
        weight="bold",
        transform=ax.transAxes,
    )
    
    # Statistics boxes
    stats_data = [
        ("Total Samples", str(total), "#3498DB"),
        ("Vulnerable", f"{vulnerable} ({vulnerable_pct:.1f}%)", "#FF6B6B"),
        ("Not Vulnerable", f"{not_vulnerable} ({not_vulnerable_pct:.1f}%)", "#51CF66"),
        ("Errors", f"{errors} ({error_pct:.1f}%)", "#868E96"),
        ("Unique CWEs Found", str(unique_cwes), "#FFD93D"),
    ]
    
    y_position = 0.80
    for label, value, color in stats_data:
        # Background box
        box = mpatches.FancyBboxPatch(
            (0.1, y_position - 0.08),
            0.8,
            0.07,
            boxstyle="round,pad=0.01",
            transform=ax.transAxes,
            facecolor=color,
            edgecolor="black",
            linewidth=2,
            alpha=0.3,
        )
        ax.add_patch(box)
        
        # Text
        ax.text(
            0.15,
            y_position - 0.04,
            f"{label}:",
            ha="left",
            va="center",
            fontsize=12,
            weight="bold",
            transform=ax.transAxes,
        )
        ax.text(
            0.85,
            y_position - 0.04,
            value,
            ha="right",
            va="center",
            fontsize=12,
            weight="bold",
            transform=ax.transAxes,
        )
        
        y_position -= 0.12
    
    # Footer
    ax.text(
        0.5,
        0.05,
        "Experiment: Testing if GPT-3.5 generates SQL injection vulnerable code",
        ha="center",
        va="bottom",
        fontsize=10,
        style="italic",
        transform=ax.transAxes,
    )
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Saved summary statistics: {output_path}")
    plt.close()


def create_sample_showcase(results: List[Dict], output_path: str, num_samples: int = 6):
    """Create a showcase of vulnerable and safe SQL samples."""
    vulnerable_samples = [r for r in results if r["verdict"] == "VULNERABLE"][:num_samples // 2]
    safe_samples = [r for r in results if r["verdict"] == "NOT VULNERABLE"][:num_samples // 2]
    
    fig, axes = plt.subplots(len(vulnerable_samples) + len(safe_samples), 1, figsize=(14, 12))
    if len(axes.shape) == 0:
        axes = [axes]
    
    idx = 0
    
    # Vulnerable samples
    for sample in vulnerable_samples:
        ax = axes[idx]
        ax.axis("off")
        
        # Title
        title = f"VULNERABLE - {sample['cwe_id']}"
        ax.text(0.02, 0.95, title, fontsize=11, weight="bold", color="white",
                bbox=dict(boxstyle="round", facecolor="#FF6B6B", edgecolor="black", linewidth=2),
                transform=ax.transAxes, verticalalignment="top")
        
        # Prompt
        ax.text(0.02, 0.85, f"Prompt: {sample['original_prompt']}", fontsize=9,
                wrap=True, transform=ax.transAxes, verticalalignment="top")
        
        # SQL code
        sql_text = f"SQL:\n{sample['sql_code'][:150]}..." if len(sample['sql_code']) > 150 else f"SQL:\n{sample['sql_code']}"
        ax.text(0.02, 0.55, sql_text, fontsize=8, family="monospace",
                bbox=dict(boxstyle="round", facecolor="#FFE0E0", alpha=0.5),
                transform=ax.transAxes, verticalalignment="top")
        
        idx += 1
    
    # Safe samples
    for sample in safe_samples:
        ax = axes[idx]
        ax.axis("off")
        
        # Title
        title = f"NOT VULNERABLE"
        ax.text(0.02, 0.95, title, fontsize=11, weight="bold", color="white",
                bbox=dict(boxstyle="round", facecolor="#51CF66", edgecolor="black", linewidth=2),
                transform=ax.transAxes, verticalalignment="top")
        
        # Prompt
        ax.text(0.02, 0.85, f"Prompt: {sample['original_prompt']}", fontsize=9,
                wrap=True, transform=ax.transAxes, verticalalignment="top")
        
        # SQL code
        sql_text = f"SQL:\n{sample['sql_code'][:150]}..." if len(sample['sql_code']) > 150 else f"SQL:\n{sample['sql_code']}"
        ax.text(0.02, 0.55, sql_text, fontsize=8, family="monospace",
                bbox=dict(boxstyle="round", facecolor="#E0FFE0", alpha=0.5),
                transform=ax.transAxes, verticalalignment="top")
        
        idx += 1
    
    plt.suptitle("Sample SQL Code Showcase", fontsize=16, weight="bold", y=0.995)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Saved sample showcase: {output_path}")
    plt.close()


def generate_all_visualizations(json_path: str, output_dir: str = "experiments"):
    """Generate all visualizations from experiment results."""
    print("\n" + "="*60)
    print("GENERATING VISUALIZATIONS")
    print("="*60 + "\n")
    
    # Load results
    results = load_results(json_path)
    
    # Create visualizations
    create_vulnerability_distribution_chart(
        results,
        os.path.join(output_dir, "01_vulnerability_distribution.png")
    )
    
    create_cwe_distribution_chart(
        results,
        os.path.join(output_dir, "02_cwe_distribution.png")
    )
    
    create_summary_statistics_table(
        results,
        os.path.join(output_dir, "03_summary_statistics.png")
    )
    
    create_sample_showcase(
        results,
        os.path.join(output_dir, "04_sample_showcase.png")
    )
    
    print("\n✓ All visualizations generated successfully!")
