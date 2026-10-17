# Grover search and amplitude amplification

Explore how Grover iterations change the probability of measuring a marked state. A NumPy statevector model is plotted alongside `sin²((2k + 1) theta)`, with `sin(theta) = 1/sqrt(N)` for one marked state.

![Three-qubit target probability](figures/grover_3qubits_101.png)

## Explore the results

- [Two-qubit search](figures/grover_2qubits_01.png) marks `01`.
- [Three-qubit search](figures/grover_3qubits_101.png) marks `101`.
- [Measurement distributions](figures/grover_3qubits_101_shot_distributions.png) compare shot counts after two amplification iterations.

The [Python script](scripts/grover_probability.py) constructs the phase oracle and diffusion matrices, updates the state, and samples outcomes. It uses NumPy rather than a Qiskit backend.

## Generate the plots

Run from the portfolio root.

```powershell
.\.venv\Scripts\python.exe -m pip install -r projects/grover/requirements.txt
.\.venv\Scripts\python.exe projects/grover/scripts/grover_probability.py
```

Images are saved in this project's `figures/` directory. The script also opens Matplotlib windows.

## Open the slide deck

The [Slidev deck](slides.md) is a work in progress. It includes custom material on qubit states, the Bloch sphere, Bell states, and the classical search baseline. Original Slidev starter slides remain in the deck.

From this project directory, run with Node.js and npm installed.

```powershell
npm ci
npm run dev
```

The `build` and `export` npm scripts create a website build and a slide export. The deck has its own [package manifest](package.json) and lockfile. JavaScript dependencies are separate from the Python environment.
