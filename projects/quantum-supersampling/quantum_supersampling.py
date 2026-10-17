"""Estimate pixel brightness with QPE on a 16-state Grover operator.

Read build_phase_oracle, build_grover_operator, build_counting_circuit,
and counter_distribution for the quantum pipeline. The CLI is in main.

Each pixel uses a boolean mask of shape (4, 4), where True marks white.
Subpixel positions use x = 4 * row + col, so mask[1, 2] maps to |0110>.
Four subpixel qubits represent the 16 positions; counter_bits qubits run QPE.

For M white subpixels, a = M/16 = sin(theta)**2. Q = D O has eigenvalues
exp(+/-2j*theta), so QPE estimates theta/pi or 1-theta/pi.
Folding combines the two phase branches, and calibration decodes the count.

image_tiles prepares the bitmap classically. reconstruct samples finite shots
from statevector probabilities for each pixel. This dense simulation does
not establish a quantum speedup.
"""

import argparse
import json
from pathlib import Path
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
from PIL import Image, ImageOps
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit.library import QFTGate, UnitaryGate
from qiskit.quantum_info import Statevector


BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6],
                  [3, 11, 1, 9], [15, 7, 13, 5]])


def build_phase_oracle(mask):
    """Return the 16 by 16 phase oracle for a 4 by 4 white-subpixel mask.

    O|x> = (-1)**mask[row, col] |x>. Flattening in row order maps each
    matrix index to x = 4 * row + col.
    """
    phase_signs = 1.0 - 2.0 * mask.ravel()
    return np.diag(phase_signs)


def build_diffusion_operator():
    """Return D = 2|s><s| - I for uniform |s> over the 16 basis states."""
    return np.full((16, 16), 2 / 16) - np.eye(16)


def build_grover_operator(mask):
    """Return Q = D @ O, which applies the oracle before diffusion.

    For |s> = (1/4) sum_x |x>, every entry of 2|s><s| is 2/16.
    Preserve the sign of D = 2|s><s| - I. A global phase on Q becomes
    a relative phase in controlled-Q and changes the QPE readout.
    """
    diffusion = build_diffusion_operator()
    oracle = build_phase_oracle(mask)
    return diffusion @ oracle


def build_counting_circuit(mask, counter_bits):
    """Build the unmeasured QPE circuit for statevector simulation.

    counter[j] controls Q**(2**j). Hadamard gates prepare |s> on subpixel.
    Counter qubits occupy indices 0 through counter_bits - 1, followed
    by the subpixel qubits. The first qarg is the least significant bit
    in Qiskit's matrix ordering. The inverse QFT converts the accumulated
    counter phases into a distribution over readout values y.
    """
    counter = QuantumRegister(counter_bits, "counter")
    subpixel = QuantumRegister(4, "subpixel")
    circuit = QuantumCircuit(counter, subpixel, name="Quantum counting")
    circuit.h(counter)
    circuit.h(subpixel)

    grover_power = build_grover_operator(mask)
    for counter_bit in range(counter_bits):
        exponent = 2 ** counter_bit
        # The control is the first qarg, so odd indices select control = 1.
        controlled_grover = np.eye(32, dtype=complex)
        controlled_grover[1::2, 1::2] = grover_power
        gate = UnitaryGate(controlled_grover, label=f"c-Q^{exponent}")
        circuit.append(gate, [counter[counter_bit], *subpixel])
        # Squaring gives the next controlled power without restarting from Q.
        grover_power = grover_power @ grover_power

    circuit.append(QFTGate(counter_bits).inverse(), counter)
    return circuit


def counter_distribution(mask, counter_bits):
    """Return the 2**counter_bits probabilities P(y) of the QPE counter.

    Statevector computes probabilities before shot sampling. Restricting
    qargs to the counter sums probabilities over all subpixel states.
    """
    circuit = build_counting_circuit(mask, counter_bits)
    probabilities = Statevector.from_instruction(circuit).probabilities(
        qargs=list(range(counter_bits)))
    return probabilities / probabilities.sum()


def folded(probabilities):
    """Combine P(y) and P(N-y), whose phase branches give the same brightness.

    The input has N = 2**counter_bits entries; the result has N/2 + 1.
    The endpoints y = 0 and y = N/2 have no distinct partner.
    """
    outcome_count = len(probabilities)
    midpoint = outcome_count // 2
    folded_probabilities = probabilities[:midpoint + 1].copy()
    folded_probabilities[1:-1] += probabilities[:midpoint:-1]
    return folded_probabilities


