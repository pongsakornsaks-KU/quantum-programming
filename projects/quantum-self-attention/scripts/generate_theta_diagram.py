from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

figures_dir = Path(__file__).resolve().parents[1] / "figures"
figures_dir.mkdir(parents=True, exist_ok=True)
out_path_local = figures_dir / "qsann_theta_circuit_example.png"

fig, ax = plt.subplots(figsize=(20, 8.5), dpi=300)
ax.set_xlim(0, 20)
ax.set_ylim(-1.6, 3.8)
ax.axis("off")
fig.patch.set_facecolor("#ffffff")

# Main Title
ax.text(10.0, 3.5, "Illustrative Input and Theta Values in the QSANN Query Circuit", 
        fontsize=15, fontweight='bold', ha='center', va='center', color='#1a252f')

# --- TOP PANEL: PARAMETER & DATA VECTOR TABLES ---
# 1. Input Word Embedding Box
box_x = patches.FancyBboxPatch((0.5, 2.2), 8.2, 0.95, boxstyle="round,pad=0.1",
                               linewidth=1.8, edgecolor='#8e44ad', facecolor='#f3e5f5')
ax.add_patch(box_x)
ax.text(4.6, 2.85, "1. Illustrative Word Embedding $x_s$ [Data - Fixed]", fontsize=11, fontweight='bold',
        ha='center', va='center', color='#6c3483')
ax.text(4.6, 2.45, r"$x_s=[+0.50,-0.20,+0.30,+0.10,-0.40,+0.20]$  (word: 'quantum')", fontsize=10,
        fontweight='bold', ha='center', va='center', color='#4a148c')

# 2. Theta_q Parameter Vector Box
box_theta = patches.FancyBboxPatch((9.2, 2.1), 10.2, 1.15, boxstyle="round,pad=0.1",
                                   linewidth=1.8, edgecolor='#d35400', facecolor='#fff3e0')
ax.add_patch(box_theta)
ax.text(14.3, 2.9, r"2. Illustrative Query Parameters ($\theta_q$) [Trainable Weights]", fontsize=11, fontweight='bold',
        ha='center', va='center', color='#d35400')
ax.text(14.3, 2.55, r"$\theta_q$ = [ $\theta_0$=+0.12,  $\theta_1$=-0.45,  $\theta_2$=+0.88,  $\theta_3$=+0.31,  $\theta_4$=-0.15,  $\theta_5$=+0.67 ]", fontsize=9.5,
        fontweight='bold', ha='center', va='center', color='#bf360c')
ax.text(14.3, 2.28, "(Example only; actual values are initialized randomly and optimized during training)", fontsize=8.5,
        fontstyle='italic', ha='center', va='center', color='#842b00')

# Qubit Wires
qubit_y = [1.2, -0.2]
for idx, y in enumerate(qubit_y):
    ax.plot([0.5, 18.5], [y, y], color='#34495e', lw=2.2, zorder=1)
    ax.text(0.2, y, rf"$|0\rangle_{{q_{idx}}}$", fontsize=13, fontweight='bold', ha='right', va='center', color='#2c3e50')

# --- SECTION A: DATA ENCODING BLOCK (U_enc) ---
enc_box = patches.FancyBboxPatch((0.9, -0.8), 7.2, 2.4, boxstyle="round,pad=0.1",
                                 linewidth=1.8, edgecolor='#8e44ad', facecolor='#f3e5f5', linestyle='--', alpha=0.6, zorder=2)
