"""
ECEN 326 Final Project - Deliverable D4: Optimization Convergence Plot
Author: Kyle Tran (cubo1424)
Texas A&M University - ECEN 326
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

csv_path = Path("iteration_log.csv")
if not csv_path.exists():
    raise FileNotFoundError("iteration_log.csv not found in the current working directory.")

df = pd.read_csv(csv_path)

# Enforce numeric types for parsing
numeric_cols = ['Iteration', 'Gain', 'f3dB', 'THD', 'Ptot']
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axs = plt.subplots(2, 2, figsize=(12, 8), dpi=300)
fig.suptitle('ECEN 326: Multi-Agent AI Optimization Convergence (Deliverable D4)', fontsize=15, fontweight='bold', color='#500000')

iters = df['Iteration']

# 1. AC Gain Convergence
ax1 = axs[0, 0]
ax1.plot(iters, df['Gain'], marker='o', color='#500000', linewidth=2, label='Measured Gain ($A_v$)')
ax1.axhline(25.0, color='crimson', linestyle='--', linewidth=1.5, label='Spec Target: $\\geq 25.0$ V/V')
ax1.set_title('Loaded Midband AC Gain ($A_v$) @ 10 kHz', fontweight='bold', fontsize=11)
ax1.set_xlabel('Iteration')
ax1.set_ylabel('Gain (V/V)')
ax1.legend(loc='lower right', frameon=True)
ax1.grid(True, linestyle=':', alpha=0.6)

# 2. 3dB Cutoff Bandwidth
ax2 = axs[0, 1]
f3db_khz = df['f3dB'] / 1000.0
ax2.plot(iters, f3db_khz, marker='s', color='#2B5B84', linewidth=2, label='Cutoff $f_{3dB}$ (kHz)')
ax2.axhline(200.0, color='crimson', linestyle='--', linewidth=1.5, label='Spec Target: $> 200$ kHz')
ax2.set_title('Upper 3 dB Cutoff Bandwidth', fontweight='bold', fontsize=11)
ax2.set_xlabel('Iteration')
ax2.set_ylabel('$f_{3dB}$ (kHz)')
ax2.legend(loc='lower right', frameon=True)
ax2.grid(True, linestyle=':', alpha=0.6)

# 3. Total Harmonic Distortion
ax3 = axs[1, 0]
ax3.plot(iters, df['THD'], marker='^', color='#2E7D32', linewidth=2, label='Measured THD (%)')
ax3.axhline(3.16, color='crimson', linestyle='--', linewidth=1.5, label='Spec Target: $< 3.16\\%$ (-30 dB)')
ax3.set_title('Total Harmonic Distortion (THD) @ 10 kHz, 8 $\\Omega$', fontweight='bold', fontsize=11)
ax3.set_xlabel('Iteration')
ax3.set_ylabel('THD (%)')
ax3.legend(loc='upper right', frameon=True)
ax3.grid(True, linestyle=':', alpha=0.6)

# 4. Total Quiescent Power
ax4 = axs[1, 1]
ax4.plot(iters, df['Ptot'], marker='d', color='#E65100', linewidth=2, label='Total Power $P_{tot}$ (mW)')
ax4.set_title('Total Power Dissipation', fontweight='bold', fontsize=11)
ax4.set_xlabel('Iteration')
ax4.set_ylabel('Power (mW)')
ax4.legend(loc='upper right', frameon=True)
ax4.grid(True, linestyle=':', alpha=0.6)

# Highlight ACCEPT iterations
accepted_rows = df[df['Decision'].str.upper() == 'ACCEPT']
if not accepted_rows.empty:
    for _, row in accepted_rows.iterrows():
        acc_it = row['Iteration']
        for ax in [ax1, ax2, ax3, ax4]:
            ax.axvline(acc_it, color='#4CAF50', linestyle=':', linewidth=2, alpha=0.8, 
                       label='Accepted Candidate' if ax == ax1 and acc_it == accepted_rows['Iteration'].iloc[0] else "")

ax1.legend(loc='lower right', frameon=True)
fig.tight_layout(rect=[0, 0.03, 1, 0.95])

output_dir = Path("results")
output_dir.mkdir(exist_ok=True)
plot_path = output_dir / "convergence_plot.png"
plt.savefig(plot_path, dpi=300)
print(f"Convergence plot saved successfully to: {plot_path}")
plt.show()