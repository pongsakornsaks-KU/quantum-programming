"""Quantum supersampling โดยเชื่อมสมการกับ circuit ของ Qiskit.

เริ่มอ่านส่วน quantum ตามลำดับ build_phase_oracle → build_grover_operator →
build_counting_circuit → counter_distribution. ส่วน main อยู่ท้ายไฟล์.

ข้อมูลหนึ่ง pixel คือ mask แบบ bool ขนาด (4, 4). True หมายถึง subpixel สีขาว.
เรียงแต่ละแถวต่อกันเป็น basis |x> โดย x = 4 * row + col เช่น [1, 2] คือ |0110>.
ใช้ 4 subpixel qubits แทน 16 ตำแหน่ง และ counter_bits qubits สำหรับ QPE.

ถ้ามีสีขาว M ตำแหน่ง จะได้ a = M/16 = sin²(theta), Q = D O มี eigenphase
±2*theta. QPE ให้ y/2**counter_bits ≈ theta/pi หรือ 1-theta/pi.
จึงพับผลสองฝั่งเข้าหากัน แล้วแปลงเป็นจำนวนสีขาวด้วย calibration.

image_tiles เตรียม bitmap ด้วยวิธี classical. reconstruct ใช้ distribution
จาก quantum circuit แล้วจำลอง finite shots แบบ classical ทีละ pixel.
นี่คือ dense statevector simulation ไม่ใช่การอ้าง quantum speedup.
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
    """คืน matrix O ขนาด (16, 16) จาก white mask ขนาด (4, 4).

    O|x> = (-1)**mask[row, col] |x>. ravel เรียงแถวต่อแถว
    ให้ index ของ matrix ตรงกับ x = 4 * row + col.
    """
    phase_signs = 1.0 - 2.0 * mask.ravel()
    return np.diag(phase_signs)


def build_diffusion_operator():
    """คืน D = 2|s><s| - I โดย |s> มี amplitude 1/4 ทั้ง 16 basis states."""
    return np.full((16, 16), 2 / 16) - np.eye(16)


def build_grover_operator(mask):
    """คืน Q = D @ O ซึ่งใช้ O ก่อน แล้วจึงใช้ D.

    |s> = (1/4) sum_x |x>, D = 2|s><s| - I.
    แต่ละช่องของ 2|s><s| จึงเท่ากับ 2/16.
    เก็บ sign ของ D ตามสมการนี้ เพราะ global phase ของ Q
    กลายเป็น relative phase เมื่อใช้ controlled-Q ใน QPE.
    """
    diffusion = build_diffusion_operator()
    oracle = build_phase_oracle(mask)
    return diffusion @ oracle


def build_counting_circuit(mask, counter_bits):
    """สร้าง QPE circuit ที่ยังไม่มี measurement เพื่อใช้ทั้งจำลองและวาดรูป.

    counter[j] ควบคุม Q**(2**j). subpixel เริ่มใน |s> ด้วย H ทั้ง 4 เส้น.
    counter อยู่ index 0..counter_bits-1 และ subpixel อยู่ถัดไป.
    ใน Qiskit qubit ตัวแรกของ qargs เป็น bit ที่มีนัยสำคัญต่ำสุด.
    inverse QFT แปลง phase ที่สะสมใน counter เป็น distribution ของค่า y.
    """
    counter = QuantumRegister(counter_bits, "counter")
    subpixel = QuantumRegister(4, "subpixel")
    circuit = QuantumCircuit(counter, subpixel, name="Quantum counting")
    circuit.h(counter)
    circuit.h(subpixel)

    grover_power = build_grover_operator(mask)
    for counter_bit in range(counter_bits):
        exponent = 2 ** counter_bit
        # qargs ตัวแรกเป็น control จึงเลือกแถว/คอลัมน์เลขคี่ที่ control = 1.
        controlled_grover = np.eye(32, dtype=complex)
        controlled_grover[1::2, 1::2] = grover_power
        gate = UnitaryGate(controlled_grover, label=f"c-Q^{exponent}")
        circuit.append(gate, [counter[counter_bit], *subpixel])
        # ยกกำลังสองต่อรอบจึงได้ Q, Q², Q⁴, ... โดยไม่คูณซ้ำจากต้น.
        grover_power = grover_power @ grover_power

    circuit.append(QFTGate(counter_bits).inverse(), counter)
    return circuit


def counter_distribution(mask, counter_bits):
    """คืน P(y) จำนวน 2**counter_bits ค่า จาก counter register ของ QPE.

    Statevector ให้ probability ที่แน่นอนก่อนสุ่ม shots.
    การไม่วัด subpixel คือการรวม probability เหนือ subpixel ทุกสถานะ.
    """
    circuit = build_counting_circuit(mask, counter_bits)
    probabilities = Statevector.from_instruction(circuit).probabilities(
        qargs=list(range(counter_bits)))
    return probabilities / probabilities.sum()


def folded(probabilities):
    """รวม P(y) กับ P(N-y) เพราะ eigenphase สองฝั่งให้ค่า a เดียวกัน.

    รับ array ยาว N = 2**counter_bits. คืน array ยาว N/2 + 1.
    y = 0 และ y = N/2 ไม่มีคู่ จึงไม่บวกซ้ำ.
    """
    outcome_count = len(probabilities)
    midpoint = outcome_count // 2
    folded_probabilities = probabilities[:midpoint + 1].copy()
    folded_probabilities[1:-1] += probabilities[:midpoint:-1]
    return folded_probabilities


def calibration(counter_bits):
    """คืน distributions ของ M=0..16, peaks ของแต่ละ M และ lookup[y]=M.

    ใช้ mask ตัวอย่างหนึ่งแบบต่อ M เพราะ distribution ขึ้นกับจำนวนสีขาว.
    self_test ตรวจสมบัตินี้ด้วย mask ที่สลับตำแหน่ง.
    สมการ a = sin(pi*y/2**counter_bits)**2 ให้ M ≈ 16*a.
    lookup เลือก M ที่มี peak ใกล้ y ที่สุด เพื่อ decode ทุก outcome ที่วัดได้.
    """
    distributions = []
    for white_count in range(17):
        mask = (np.arange(16) < white_count).reshape(4, 4)
        distributions.append(counter_distribution(mask, counter_bits))
    peaks = np.array([np.argmax(folded(distribution)) for distribution in distributions])
    if len(np.unique(peaks)) != 17:
        raise ValueError("Use at least 6 counter bits to distinguish all 17 shades.")
    folded_outcomes = np.arange(2 ** (counter_bits - 1) + 1)
    # [:, None] จัด outcome เป็นคอลัมน์ และ [None, :] จัด 17 peaks เป็นแถว.
    distance_to_each_peak = abs(folded_outcomes[:, None] - peaks[None, :])
    lookup = np.argmin(distance_to_each_peak, axis=1)
    return distributions, peaks, lookup


def self_test(counter_bits, distributions, peaks, lookup):
    """ตรวจการ decode, normalization และ invariance เมื่อสลับตำแหน่งสีขาว."""
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
    """คืน bool array [pixel_row, pixel_col, subpixel_row, subpixel_col].

    แต่ละ pixel มี mask (4, 4). Bayer dithering แปลง grayscale
    เป็น subpixel สีขาว/ดำในขั้น classical ก่อนสร้าง oracle.
    """
    gray = source.convert("L").resize((size * 4, size * 4), Image.Resampling.NEAREST)
    values = np.asarray(gray, dtype=float) / 255
    thresholds = np.tile((BAYER + 0.5) / 16, (size, size))
    white = values >= thresholds
    return white.reshape(size, 4, size, 4).transpose(0, 2, 1, 3)


def reconstruct(tiles, counter_bits, shots, lookup, seed):
    """คืน brightness จาก shots, brightness จาก exact mode และจำนวน mask.

    สองภาพแรกมี shape (size, size). lookup แปลง counter outcome เป็น M
    แล้ว M/16 เป็น brightness. เลือก outcome ที่พบบ่อยที่สุดจาก shots.
    cache เก็บ distribution ของ mask ที่เหมือนกันเพื่อลดงาน simulator.
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
    """วาด oracle state ของ pixel ตัวอย่าง และคืน mask ที่ใช้วาดจริง."""
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