ax.add_patch(enc_box)
ax.text(4.5, 1.35, r"Data Encoder $U_{enc}(x_s)$", fontsize=11, fontweight='bold', 
        ha='center', va='center', color='#6c3483', bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#8e44ad", lw=1.2))

# Gates in Encoding Block
x_vals = ["+0.50", "-0.20", "+0.30", "+0.10", "-0.40", "+0.20"]
for idx, y in enumerate(qubit_y):
    # Hadamard Gate
    h_box = patches.FancyBboxPatch((1.1, y-0.35), 0.7, 0.7, boxstyle="round,pad=0.05",
                                   linewidth=1.5, edgecolor='#2980b9', facecolor='#e1f5fe', zorder=3)
    ax.add_patch(h_box)
    ax.text(1.45, y, "H", fontsize=13, fontweight='bold', ha='center', va='center', color='#1b4f72')

    # RX(x_0/x_1) Gate
    rx_box = patches.FancyBboxPatch((2.0, y-0.4), 1.4, 0.8, boxstyle="round,pad=0.05",
                                    linewidth=1.5, edgecolor='#8e44ad', facecolor='#ede7f6', zorder=3)
    ax.add_patch(rx_box)
    ax.text(2.7, y+0.15, r"$R_X$", fontsize=11, fontweight='bold', ha='center', va='center', color='#4a148c')
    ax.text(2.7, y-0.15, rf"$x_{idx}={x_vals[idx]}$", fontsize=8.8, fontweight='bold', ha='center', va='center', color='#6c3483')

    # RY(x_2/x_3) Gate
    ry_box = patches.FancyBboxPatch((3.6, y-0.4), 1.4, 0.8, boxstyle="round,pad=0.05",
                                    linewidth=1.5, edgecolor='#8e44ad', facecolor='#ede7f6', zorder=3)
    ax.add_patch(ry_box)
    ax.text(4.3, y+0.15, r"$R_Y$", fontsize=11, fontweight='bold', ha='center', va='center', color='#4a148c')
    ax.text(4.3, y-0.15, rf"$x_{idx + 2}={x_vals[idx + 2]}$", fontsize=8.8, fontweight='bold', ha='center', va='center', color='#6c3483')

# Encoder CNOT ring: 0->1, then 1->0.
for x_c, control_idx, target_idx in [(5.35, 0, 1), (6.0, 1, 0)]:
    ax.plot([x_c, x_c], [qubit_y[0], qubit_y[1]], color='#8e44ad', lw=2.0, zorder=3)
    ax.scatter([x_c], [qubit_y[control_idx]], color='#8e44ad', s=70, zorder=4)
    target = patches.Circle((x_c, qubit_y[target_idx]), 0.15, edgecolor='#8e44ad', facecolor='#ffffff', lw=1.8, zorder=4)
    ax.add_patch(target)
    ax.plot([x_c, x_c], [qubit_y[target_idx]-0.15, qubit_y[target_idx]+0.15], color='#8e44ad', lw=1.8, zorder=5)
    ax.plot([x_c-0.15, x_c+0.15], [qubit_y[target_idx], qubit_y[target_idx]], color='#8e44ad', lw=1.8, zorder=5)

# Encoder's repeated-block RY layer: x_4 on q0 and x_5 on q1.
for idx, y in enumerate(qubit_y):
    ry_box = patches.FancyBboxPatch((6.35, y-0.4), 1.4, 0.8, boxstyle="round,pad=0.05",
                                    linewidth=1.5, edgecolor='#8e44ad', facecolor='#ede7f6', zorder=3)
    ax.add_patch(ry_box)
    ax.text(7.05, y+0.15, r"$R_Y$", fontsize=11, fontweight='bold', ha='center', va='center', color='#4a148c')
    ax.text(7.05, y-0.15, rf"$x_{idx + 4}={x_vals[idx + 4]}$", fontsize=8.8, fontweight='bold', ha='center', va='center', color='#6c3483')

# --- SECTION B: ANSATZ BLOCK U_q(theta_q) ---
ansatz_box = patches.FancyBboxPatch((8.4, -0.8), 7.9, 2.4, boxstyle="round,pad=0.1",
                                    linewidth=1.8, edgecolor='#d35400', facecolor='#fff3e0', linestyle='--', alpha=0.6, zorder=2)
ax.add_patch(ansatz_box)
ax.text(12.35, 1.35, r"Query PQC Ansatz $U_q(\theta_q)$", fontsize=11, fontweight='bold', 
        ha='center', va='center', color='#d35400', bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#d35400", lw=1.2))

# Layer 1 Rotations: RX(theta), RY(theta)
theta_labels = [
    [(r"$\theta_0$", "+0.12"), (r"$\theta_2$", "+0.88")],  # Qubit 0
    [(r"$\theta_1$", "-0.45"), (r"$\theta_3$", "+0.31")]   # Qubit 1
]

for idx, y in enumerate(qubit_y):
    # RX
    t_name, t_val = theta_labels[idx][0]
    rx_box = patches.FancyBboxPatch((8.7, y-0.4), 1.7, 0.8, boxstyle="round,pad=0.05",
                                    linewidth=1.5, edgecolor='#e67e22', facecolor='#ffe0b2', zorder=3)
    ax.add_patch(rx_box)
    ax.text(9.55, y+0.15, r"$R_X$", fontsize=11, fontweight='bold', ha='center', va='center', color='#bf360c')
    ax.text(9.55, y-0.15, f"({t_name} = {t_val})", fontsize=9.2, fontweight='bold', ha='center', va='center', color='#d84315')

    # RY
    t_name2, t_val2 = theta_labels[idx][1]
    ry_box = patches.FancyBboxPatch((10.6, y-0.4), 1.7, 0.8, boxstyle="round,pad=0.05",
                                    linewidth=1.5, edgecolor='#e67e22', facecolor='#ffe0b2', zorder=3)
    ax.add_patch(ry_box)
    ax.text(11.45, y+0.15, r"$R_Y$", fontsize=11, fontweight='bold', ha='center', va='center', color='#bf360c')
    ax.text(11.45, y-0.15, f"({t_name2} = {t_val2})", fontsize=9.2, fontweight='bold', ha='center', va='center', color='#d84315')

# CNOT Ring
x_c1 = 12.7
ax.plot([x_c1, x_c1], [qubit_y[0], qubit_y[1]], color='#c0392b', lw=2.2, zorder=3)
ax.scatter([x_c1], [qubit_y[0]], color='#c0392b', s=80, zorder=4)
target1 = patches.Circle((x_c1, qubit_y[1]), 0.16, edgecolor='#c0392b', facecolor='#ffffff', lw=2, zorder=4)
ax.add_patch(target1)
ax.plot([x_c1, x_c1], [qubit_y[1]-0.16, qubit_y[1]+0.16], color='#c0392b', lw=2, zorder=5)
ax.plot([x_c1-0.16, x_c1+0.16], [qubit_y[1], qubit_y[1]], color='#c0392b', lw=2, zorder=5)

x_c2 = 13.5
ax.plot([x_c2, x_c2], [qubit_y[0], qubit_y[1]], color='#c0392b', lw=2.2, zorder=3)
ax.scatter([x_c2], [qubit_y[1]], color='#c0392b', s=80, zorder=4)
target0 = patches.Circle((x_c2, qubit_y[0]), 0.16, edgecolor='#c0392b', facecolor='#ffffff', lw=2, zorder=4)
ax.add_patch(target0)
ax.plot([x_c2, x_c2], [qubit_y[0]-0.16, qubit_y[0]+0.16], color='#c0392b', lw=2, zorder=5)
ax.plot([x_c2-0.16, x_c2+0.16], [qubit_y[0], qubit_y[0]], color='#c0392b', lw=2, zorder=5)

# Layer 2 Rotations: RY(theta_4/5)
t_l2 = [(r"$\theta_4$", "-0.15"), (r"$\theta_5$", "+0.67")]
for idx, y in enumerate(qubit_y):
    t_name, t_val = t_l2[idx]
    ry_box = patches.FancyBboxPatch((14.0, y-0.4), 1.7, 0.8, boxstyle="round,pad=0.05",
                                    linewidth=1.5, edgecolor='#e67e22', facecolor='#ffe0b2', zorder=3)
    ax.add_patch(ry_box)
    ax.text(14.85, y+0.15, r"$R_Y$", fontsize=11, fontweight='bold', ha='center', va='center', color='#bf360c')
    ax.text(14.85, y-0.15, f"({t_name} = {t_val})", fontsize=9.2, fontweight='bold', ha='center', va='center', color='#d84315')

# --- SECTION C: MEASUREMENT BLOCK ---
meas_box = patches.FancyBboxPatch((16.7, qubit_y[0]-0.4), 1.6, 0.8, boxstyle="round,pad=0.05",
                                   linewidth=2, edgecolor='#27ae60', facecolor='#e8f8f5', zorder=3)
ax.add_patch(meas_box)
ax.text(17.5, qubit_y[0]+0.15, "Pauli-Z", fontsize=11, fontweight='bold', ha='center', va='center', color='#145a32')
ax.text(17.5, qubit_y[0]-0.15, r"$\langle Z_0 \rangle_s$", fontsize=11, fontweight='bold', ha='center', va='center', color='#196f3d')

# Output Arrow & Label
ax.annotate('', xy=(18.8, qubit_y[0]), xytext=(18.3, qubit_y[0]),
            arrowprops=dict(arrowstyle="->", color="#27ae60", lw=2.5))
ax.text(18.9, qubit_y[0], "Illustrative output\n" + r"$\langle Z_0 \rangle_s = +0.412$", fontsize=9.5, fontweight='bold', 
        ha='left', va='center', color='#196f3d', bbox=dict(boxstyle="round,pad=0.25", fc="#f4f6f6", ec="#27ae60", lw=1.2))

# Bottom Explanatory Legend
ax.text(10.0, -1.3, "Query path used in qsann_demo.py:\n6D input data prepares |ψ_s⟩; six trainable angles then produce one query expectation value.", 
        fontsize=10.5, fontweight='bold', ha='center', va='center', color='#2c3e50',
        bbox=dict(boxstyle="round,pad=0.3", fc="#eef2f7", ec="#b0bec5", lw=1.5))

plt.tight_layout()
fig.savefig(out_path_local, dpi=300, bbox_inches='tight')
plt.close()
print("Successfully generated diagram:", out_path_local)
