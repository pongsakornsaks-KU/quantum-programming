"""Compare independent RX, RY, RZ rotations of one initial qubit.

Run with the project's virtual environment. Requires qiskit, numpy,
and matplotlib. Saves three PNGs beside this script and opens the plots.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, Statevector
from qiskit.visualization import plot_bloch_vector


THETA = np.pi / 2
# This pure state has Bloch vector (1, 1, 1) / sqrt(3).
POLAR_ANGLE = np.arccos(1 / np.sqrt(3))
AZIMUTH = np.pi / 4


def initial_state():
    preparation = QuantumCircuit(1)
    preparation.ry(POLAR_ANGLE, 0)
    preparation.rz(AZIMUTH, 0)
    return Statevector.from_instruction(preparation)


def rotate(state, axis, angle):
    circuit = QuantumCircuit(1)
    getattr(circuit, f"r{axis}")(angle, 0)
    return state.evolve(circuit)


def bloch_vector(state):
    return np.array([
        float(np.real(state.expectation_value(Pauli(axis))))
        for axis in "XYZ"
    ])


def main():
    state = initial_state()
    start = bloch_vector(state)
    output_directory = Path(__file__).resolve().parent / "bloch_rotation_output"
    output_directory.mkdir(parents=True, exist_ok=True)
    print("Initial state amplitudes:", state.data)
    print("Initial Bloch vector:", start)
    print("Each gate acts independently on this same initial state.")

    for axis in "xyz":
        final_state = rotate(state, axis, THETA)
        end = bloch_vector(final_state)
        trajectory = np.array([
            bloch_vector(rotate(state, axis, angle))
            for angle in np.linspace(0, THETA, 101)
        ])

        figure = plt.figure(figsize=(8, 7))
        axes = figure.add_subplot(111, projection="3d")
        plot_bloch_vector(
            end.tolist(), ax=axes,
            title=rf"$R_{axis.upper()}(\pi/2)$ on the same initial state",
        )
        # Qiskit's Bloch renderer maps physical (x, y, z) to plot (y, -x, z).
        axes.quiver(
            0, 0, 0, start[1], -start[0], start[2],
            color="darkorange", linewidth=2.5, arrow_length_ratio=0.12,
        )
        axes.plot(
            trajectory[:, 1], -trajectory[:, 0], trajectory[:, 2],
            color="purple", linewidth=2,
        )
        axes.scatter(
            [end[1]], [-end[0]], [end[2]], color="blue", s=45,
        )
        axes.plot([], [], [], color="darkorange", label="Initial state")
        axes.plot([], [], [], color="blue", label="Final state")
        axes.plot([], [], [], color="purple", label="Rotation path")
        axes.legend(loc="upper left")
        figure.text(
            0.5, 0.04,
            f"Initial (x,y,z): {np.round(start, 3)}\n"
            f"Final (x,y,z):   {np.round(end, 3)}",
            ha="center", fontsize=11,
        )
        destination = output_directory / f"bloch_r{axis}.png"
        figure.savefig(destination, dpi=180, bbox_inches="tight")
        print(f"R{axis.upper()}: amplitudes={final_state.data}")
        print(f"  Bloch vector={end}; saved to {destination}")

    plt.show()


if __name__ == "__main__":
    main()