def calibration(counter_bits):
    """Return distributions, folded peaks, and a count lookup for M = 0..16.

    One mask per M suffices because the distribution depends on the white
    count. self_test checks this with spatial permutations of the masks.
    The phase relation gives M approximately 16*sin(pi*y/2**counter_bits)**2.
    For each folded outcome, lookup selects M with the nearest folded peak.
    """
    distributions = []
    for white_count in range(17):
        mask = (np.arange(16) < white_count).reshape(4, 4)
        distributions.append(counter_distribution(mask, counter_bits))
    peaks = np.array([np.argmax(folded(distribution)) for distribution in distributions])
    if len(np.unique(peaks)) != 17:
        raise ValueError("Use at least 6 counter bits to distinguish all 17 shades.")
    folded_outcomes = np.arange(2 ** (counter_bits - 1) + 1)
    # Broadcast folded outcomes against all 17 calibration peaks.
    distance_to_each_peak = abs(folded_outcomes[:, None] - peaks[None, :])
    lookup = np.argmin(distance_to_each_peak, axis=1)
    return distributions, peaks, lookup


def self_test(counter_bits, distributions, peaks, lookup):
    """Check decoding, normalization, and invariance under mask permutations."""
    rng = np.random.default_rng(21)
    max_error = 0.0
    for count, expected in enumerate(distributions):
        assert lookup[np.argmax(folded(expected))] == count
        decoded = np.sin(np.pi * peaks[count] / (2 ** counter_bits)) ** 2
        assert round(16 * decoded) == count, (count, decoded)
        mask = rng.permutation(np.arange(16) < count).reshape(4, 4)
        actual = counter_distribution(mask, counter_bits)
        error = float(np.max(abs(actual - expected)))
        max_error = max(max_error, error)
        assert error < 1e-10, (count, error)
        assert abs(float(actual.sum()) - 1) < 1e-12
    assert peaks[0] == 0 and peaks[16] == 2 ** (counter_bits - 1)
    return {"counts_checked": 17, "permuted_masks_checked": 17,
            "max_probability_error_after_permutation": max_error}


def image_tiles(source, size):
    """Return a boolean array of 4 by 4 subpixel masks.

    The shape is (size, size, 4, 4). Classical Bayer dithering converts
    grayscale samples to white or black before oracle construction.
    """
    gray = source.convert("L").resize((size * 4, size * 4), Image.Resampling.NEAREST)
    values = np.asarray(gray, dtype=float) / 255
    thresholds = np.tile((BAYER + 0.5) / 16, (size, size))
    white = values >= thresholds
    return white.reshape(size, 4, size, 4).transpose(0, 2, 1, 3)


def reconstruct(tiles, counter_bits, shots, lookup, seed):
    """Return shot-based brightness, exact-mode brightness, and the mask count.

    Both images have shape (size, size). The most frequent folded outcome
    decodes through lookup to a white count M, giving brightness M/16.
    Identical masks share a cached distribution to avoid repeated simulation.
    """
    rng = np.random.default_rng(seed)
    measured = np.empty(tiles.shape[:2], dtype=float)
    diagnostic = np.empty_like(measured)
    distribution_by_mask = {}
    for row in range(len(tiles)):
        for col in range(len(tiles)):
            mask = tiles[row, col]
            mask_key = mask.tobytes()
            if mask_key not in distribution_by_mask:
                distribution_by_mask[mask_key] = folded(counter_distribution(mask, counter_bits))
            probabilities = distribution_by_mask[mask_key]
            shot_counts = rng.multinomial(shots, probabilities / probabilities.sum())
            most_frequent_outcome = np.argmax(shot_counts)
            exact_mode_outcome = np.argmax(probabilities)
            measured[row, col] = lookup[most_frequent_outcome] / 16
            diagnostic[row, col] = lookup[exact_mode_outcome] / 16
        if (row + 1) % 32 == 0 or row + 1 == len(tiles):
            print(f"Rendered {row + 1}/{len(tiles)} rows; {len(distribution_by_mask)} unique oracles", flush=True)
    return measured, diagnostic, len(distribution_by_mask)


