from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

figures_dir = Path(__file__).resolve().parents[1] / "figures"
figures_dir.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------
# DIAGRAM 3: MEASUREMENT BLOCK (Pauli-Z on Qubit 0)
# ----------------------------------------------------
fig3, ax3 = plt.subplots(figsize=(11, 5.5), dpi=300)
ax3.set_xlim(0, 11)
ax3.set_ylim(-0.6, 3.2)
ax3.axis("off")
fig3.patch.set_facecolor("#ffffff")

# Title
ax3.text(5.5, 2.9, r"Step 3: Query Measurement  $\langle Z_0\rangle_s$", 
         fontsize=16, fontweight='bold', ha='center', va='center', color='#145a32')
ax3.text(5.5, 2.4, r"Query output: one scalar $\langle Z_0\rangle_s\in[-1,1]$ for the Gaussian distance kernel", 
         fontsize=11.5, fontweight='bold', ha='center', va='center', color='#196f3d',
         bbox=dict(boxstyle="round,pad=0.3", fc="#e8f8f5", ec="#27ae60", lw=1.5))

qubit_y3 = [1.5, 0.4]

# Wires
ax3.plot([0.8, 5.0], [qubit_y3[0], qubit_y3[0]], color='#34495e', lw=2.5, zorder=1)
ax3.plot([0.8, 8.5], [qubit_y3[1], qubit_y3[1]], color='#34495e', lw=2.5, zorder=1, linestyle="--")

ax3.text(0.5, qubit_y3[0], r"$|\psi_{q,s}\rangle_{q_0}$", fontsize=13, fontweight='bold', ha='right', va='center', color='#2c3e50')
ax3.text(0.5, qubit_y3[1], r"$|\psi_{q,s}\rangle_{q_1}$", fontsize=13, fontweight='bold', ha='right', va='center', color='#7f8c8d')

# Pauli-Z Measurement Box on Qubit 0
meas_box = patches.FancyBboxPatch((5.0, qubit_y3[0]-0.4), 2.2, 0.8, boxstyle="round,pad=0.08",
                                   linewidth=2.0, edgecolor='#27ae60', facecolor='#e8f8f5', zorder=3)
ax3.add_patch(meas_box)
ax3.text(6.1, qubit_y3[0]+0.15, "Pauli-Z Meter", fontsize=12, fontweight='bold', ha='center', va='center', color='#145a32')
ax3.text(6.1, qubit_y3[0]-0.16, "Measurement", fontsize=11, fontweight='bold', ha='center', va='center', color='#196f3d')

# Output Arrow & Result
ax3.annotate('', xy=(8.8, qubit_y3[0]), xytext=(7.2, qubit_y3[0]),
            arrowprops=dict(arrowstyle="->", color="#27ae60", lw=2.5))
ax3.text(9.0, qubit_y3[0], "Illustrative output:\n$\\langle Z_0 \\rangle_s = +0.412$", fontsize=12, fontweight='bold', 
        ha='left', va='center', color='#145a32', bbox=dict(boxstyle="round,pad=0.25", fc="#f4f6f6", ec="#27ae60", lw=1.5))

# Qubit 1 label
ax3.text(8.7, qubit_y3[1], "(q1 is not directly measured in the query circuit)", 
         fontsize=10.5, fontstyle='italic', ha='left', va='center', color='#7f8c8d')

plt.tight_layout()
path3_loc = figures_dir / "qsann_step3_measurement.png"
fig3.savefig(path3_loc, dpi=300, bbox_inches='tight')
plt.close(fig3)

print("Successfully generated Step 3 measurement diagram!")
