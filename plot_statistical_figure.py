import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# =========================
# Input / output
# =========================
input_file = Path(r"/mnt/data/31_method_statistical_analysis.xlsx")
output_file = Path(r"/mnt/data/statistical_summary_figure.png")

# =========================
# Read data
# =========================
summary = pd.read_excel(input_file, sheet_name="Method_Summary")
sig = pd.read_excel(input_file, sheet_name="Significance_Matrix")

# Sort methods by average dataset rank (smaller is better)
summary = summary.sort_values("Average Dataset Rank", ascending=True).reset_index(drop=True)

# Top-10 methods defined by USI rank
top10 = (
    pd.read_excel(input_file, sheet_name="Method_Summary")
    .sort_values("USI Rank", ascending=True)
    .head(10)["Method"]
    .tolist()
)

# Subset significance matrix to top-10 methods
sig_top10 = sig[sig["Method"].isin(top10)].copy()
sig_top10 = sig_top10.set_index("Method").loc[top10, top10]

# Convert the string significance matrix to numeric values
# diagonal = NaN; significant = 1; non-significant = 0
sig_numeric = sig_top10.copy()
for r in sig_numeric.index:
    for c in sig_numeric.columns:
        val = sig_numeric.loc[r, c]
        if val == "—":
            sig_numeric.loc[r, c] = np.nan
        elif isinstance(val, str) and val.strip().upper() == "NS":
            sig_numeric.loc[r, c] = 0
        else:
            # Any non-NS and non-diagonal marker is treated as significant
            sig_numeric.loc[r, c] = 1
sig_numeric = sig_numeric.astype(float)

# =========================
# Create the figure
# =========================
fig, axes = plt.subplots(
    1, 2,
    figsize=(16, 10),
    gridspec_kw={"width_ratios": [1.45, 1]}
)

# ---- Left panel: average rank plot ----
ax = axes[0]
y = np.arange(len(summary))
x = summary["Average Dataset Rank"].values

ax.hlines(y=y, xmin=0, xmax=x)
ax.scatter(x, y)

ax.set_yticks(y)
ax.set_yticklabels(summary["Method"])
ax.invert_yaxis()
ax.set_xlabel("Average rank across 17 datasets (smaller is better)")
ax.set_ylabel("Method")
ax.set_title("Average-rank comparison of 31 methods")
ax.grid(True, axis="x", alpha=0.3)

# Annotate a few useful statistics on the right side
rank_text = [
    f"USI rank {int(r)}"
    for r in summary["USI Rank"]
]
x_max = max(x) * 1.22
for yi, xi, txt in zip(y, x, rank_text):
    ax.text(xi + 0.15, yi, txt, va="center", fontsize=8)

ax.set_xlim(0, x_max)

# ---- Right panel: Top-10 significance matrix ----
ax2 = axes[1]
im = ax2.imshow(sig_numeric.values)

ax2.set_xticks(np.arange(len(top10)))
ax2.set_yticks(np.arange(len(top10)))
ax2.set_xticklabels(top10, rotation=90)
ax2.set_yticklabels(top10)
ax2.set_title("Top-10 Wilcoxon-Holm significance matrix")

# Put text labels inside cells
for i in range(sig_numeric.shape[0]):
    for j in range(sig_numeric.shape[1]):
        val = sig_top10.iloc[i, j]
        display = "" if val == "—" else str(val)
        ax2.text(j, i, display, ha="center", va="center", fontsize=8)

# Add a simple legend text under the matrix
ax2.set_xlabel("NS = not significant after Holm correction")

# Add panel labels
axes[0].text(-0.08, 1.03, "a", transform=axes[0].transAxes, fontsize=14, fontweight="bold")
axes[1].text(-0.12, 1.03, "b", transform=axes[1].transAxes, fontsize=14, fontweight="bold")

plt.tight_layout()
plt.savefig(output_file, dpi=300, bbox_inches="tight")
print(f"Figure saved to: {output_file}")