def save_gray(values, destination):
    image = Image.fromarray(np.rint(np.clip(values, 0, 1) * 255).astype("uint8"))
    image.save(destination)
    return image


def comparison(source, tiles, measured, output):
    figure, panels = plt.subplots(1, 4, figsize=(16, 4.8))
    single = source.convert("L").resize(measured.shape[::-1], Image.Resampling.NEAREST)
    images = [source, np.asarray(single) / 255,
              tiles.mean(axis=(2, 3)), measured]
    titles = ["Original reference", "Single sample / pixel", "Classical 16 samples / pixel",
              "Quantum supersampling\nfinite-shot QPE estimate"]
    for panel, image, title in zip(panels, images, titles):
        panel.imshow(image, cmap="gray", vmin=0, vmax=1, interpolation="nearest")
        panel.set_title(title, fontsize=11)
        panel.axis("off")
    figure.text(0.5, 0.04, "Bitmap preparation and Bayer dithering are classical. Qiskit estimates each tile's white fraction.\n"
                "Dense statevector simulation and repeated-mask caching demonstrate the algorithm; they do not demonstrate a speedup.",
                ha="center", fontsize=10)
    figure.subplots_adjust(bottom=0.20, top=0.87, wspace=0.06)
    figure.savefig(output / "comparison.png", dpi=160)
    plt.close(figure)


