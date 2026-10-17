"""Head-on rotation views for |+>; run manually in the project venv."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, Statevector


def rotated_vector(axis, angle):
    circuit = QuantumCircuit(1)
    circuit.h(0)
    getattr(circuit, f"r{axis}")(angle, 0)
    state = Statevector.from_instruction(circuit)
    return np.array([
        float(np.real(state.expectation_value(Pauli(label))))
        for label in "XYZ"
    ])


def main():
    figure, panels = plt.subplots(1, 3, figsize=(13, 5))
    circle = np.linspace(0, 2 * np.pi, 241)
    # Local screen coordinates explicitly labeled in each panel.
    views = [
        ("x", 1, 2, "+Y", "+Z", "Stays at +X", "|+>"),
        ("y", 0, 2, "+X", "+Z", "+X to -Z", "|1>"),
        ("z", 0, 1, "+X", "+Y", "+X to +Y", "(|0> + i|1>)/sqrt(2)"),
    ]
    for panel, (axis, horizontal, vertical, hlabel, vlabel, result, ket) in zip(panels, views):
        panel.plot(np.cos(circle), np.sin(circle), color="lightgray")
        panel.axhline(0, color="lightgray", linewidth=1)
        panel.axvline(0, color="lightgray", linewidth=1)
        panel.text(1.08, 0, hlabel, va="center")
        panel.text(0, 1.12, vlabel, ha="center")
        if axis == "x":
            panel.scatter(0, 0, s=200, facecolors="none", edgecolors="darkorange", linewidths=3, label="Start: +X")
            panel.scatter(0, 0, s=45, color="royalblue", label="End: +X")
            panel.text(0, -0.35, "+X points toward you\nStart and end overlap", ha="center")
        else:
            path = np.array([rotated_vector(axis, angle) for angle in np.linspace(0, np.pi / 2, 101)])
            u, v = path[:, horizontal], path[:, vertical]
            panel.plot(u, v, color="purple", linewidth=3)
            panel.annotate("", xy=(u[65], v[65]), xytext=(u[48], v[48]), arrowprops={"arrowstyle": "->", "color": "purple", "lw": 3})
            panel.scatter(u[0], v[0], s=85, color="darkorange", zorder=4, label="Start: +X")
            panel.scatter(u[-1], v[-1], s=85, color="royalblue", zorder=4, label=f"End: {result.split(' to ')[-1]}")
            panel.annotate("Start", (u[0], v[0]), xytext=(-10, 12), textcoords="offset points", ha="right")
            panel.annotate("End", (u[-1], v[-1]), xytext=(12, 0), textcoords="offset points")
        panel.set_title(f"R{axis.upper()}(pi/2): looking along +{axis.upper()}\n{result}", pad=25)
        panel.set_xlim(-1.35, 1.45)
        panel.set_ylim(-1.4, 1.4)
        panel.set_aspect("equal")
        panel.axis("off")
        panel.legend(loc="lower center", bbox_to_anchor=(0.5, -0.13), frameon=False)
        panel.text(0.5, -0.18, f"Final state: {ket}", transform=panel.transAxes, ha="center", fontsize=10)
    figure.suptitle("Same initial state |+> = +X; three independent 90-degree rotations", fontsize=15)
    figure.subplots_adjust(top=0.77, bottom=0.22, wspace=0.3)
    output = Path(__file__).resolve().parent / "bloch_rotation_output"
    output.mkdir(parents=True, exist_ok=True)
    figure.savefig(output / "rotation_simple_views.png", dpi=180, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
