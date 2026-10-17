# Quantum programming

This repository contains quantum computing projects and learning experiments. Each project includes code and example results.

## Projects

| Project | Description | Main tools |
| --- | --- | --- |
| [Quantum supersampling](projects/quantum-supersampling/README.md) | Estimates image brightness with Grover operators and quantum phase estimation. | Qiskit, NumPy, Matplotlib |
| [Grover search](projects/grover/README.md) | Compares amplitude amplification simulations and finite-shot measurements with the analytic probability curve. | NumPy, Matplotlib |
| [Quantum self-attention](projects/quantum-self-attention/README.md) | Compares a small quantum self-attention model with a classical baseline. | PennyLane, Qiskit, Matplotlib |
| [Remote-Controlled Randomness](https://github.com/pongsakornsaks-KU/remote-controlled-randomness) | Uses a Qiskit notebook to study entanglement and randomness. | Qiskit, Jupyter |

Remote-Controlled Randomness has its own repository. You can clone it into `projects/remote-controlled-randomness/`. This repository's `.gitignore` excludes that directory.

## Start with a result

The [QSS comparison](projects/quantum-supersampling/qss_output/comparison.png) shows the input image, a single-sample baseline, classical supersampling, and the quantum counting estimate.

![Quantum supersampling comparison](projects/quantum-supersampling/qss_output/comparison.png)

Read the [QSS project guide](projects/quantum-supersampling/README.md) for the mathematical steps. The [Grover plots](projects/grover/figures/) show how the target-state probability changes with the number of iterations.

These projects use classical simulation. Their sample outputs do not establish a quantum speedup.

## Learning material

The [learning experiments](learning/README.md) include Bloch sphere visualizations, basic circuit notebooks, and classical Fourier and sampling exercises.

## Set up Python

Use Python 3.12 to match the existing local environment. Run these commands from the repository root.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r projects/quantum-supersampling/requirements.txt
```

If `.venv` already exists, use it. QSS, quantum self-attention, and the learning experiments each have a requirements file. Install the requirements for the project you want to run. For notebooks, select `.venv` as the Jupyter kernel.

For Grover, install NumPy and Matplotlib, then run the plot script from the repository root.

```powershell
.\.venv\Scripts\python.exe -m pip install numpy matplotlib
.\.venv\Scripts\python.exe projects/grover/scripts/grover_probability.py
```

## Repository layout

```text
quantum/
  README.md
  projects/
    quantum-supersampling/
    grover/
    quantum-self-attention/
  learning/
    qubit-visualization/
    fourier-and-sampling/
```

The `.gitignore` file excludes the local Remote-Controlled Randomness checkout, reference PDFs, environments, caches, and agent working files. The repository includes example result images so you can inspect them without running code.