def circle_notation(tiles, measured, output):
    """Draw a selected pixel's oracle state and return its mask metadata."""
    size = len(tiles)
    candidates = np.argwhere((tiles.mean(axis=(2, 3)) > 0.25) &
                             (tiles.mean(axis=(2, 3)) < 0.75))
    row, col = (min(candidates, key=lambda rc: np.sum((rc - size / 2) ** 2))
                if len(candidates) else (size // 2, size // 2))
    mask = tiles[row, col]
    circuit = QuantumCircuit(4)
    circuit.h(range(4))
    circuit.append(UnitaryGate(build_phase_oracle(mask), label="O"), range(4))
    state = Statevector.from_instruction(circuit)
    figure, (overview, detail) = plt.subplots(1, 2, figsize=(13, 7))
    yy, xx = np.indices(measured.shape)
    overview.scatter(xx.ravel(), yy.ravel(), c=measured.ravel(), cmap="gray", vmin=0,
                     vmax=1, s=7, edgecolors="none")
    overview.scatter([col], [row], s=80, facecolors="none", edgecolors="red", linewidths=1)
    overview.set(xlim=(-1, size), ylim=(size, -1), aspect="equal")
    overview.set_title("Reconstructed pixels as circles\nClassical display of measured brightness", fontsize=12)
    overview.axis("off")
    for index, amplitude in enumerate(state.data):
        y, x = divmod(index, 4)
        phase = np.angle(amplitude)
        color = "white" if mask[y, x] else "#454545"
        radius = 0.32
        detail.add_patch(Circle((x, -y), radius, facecolor=color, edgecolor="black"))
        detail.plot([x, x + radius * np.sin(phase)], [-y, -y + radius * np.cos(phase)],
                    color="#d94801", linewidth=2.3)
        detail.text(x, -y - 0.47, f"|{index:04b}>", ha="center", fontsize=10)
    detail.set(xlim=(-0.7, 3.7), ylim=(-3.9, 0.65), aspect="equal")
    detail.set_title(f"Actual oracle state for pixel ({col}, {row})\n16 basis states = 4 x 4 subpixels", fontsize=12)
    detail.axis("off")
    figure.text(0.5, 0.045, "Right: each amplitude has magnitude 1/4 and probability 1/16. Orange spokes show phase.\n"
                "White marked subpixels have phase pi (down); dark subpixels have phase 0 (up).\n"
                "The left panel is a display, not one quantum register containing the reconstructed image.",
                ha="center", fontsize=10)
    figure.subplots_adjust(bottom=0.21, top=0.88, wspace=0.15)
    figure.savefig(output / "circle_notation.png", dpi=180)
    plt.close(figure)
    return {"pixel_xy": [int(col), int(row)], "oracle_amplitude_magnitude": 0.25,
            "oracle_basis_states": 16, "white_subpixel_mask": mask.astype(int).tolist()}


def print_circuit_diagrams(mask, counter_bits):
    """Print QPE, one Grover iteration, and the expanded inverse QFT as text.

    Measurements appear on a copy of the QPE circuit. The simulation uses
    the unmeasured circuit from build_counting_circuit.
    """
    counting_circuit = build_counting_circuit(mask, counter_bits)
    measured_circuit = counting_circuit.copy()
    readout = ClassicalRegister(counter_bits, "readout")
    measured_circuit.add_register(readout)
    measured_circuit.measure(measured_circuit.qregs[0], readout)

    subpixel = QuantumRegister(4, "subpixel")
    grover_circuit = QuantumCircuit(subpixel, name="One Grover iteration")
    grover_circuit.append(UnitaryGate(build_phase_oracle(mask), label="O"), subpixel)
    grover_circuit.append(UnitaryGate(build_diffusion_operator(), label="D"), subpixel)

    counter = QuantumRegister(counter_bits, "counter")
    inverse_qft_circuit = QuantumCircuit(counter, name="Inverse QFT")
    inverse_qft_circuit.append(QFTGate(counter_bits).inverse(), counter)
    inverse_qft_circuit = inverse_qft_circuit.decompose(reps=1)

    diagrams = [
        ("QPE / quantum counting", measured_circuit),
        ("One Grover iteration Q = D O", grover_circuit),
        ("Inverse QFT on the counter", inverse_qft_circuit),
    ]
    print("\nControlled Grover blocks use pin 0 as the counter control; "
          "pins 1 through 4 are subpixel targets.", flush=True)
    for title, circuit in diagrams:
        print(f"\n{title}\n{circuit.draw(output='text', fold=120)}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("Origami Totoro-Style Paper Creature.png"))
    parser.add_argument("--size", type=int, default=128)
    parser.add_argument("--counter-bits", type=int, default=6)
    parser.add_argument("--shots", type=int, default=128)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("qss_output"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not 8 <= args.size <= 512 or not 6 <= args.counter_bits <= 9 or args.shots < 1:
        parser.error("Require size 8..512, counter bits 6..9, and shots >= 1.")
    if not args.input.is_file():
        parser.error(f"Input image not found: {args.input}")
    args.output.mkdir(parents=True, exist_ok=True)
    started = perf_counter()
    distributions, peaks, lookup = calibration(args.counter_bits)
    checks = self_test(args.counter_bits, distributions, peaks, lookup) if args.self_test else None
    with Image.open(args.input) as original:
        source = ImageOps.exif_transpose(original).convert("RGB")
    tiles = image_tiles(source, args.size)
    measured, diagnostic, unique_oracles = reconstruct(
        tiles, args.counter_bits, args.shots, lookup, args.seed)
    classical = tiles.mean(axis=(2, 3))
    save_gray(measured, args.output / "qss_totoro.png")
    comparison(source, tiles, measured, args.output)
    circles = circle_notation(tiles, measured, args.output)
    representative_mask = np.array(circles["white_subpixel_mask"], dtype=bool)
    print_circuit_diagrams(representative_mask, args.counter_bits)
    metrics = {
        "input": str(args.input.resolve()), "output_size": [args.size, args.size],
        "subpixels_per_pixel": 16, "counter_bits": args.counter_bits,
        "qubits_per_circuit": args.counter_bits + 4, "shots_per_pixel": args.shots,
        "seed": args.seed, "unique_spatial_oracles_simulated": unique_oracles,
        "calibration_circuits": 17, "counter_calibration_peaks": peaks.tolist(),
        "measured_mae_vs_classical_fraction": float(abs(measured - classical).mean()),
        "measured_max_error_vs_classical_fraction": float(abs(measured - classical).max()),
        "measured_pixels_matching_classical": int(np.count_nonzero(measured == classical)),
        "statevector_mode_mae_vs_classical_fraction": float(abs(diagnostic - classical).mean()),
        "elapsed_seconds_including_figures": perf_counter() - started,
        "self_test": checks, "circle_notation": circles,
        "method": "Qiskit Statevector QPE on full 16-state Grover operator; finite-shot folded-counter mode decoded by quantum calibration",
        "qualification": "Classical bitmap LUT oracle preparation, dense controlled Grover powers, simulator sampling and exact spatial-mask caching; no hardware run or speedup claim.",
    }
    (args.output / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