def save_circuit_diagrams(mask, counter_bits, output):
    """พิมพ์และบันทึก circuit ของ mask เดียวกับภาพ circle notation.

    QPE ใช้ builder เดียวกับ simulator แต่เพิ่ม measurement ลงในสำเนาเพื่อวาด.
    PNG ใช้ circuit.draw(output="mpl") ของ Qiskit โดยต้องมี pylatexenc.
    กล่อง c-Q เป็น dense matrix จริง โดย pin 0 เป็น control ไม่ใช่ target.
    """
    counting_circuit = build_counting_circuit(mask, counter_bits)
    measured_circuit = counting_circuit.copy()
    readout = ClassicalRegister(counter_bits, "readout")
    measured_circuit.add_register(readout)
    measured_circuit.measure(measured_circuit.qregs[0], readout)

    subpixel = QuantumRegister(4, "subpixel")
    grover_circuit = QuantumCircuit(subpixel, name="One Grover iteration")
    grover_circuit.append(UnitaryGate(build_phase_oracle(mask), label="O"), subpixel)
    diffusion = build_diffusion_operator()
    grover_circuit.append(UnitaryGate(diffusion, label="D"), subpixel)

    counter = QuantumRegister(counter_bits, "counter")
    inverse_qft_circuit = QuantumCircuit(counter, name="Inverse QFT")
    inverse_qft_circuit.append(QFTGate(counter_bits).inverse(), counter)
    inverse_qft_circuit = inverse_qft_circuit.decompose(reps=1)

    diagrams = [
        ("qpe_circuit", measured_circuit, "QPE / quantum counting",
         "H prepares the counter and |s>. Each c-Q^(2^j) is controlled by counter[j].\n"
         "In each dense c-Q box, pin 0 is the control; pins 1..4 are subpixel targets.\n"
         "Measurement is shown here; simulation uses the same circuit before measurement."),
        ("grover_circuit", grover_circuit, "One Grover iteration Q = D O",
         "Read left to right: O flips white-subpixel phases, then D = 2|s><s| - I.\n"
         "Subpixel basis index x = 4*row + col; |s> is prepared in the QPE circuit."),
        ("inverse_qft_circuit", inverse_qft_circuit, "Inverse QFT on the counter",
         "The inverse QFT block from QPE, expanded into gates.\n"
         "counter[0] is the least significant bit of the counter outcome."),
    ]
    saved_files = []
    for filename, circuit, title, caption in diagrams:
        circuit_text = str(circuit.draw(output="text", fold=120))
        print(f"\n{title}\n{caption}\n\n{circuit_text}", flush=True)

        figure = circuit.draw(output="mpl", fold=-1, initial_state=True,
                              style={"fontsize": 10, "subfontsize": 8})
        figure.suptitle(title, y=1.02, fontsize=14)
        figure.text(0.5, -0.02, caption, ha="center", va="top", fontsize=10)
        png_path = output / f"{filename}.png"
        figure.savefig(png_path, dpi=160, bbox_inches="tight")
        plt.close(figure)
        saved_files.append(png_path.name)
    return saved_files


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
    circuit_files = save_circuit_diagrams(representative_mask, args.counter_bits, args.output)
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
        "self_test": checks, "circle_notation": circles, "circuit_diagrams": circuit_files,
        "method": "Qiskit Statevector QPE on full 16-state Grover operator; finite-shot folded-counter mode decoded by quantum calibration",
        "qualification": "Classical bitmap LUT oracle preparation, dense controlled Grover powers, simulator sampling and exact spatial-mask caching; no hardware run or speedup claim.",
    }
    (args.output / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

