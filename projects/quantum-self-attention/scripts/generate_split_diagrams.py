from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

figures_dir = Path(__file__).resolve().parents[1] / "figures"
figures_dir.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------
# DIAGRAM 1: DATA ENCODING (U_enc)
# ----------------------------------------------------
fig1, ax1 = plt.subplots(figsize=(16, 5.5), dpi=300)
ax1.set_xlim(0, 16)
ax1.set_ylim(-0.5, 3.2)
ax1.axis("off")
fig1.patch.set_facecolor("#ffffff")

# Title
ax1.text(8.0, 2.9, "Step 1: Data Encoding Block  $U_{enc}(x_s)$", 
         fontsize=16, fontweight='bold', ha='center', va='center', color='#6c3483')
ax1.text(8.0, 2.45,
         r"Illustrative input: 'quantum'  $x_s=[+0.50,-0.20,+0.30,+0.10,-0.40,+0.20]$",
         fontsize=11.5, fontweight='bold', ha='center', va='center', color='#4a148c',
         bbox=dict(boxstyle="round,pad=0.3", fc="#f3e5f5", ec="#8e44ad", lw=1.5))

qubit_y = [1.5, 0.4]
for idx, y in enumerate(qubit_y):
    ax1.plot([0.8, 15.2], [y, y], color='#34495e', lw=2.5, zorder=1)
    ax1.text(0.5, y, rf"$|0\rangle_{{q_{idx}}}$", fontsize=14, fontweight='bold', ha='right', va='center', color='#2c3e50')

# Gates: exactly the order used by quantum_encoder() in qsann_demo.py.
x_vals = ["+0.50", "-0.20", "+0.30", "+0.10", "-0.40", "+0.20"]
for idx, y in enumerate(qubit_y):
    # Hadamard Gate
    h_box = patches.FancyBboxPatch((1.6, y-0.35), 0.9, 0.7, boxstyle="round,pad=0.08",
                                   linewidth=1.8, edgecolor='#2980b9', facecolor='#e1f5fe', zorder=3)
    ax1.add_patch(h_box)
    ax1.text(2.05, y, "H", fontsize=14, fontweight='bold', ha='center', va='center', color='#1b4f72')

    # Initial RX layer: x_0 on q0 and x_1 on q1.
    rx_box = patches.FancyBboxPatch((3.0, y-0.4), 2.2, 0.8, boxstyle="round,pad=0.08",
                                    linewidth=1.8, edgecolor='#8e44ad', facecolor='#ede7f6', zorder=3)
    ax1.add_patch(rx_box)
    ax1.text(4.1, y+0.15, r"$R_X$", fontsize=13, fontweight='bold', ha='center', va='center', color='#4a148c')
    ax1.text(4.1, y-0.16, rf"$x_{idx}={x_vals[idx]}$", fontsize=11, fontweight='bold', ha='center', va='center', color='#6c3483')

    # Initial RY layer: x_2 on q0 and x_3 on q1.
    ry_box = patches.FancyBboxPatch((5.7, y-0.4), 2.2, 0.8, boxstyle="round,pad=0.08",
                                    linewidth=1.8, edgecolor='#8e44ad', facecolor='#ede7f6', zorder=3)
    ax1.add_patch(ry_box)
    ax1.text(6.8, y+0.15, r"$R_Y$", fontsize=13, fontweight='bold', ha='center', va='center', color='#4a148c')
    ax1.text(6.8, y-0.16, rf"$x_{idx + 2}={x_vals[idx + 2]}$", fontsize=11, fontweight='bold', ha='center', va='center', color='#6c3483')

# One CNOT ring for ENCODER_LAYERS=1: 0->1 followed by 1->0.
for x_c, control_idx, target_idx in [(8.8, 0, 1), (9.8, 1, 0)]:
    ax1.plot([x_c, x_c], [qubit_y[0], qubit_y[1]], color='#c0392b', lw=2.5, zorder=3)
    ax1.scatter([x_c], [qubit_y[control_idx]], color='#c0392b', s=90, zorder=4)
    target = patches.Circle((x_c, qubit_y[target_idx]), 0.18, edgecolor='#c0392b', facecolor='#ffffff', lw=2.2, zorder=4)
    ax1.add_patch(target)
    ax1.plot([x_c, x_c], [qubit_y[target_idx]-0.18, qubit_y[target_idx]+0.18], color='#c0392b', lw=2.2, zorder=5)
    ax1.plot([x_c-0.18, x_c+0.18], [qubit_y[target_idx], qubit_y[target_idx]], color='#c0392b', lw=2.2, zorder=5)

# Final encoder RY layer: x_4 on q0 and x_5 on q1.
for idx, y in enumerate(qubit_y):
    ry_box = patches.FancyBboxPatch((10.8, y-0.4), 2.6, 0.8, boxstyle="round,pad=0.08",
                                    linewidth=1.8, edgecolor='#8e44ad', facecolor='#ede7f6', zorder=3)
    ax1.add_patch(ry_box)
    ax1.text(12.1, y+0.15, r"$R_Y$", fontsize=13, fontweight='bold', ha='center', va='center', color='#4a148c')
    ax1.text(12.1, y-0.16, rf"$x_{idx + 4}={x_vals[idx + 4]}$", fontsize=11, fontweight='bold', ha='center', va='center', color='#6c3483')

ax1.text(14.3, 0.95, r"$|\psi_s\rangle$", fontsize=14, fontweight='bold',
         ha='center', va='center', color='#2c3e50')

plt.tight_layout()
path1_loc = figures_dir / "qsann_step1_encoder.png"
fig1.savefig(path1_loc, dpi=300, bbox_inches='tight')
plt.close(fig1)

