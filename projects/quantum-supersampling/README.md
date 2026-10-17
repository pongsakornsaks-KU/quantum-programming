# Totoro using quantum supersampling

Reconstruct a grayscale image of Totoro by estimating white-subpixel fractions with quantum counting. This project connects an image tile to a phase oracle, a Grover operator, and a quantum phase estimation (QPE) circuit.

![Supersampling comparison](qss_output/comparison.png)

## How the estimate works

Classical preprocessing converts the source image to grayscale, resizes it to 512 by 512, and applies Bayer dithering to produce a binary image. Each 4 by 4 tile supplies 16 subpixel samples for one pixel in the 128 by 128 output. The final reduction is downsampling; supersampling uses the multiple samples within each output pixel to estimate its average brightness.

Four subpixel qubits represent the 16 positions. The tile configures a phase oracle `O_f` that marks white positions. One Grover iteration is `U = Q = D @ O_f`, applying the oracle first and then diffusion, where `D = 2|s><s| - I`.

All ten qubits start in zero. QPE uses six counter qubits to estimate the eigenphases of `Q`, and only the counter is measured. For each pixel, the decoder folds symmetric outcomes, selects the most frequent bin from 128 shots, and applies a calibration lookup to estimate the number of white subpixels. Dividing that count by 16 gives brightness. A classical loop writes the brightness into the corresponding output pixel.

Bitmap preparation, dithering, and sampling from simulator probabilities are classical operations. This is a statevector demonstration of the algorithm. The recorded results do not establish a hardware speedup or a noise advantage over Monte Carlo sampling.

## Circuit diagrams

The three figures below are rendered from LaTeX with Quantikz. They use the default six counter qubits and four subpixel qubits.

### Quantum counting

Each counter qubit `c_j` controls `Q^(2^j)` on all four subpixel qubits. The inverse QFT acts on the counter, which is then measured. `c_0` is the least significant bit of the readout.

![Quantum counting with six counter qubits and four subpixel qubits](qss_output/quantum_counting_circuit.png)

### One application of U

`U = Q = D O_f` applies the phase oracle followed by diffusion. The dashed group applies Hadamard to each qubit, then `S_0`, then Hadamard to each qubit again, with `S_0 = 2|0000><0000| - I`. The sign matches the controlled Grover operator used by QPE.

![One Grover iteration with the phase oracle and expanded diffusion](qss_output/unitary_u_circuit.png)

### Inverse QFT

The six-qubit inverse QFT includes bit-reversal SWAP gates, Hadamard gates, and controlled phase rotations. The figure defines the inverse phase rotations and preserves the qubit order used by Qiskit.

![Expanded six-qubit inverse QFT](qss_output/inverse_qft_6qubit.png)

## Read the code

Start with these functions in [quantum_supersampling.py](quantum_supersampling.py).

1. `build_phase_oracle` defines `O` from the tile.
2. `build_diffusion_operator` defines `D = 2|s><s| - I`.
3. `build_grover_operator` combines them as `Q = D @ O`.
4. `build_counting_circuit` prepares registers, controlled powers, and inverse QFT.
5. `counter_distribution` extracts counter probabilities.
6. `folded`, `calibration`, and `reconstruct` convert outcomes into an image.

The source includes Thai explanations with English quantum terminology. A standalone HTML walkthrough is kept locally at `qss_output/quantum_supersampling_explained.html` and excluded from Git.

## Run the example

Run from the repository root with its virtual environment.

```powershell
.\.venv\Scripts\python.exe -m pip install -r projects/quantum-supersampling/requirements.txt
.\.venv\Scripts\python.exe -X utf8 projects/quantum-supersampling/quantum_supersampling.py --self-test
```

For a smaller trial, use `--size 8`. `-X utf8` enables circuit printing on Windows. Input and output defaults resolve relative to the script.

The script also generates Qiskit Matplotlib diagrams named `qpe_circuit.png`, `grover_circuit.png`, and `inverse_qft_circuit.png`. Those files are separate from the three Quantikz figures above and will be recreated on a run. The saved `metrics.json` retains those diagram filenames as part of the original run record.

## Inspect the outputs

| File | Purpose |
| --- | --- |
| [comparison.png](qss_output/comparison.png) | Compare input, classical baselines, and QPE estimates. |
| [circle_notation.png](qss_output/circle_notation.png) | Connect a selected tile to its basis-state phases. |
| [quantum_counting_circuit.png](qss_output/quantum_counting_circuit.png) | Inspect the full quantum counting circuit. |
| [unitary_u_circuit.png](qss_output/unitary_u_circuit.png) | Inspect the oracle and expanded diffusion in one application of U. |
| [inverse_qft_6qubit.png](qss_output/inverse_qft_6qubit.png) | Inspect the expanded six-qubit inverse QFT. |
| [qss_totoro.png](qss_output/qss_totoro.png) | Read the output at its native resolution. |
| [metrics.json](qss_output/metrics.json) | Read parameters, self-test results, and errors. |

The simulator implements controlled Grover powers as dense unitary matrices. The Quantikz figures show the same operations using standard control dots and target blocks. Measurements are shown for readout; the statevector simulation uses the circuit before measurement.

The saved example is 128 by 128. Absolute paths in saved metrics record the original run location and are not used to locate input files.

## Reports

- [English report](report/report_en.pdf), titled *Totoro Using Quantum supersampling*.

The Thai report is kept locally at `report/report.pdf` and excluded from Git.

The reports follow Chapter 11 of *Programming Quantum Computers* and distinguish its QSS examples from this project's bitmap-based simulation.

## Local LaTeX sources

Circuit sources are stored in `qss_output/latex`. Report sources, fonts, and build assets are stored in `report/latex`. Both `latex` directories are local files excluded from Git. PNG figures remain in `qss_output`, and completed PDF reports remain in `report`. Only the English report is tracked in Git.

With the local sources and Tectonic available, compile from this project's `qss_output/latex` directory:

```powershell
tectonic --untrusted --outdir .. quantum_counting_circuit.tex
tectonic --untrusted --outdir .. unitary_u_circuit.tex
tectonic --untrusted --outdir .. inverse_qft_6qubit.tex
```

These commands produce vector PDFs in `qss_output`. The saved PNGs were exported from those PDFs with `python -m pypdfium2_cli render` at a scale of 5 pixels per PDF point. The circuit sources load the bundled Quantikz library from `report/latex/assets`, so retain that local directory.

To compile the reports, run these commands from `report/latex`:

```powershell
tectonic --untrusted --outdir .. report.tex
tectonic --untrusted --outdir .. report_en.tex
```

Tectonic was used as a temporary tool and is not bundled with the project.
