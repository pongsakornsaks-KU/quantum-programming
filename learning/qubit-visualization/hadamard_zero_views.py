"""Compare |0> and H|0> in the XZ plane; run manually in the venv."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, Statevector


def main():
    zero_circuit = QuantumCircuit(1)
    hadamard_circuit = QuantumCircuit(1)
    hadamard_circuit.h(0)
    states = [
        Statevector.from_instruction(zero_circuit),
        Statevector.from_instruction(hadamard_circuit),
    ]
    titles = [r"Initial: $|0\rangle$", r"After Hadamard: $H|0\rangle = |+\rangle$"]
    captions = [
        "Bloch vector: (0, 0, 1)\nP(0) = 1, P(1) = 0",
        "Bloch vector: (1, 0, 0)\nP(0) = 1/2, P(1) = 1/2",
    ]
    figure, panels = plt.subplots(1, 2, figsize=(10, 6))
    circle = np.linspace(0, 2 * np.pi, 241)
    for panel, state, title, caption, color in zip(
        panels, states, titles, captions, ["darkorange", "royalblue"]
    ):
        vector = np.array([
            float(np.real(state.expectation_value(Pauli(label))))
            for label in "XYZ"
        ])
        panel.plot(np.cos(circle), np.sin(circle), color="lightgray", linewidth=2)
        panel.axhline(0, color="lightgray", linewidth=1)
        panel.axvline(0, color="lightgray", linewidth=1)
        panel.text(0, 1.12, r"$+Z: |0\rangle$", ha="center")
        panel.text(0, -1.18, r"$-Z: |1\rangle$", ha="center")
        panel.text(1.07, 0, r"$+X: |+\rangle$", va="center", fontsize=10)
        panel.text(-1.07, 0, r"$-X: |-\rangle$", va="center", ha="right", fontsize=10)
        panel.annotate(
            "", xy=(vector[0], vector[2]), xytext=(0, 0),
            arrowprops={"arrowstyle": "->", "color": color, "lw": 4},
        )
        panel.scatter(vector[0], vector[2], color=color, s=65, zorder=4)
        panel.set_title(title, fontsize=15, pad=22)
        panel.set_xlim(-1.65, 1.65)
        panel.set_ylim(-1.4, 1.4)
        panel.set_aspect("equal")
        panel.axis("off")
        panel.text(0.5, -0.08, caption, transform=panel.transAxes, ha="center", fontsize=12)
    figure.suptitle("Same qubit before and after H (XZ view)", fontsize=17)
    figure.text(
        0.5, 0.05,
        r"$H|0\rangle = (|0\rangle + |1\rangle)/\sqrt{2}$"
        "\nArrows show the Bloch state direction; probabilities refer to Z-basis measurement.",
        ha="center", fontsize=11,
    )
    figure.subplots_adjust(top=0.78, bottom=0.23, wspace=0.25)
    output = Path(__file__).resolve().parent / "bloch_rotation_output"
    output.mkdir(parents=True, exist_ok=True)
    destination = output / "hadamard_zero_views.png"
    figure.savefig(destination, dpi=180, bbox_inches="tight")
    print(f"Saved: {destination}")
    plt.show()


if __name__ == "__main__":
    main()
