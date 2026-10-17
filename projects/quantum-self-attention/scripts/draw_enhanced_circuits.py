from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_enhanced_query_circuit(filename=None):
    if filename is None:
        filename = Path(__file__).resolve().parents[1] / "figures" / "qsann_circuit_query_enhanced.png"
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(15, 6.5), dpi=300)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(-0.4, 2.6)
    ax.axis("off")

    fig.patch.set_facecolor('#ffffff')

    # Title
    ax.text(7.75, 2.45, "QSANN Query Quantum Circuit  ($U_{enc} + U_q +$ Pauli-Z Measurement)", 
            fontsize=15, fontweight='bold', ha='center', va='center', color='#1a252f')

    # Qubit Wires
    qubit_y = [1.6, 0.5]
    for idx, y in enumerate(qubit_y):
        ax.plot([0.5, 14.2], [y, y], color='#34495e', lw=2, zorder=1)
        ax.text(0.2, y, f"|0⟩_q{idx}", fontsize=13, fontweight='bold', ha='right', va='center', color='#2c3e50')

    # --- 1. DATA ENCODING BLOCK (U_enc) ---
    enc_box = patches.FancyBboxPatch((1.1, -0.15), 3.5, 2.3, boxstyle="round,pad=0.1",
                                     linewidth=1.8, edgecolor='#8e44ad', facecolor='#f3e5f5', linestyle='--', alpha=0.7, zorder=2)
    ax.add_patch(enc_box)
    ax.text(2.85, 2.2, r"Data Encoding Block $U_{enc}(x)$", fontsize=11, fontweight='bold', 
            ha='center', va='center', color='#6c3483', bbox=dict(boxstyle="round,pad=0.25", fc="#ffffff", ec="#8e44ad", lw=1.2))

    # Gates in Encoding Block
    for idx, y in enumerate(qubit_y):
        # Hadamard Gate
        h_box = patches.FancyBboxPatch((1.4, y-0.3), 0.7, 0.6, boxstyle="round,pad=0.05",
                                       linewidth=1.5, edgecolor='#2980b9', facecolor='#e1f5fe', zorder=3)
        ax.add_patch(h_box)
        ax.text(1.75, y, "H", fontsize=12, fontweight='bold', ha='center', va='center', color='#1b4f72')

        # RY(x_i) Gate
        x_text = r"$x_0$" if idx == 0 else r"$x_1$"
        ry_box = patches.FancyBboxPatch((2.5, y-0.35), 1.7, 0.7, boxstyle="round,pad=0.05",
                                        linewidth=1.5, edgecolor='#8e44ad', facecolor='#ede7f6', zorder=3)
        ax.add_patch(ry_box)
        ax.text(3.35, y+0.12, r"$R_Y$", fontsize=12, fontweight='bold', ha='center', va='center', color='#4a148c')
        ax.text(3.35, y-0.14, f"({x_text})", fontsize=11, fontweight='bold', ha='center', va='center', color='#6a1b9a')

    # --- 2. QUERY ANSATZ BLOCK (U_q) ---
    ansatz_box = patches.FancyBboxPatch((5.0, -0.15), 7.3, 2.3, boxstyle="round,pad=0.1",
                                        linewidth=1.8, edgecolor='#d35400', facecolor='#fff3e0', linestyle='--', alpha=0.7, zorder=2)
    ax.add_patch(ansatz_box)
    ax.text(8.65, 2.2, r"Query Ansatz Block $U_q(\theta_q)$", fontsize=11, fontweight='bold', 
            ha='center', va='center', color='#d35400', bbox=dict(boxstyle="round,pad=0.25", fc="#ffffff", ec="#d35400", lw=1.2))

    # Layer 1 Rotations: RX(theta), RY(theta)
    rx_texts = [r"$\theta_0$", r"$\theta_2$"]
    ry_texts = [r"$\theta_1$", r"$\theta_3$"]
    for idx, y in enumerate(qubit_y):
        # RX
        rx_box = patches.FancyBboxPatch((5.3, y-0.35), 1.4, 0.7, boxstyle="round,pad=0.05",
                                        linewidth=1.5, edgecolor='#e67e22', facecolor='#ffe0b2', zorder=3)
        ax.add_patch(rx_box)
        ax.text(6.0, y+0.12, r"$R_X$", fontsize=11, fontweight='bold', ha='center', va='center', color='#bf360c')
        ax.text(6.0, y-0.14, f"({rx_texts[idx]})", fontsize=10, fontweight='bold', ha='center', va='center', color='#d84315')

        # RY
        ry_box = patches.FancyBboxPatch((6.9, y-0.35), 1.4, 0.7, boxstyle="round,pad=0.05",
                                        linewidth=1.5, edgecolor='#e67e22', facecolor='#ffe0b2', zorder=3)
        ax.add_patch(ry_box)
        ax.text(7.6, y+0.12, r"$R_Y$", fontsize=11, fontweight='bold', ha='center', va='center', color='#bf360c')
        ax.text(7.6, y-0.14, f"({ry_texts[idx]})", fontsize=10, fontweight='bold', ha='center', va='center', color='#d84315')

    # Entanglement Ring (CNOT Gates)
    # CNOT 1: Control q0, Target q1
    x_c1 = 8.7
    ax.plot([x_c1, x_c1], [qubit_y[0], qubit_y[1]], color='#c0392b', lw=2.2, zorder=3)
    ax.scatter([x_c1], [qubit_y[0]], color='#c0392b', s=80, zorder=4)
    target1 = patches.Circle((x_c1, qubit_y[1]), 0.16, edgecolor='#c0392b', facecolor='#ffffff', lw=2, zorder=4)
    ax.add_patch(target1)
    ax.plot([x_c1, x_c1], [qubit_y[1]-0.16, qubit_y[1]+0.16], color='#c0392b', lw=2, zorder=5)
    ax.plot([x_c1-0.16, x_c1+0.16], [qubit_y[1], qubit_y[1]], color='#c0392b', lw=2, zorder=5)

    # CNOT 2: Control q1, Target q0
    x_c2 = 9.5
    ax.plot([x_c2, x_c2], [qubit_y[0], qubit_y[1]], color='#c0392b', lw=2.2, zorder=3)
    ax.scatter([x_c2], [qubit_y[1]], color='#c0392b', s=80, zorder=4)
    target0 = patches.Circle((x_c2, qubit_y[0]), 0.16, edgecolor='#c0392b', facecolor='#ffffff', lw=2, zorder=4)
    ax.add_patch(target0)
    ax.plot([x_c2, x_c2], [qubit_y[0]-0.16, qubit_y[0]+0.16], color='#c0392b', lw=2, zorder=5)
    ax.plot([x_c2-0.16, x_c2+0.16], [qubit_y[0], qubit_y[0]], color='#c0392b', lw=2, zorder=5)

    # Layer 2 Rotations: RY(theta_4/5)
    ry2_texts = [r"$\theta_4$", r"$\theta_5$"]
    for idx, y in enumerate(qubit_y):
        ry_box = patches.FancyBboxPatch((10.3, y-0.35), 1.4, 0.7, boxstyle="round,pad=0.05",
                                        linewidth=1.5, edgecolor='#e67e22', facecolor='#ffe0b2', zorder=3)
        ax.add_patch(ry_box)
        ax.text(11.0, y+0.12, r"$R_Y$", fontsize=11, fontweight='bold', ha='center', va='center', color='#bf360c')
        ax.text(11.0, y-0.14, f"({ry2_texts[idx]})", fontsize=10, fontweight='bold', ha='center', va='center', color='#d84315')

    # --- 3. MEASUREMENT BLOCK ---
    meas_box = patches.FancyBboxPatch((12.6, qubit_y[0]-0.38), 1.4, 0.76, boxstyle="round,pad=0.05",
                                       linewidth=2, edgecolor='#27ae60', facecolor='#e8f8f5', zorder=3)
    ax.add_patch(meas_box)
    ax.text(13.3, qubit_y[0]+0.12, "Pauli-Z", fontsize=11, fontweight='bold', ha='center', va='center', color='#145a32')
    ax.text(13.3, qubit_y[0]-0.14, r"$\langle Z_q \rangle_s$", fontsize=11, fontweight='bold', ha='center', va='center', color='#196f3d')

    # Output arrow & Scalar box
    ax.annotate('', xy=(14.5, qubit_y[0]), xytext=(14.0, qubit_y[0]),
                arrowprops=dict(arrowstyle="->", color="#27ae60", lw=2.5))
    ax.text(14.6, qubit_y[0], "Scalar Output\n" + r"$\langle Z_q \rangle_s \in [-1, 1]$", fontsize=10, fontweight='bold', 
            ha='left', va='center', color='#196f3d', bbox=dict(boxstyle="round,pad=0.25", fc="#f4f6f6", ec="#27ae60", lw=1.2))

    # Qubit 1 termination label
    ax.text(12.6, qubit_y[1], "(Unmeasured)", fontsize=9.5, fontstyle='italic', ha='left', va='center', color='#7f8c8d')

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated enhanced circuit diagram: {filename}")

if __name__ == "__main__":
    draw_enhanced_query_circuit()