# ----------------------------------------------------
# DIAGRAM 2: QUERY ANSATZ (U_q) WITH THETA VALUES
# ----------------------------------------------------
fig2, ax2 = plt.subplots(figsize=(12, 6), dpi=300)
ax2.set_xlim(0, 12)
ax2.set_ylim(-0.6, 3.5)
ax2.axis("off")
fig2.patch.set_facecolor("#ffffff")

# Title
ax2.text(6.0, 3.2, r"Step 2: Query PQC Ansatz Block  $U_q(\theta_q)$", 
         fontsize=16, fontweight='bold', ha='center', va='center', color='#d35400')
ax2.text(6.0, 2.7, r"Illustrative trainable values: $\theta_q=[+0.12,-0.45,+0.88,+0.31,-0.15,+0.67]$", 
         fontsize=10.5, fontweight='bold', ha='center', va='center', color='#bf360c',
         bbox=dict(boxstyle="round,pad=0.3", fc="#fff3e0", ec="#d35400", lw=1.5))

qubit_y2 = [1.6, 0.4]
for idx, y in enumerate(qubit_y2):
    ax2.plot([0.5, 11.2], [y, y], color='#34495e', lw=2.5, zorder=1)
    ax2.text(0.2, y, rf"$|\psi_s\rangle_{{q_{idx}}}$", fontsize=14, fontweight='bold', ha='right', va='center', color='#2c3e50')

# Layer 1 Rotations
theta_pairs = [
    [(r"$\theta_0$", "+0.12"), (r"$\theta_2$", "+0.88")],  # Qubit 0
    [(r"$\theta_1$", "-0.45"), (r"$\theta_3$", "+0.31")]   # Qubit 1
]

for idx, y in enumerate(qubit_y2):
    # RX Gate
    t0_name, t0_val = theta_pairs[idx][0]
    rx_box = patches.FancyBboxPatch((1.2, y-0.4), 2.2, 0.8, boxstyle="round,pad=0.08",
                                    linewidth=1.8, edgecolor='#e67e22', facecolor='#ffe0b2', zorder=3)
    ax2.add_patch(rx_box)
    ax2.text(2.3, y+0.15, r"$R_X$", fontsize=12, fontweight='bold', ha='center', va='center', color='#bf360c')
    ax2.text(2.3, y-0.16, f"({t0_name} = {t0_val})", fontsize=11, fontweight='bold', ha='center', va='center', color='#d84315')

    # RY Gate
    t1_name, t1_val = theta_pairs[idx][1]
    ry_box = patches.FancyBboxPatch((3.8, y-0.4), 2.2, 0.8, boxstyle="round,pad=0.08",
                                    linewidth=1.8, edgecolor='#e67e22', facecolor='#ffe0b2', zorder=3)
    ax2.add_patch(ry_box)
    ax2.text(4.9, y+0.15, r"$R_Y$", fontsize=12, fontweight='bold', ha='center', va='center', color='#bf360c')
    ax2.text(4.9, y-0.16, f"({t1_name} = {t1_val})", fontsize=11, fontweight='bold', ha='center', va='center', color='#d84315')

# CNOT Entanglement Ring
x_c1 = 6.7
ax2.plot([x_c1, x_c1], [qubit_y2[0], qubit_y2[1]], color='#c0392b', lw=2.5, zorder=3)
ax2.scatter([x_c1], [qubit_y2[0]], color='#c0392b', s=90, zorder=4)
target1 = patches.Circle((x_c1, qubit_y2[1]), 0.18, edgecolor='#c0392b', facecolor='#ffffff', lw=2.2, zorder=4)
ax2.add_patch(target1)
ax2.plot([x_c1, x_c1], [qubit_y2[1]-0.18, qubit_y2[1]+0.18], color='#c0392b', lw=2.2, zorder=5)
ax2.plot([x_c1-0.18, x_c1+0.18], [qubit_y2[1], qubit_y2[1]], color='#c0392b', lw=2.2, zorder=5)

x_c2 = 7.7
ax2.plot([x_c2, x_c2], [qubit_y2[0], qubit_y2[1]], color='#c0392b', lw=2.5, zorder=3)
ax2.scatter([x_c2], [qubit_y2[1]], color='#c0392b', s=90, zorder=4)
target0 = patches.Circle((x_c2, qubit_y2[0]), 0.18, edgecolor='#c0392b', facecolor='#ffffff', lw=2.2, zorder=4)
ax2.add_patch(target0)
ax2.plot([x_c2, x_c2], [qubit_y2[0]-0.18, qubit_y2[0]+0.18], color='#c0392b', lw=2.2, zorder=5)
ax2.plot([x_c2-0.18, x_c2+0.18], [qubit_y2[0], qubit_y2[0]], color='#c0392b', lw=2.2, zorder=5)

# Layer 2 Rotations
t_l2 = [(r"$\theta_4$", "-0.15"), (r"$\theta_5$", "+0.67")]
for idx, y in enumerate(qubit_y2):
    t_name, t_val = t_l2[idx]
    ry_box = patches.FancyBboxPatch((8.5, y-0.4), 2.2, 0.8, boxstyle="round,pad=0.08",
                                    linewidth=1.8, edgecolor='#e67e22', facecolor='#ffe0b2', zorder=3)
    ax2.add_patch(ry_box)
    ax2.text(9.6, y+0.15, r"$R_Y$", fontsize=12, fontweight='bold', ha='center', va='center', color='#bf360c')
    ax2.text(9.6, y-0.16, f"({t_name} = {t_val})", fontsize=11, fontweight='bold', ha='center', va='center', color='#d84315')

plt.tight_layout()
path2_loc = figures_dir / "qsann_step2_ansatz.png"
fig2.savefig(path2_loc, dpi=300, bbox_inches='tight')
plt.close(fig2)

print("Successfully generated split diagrams!")
