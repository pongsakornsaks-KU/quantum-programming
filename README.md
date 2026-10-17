# Quantum programming

Quantum computing projects and learning experiments. Each project contains its code, example results, and instructions for exploring the work.

## Projects

| Project | What it explores | Main tools |
| --- | --- | --- |
| [Quantum supersampling](projects/quantum-supersampling/README.md) | Estimate image brightness with Grover operators and quantum phase estimation. | Qiskit, NumPy, Matplotlib |
| [Grover search](projects/grover/README.md) | Compare amplitude amplification with its analytic probability curve and finite-shot measurements. | NumPy, Matplotlib, Slidev |
| [Quantum self-attention](projects/quantum-self-attention/README.md) | Explore a small quantum self-attention model alongside a classical baseline. | PennyLane, Qiskit, Matplotlib |
| [Remote-Controlled Randomness](https://github.com/pongsakornsaks-KU/remote-controlled-randomness) | Explore entanglement and randomness through a Qiskit notebook. | Qiskit, Jupyter |

Remote-Controlled Randomness remains in its own repository. This repository links to it rather than embedding another Git repository. A local checkout can live at `projects/remote-controlled-randomness/`, which is excluded from this repository's Git tracking.

## Start with a result

The [QSS comparison](projects/quantum-supersampling/qss_output/comparison.png) shows the input image, a single-sample baseline, classical supersampling, and the quantum counting estimate.

![Quantum supersampling comparison](projects/quantum-supersampling/qss_output/comparison.png)

Read the [QSS project guide](projects/quantum-supersampling/README.md) for the mathematical steps. The [Grover plots](projects/grover/README.md) connect repeated iterations to target-state probability.

These projects use classical simulation. Their sample outputs do not establish a quantum speedup.

## Learning material

[Learning experiments](learning/README.md) contain Bloch sphere visualizations, basic circuit notebooks, and classical Fourier and sampling exercises.

## Set up Python

Use Python 3.12 to match the existing local environment. Run these commands from the repository root.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r projects/quantum-supersampling/requirements.txt
```

If `.venv` already exists, use it without recreating it. Each project lists its own dependencies. Install the requirements for the project you want to run. Select this environment as the Jupyter kernel for notebooks. The Grover slide deck uses Node.js separately.

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

The local Remote-Controlled Randomness checkout, reading PDFs, environments, caches, and agent working files are excluded by `.gitignore`. Selected result images remain in this repository so visitors can inspect them without running code.

## Get the code

Clone [quantum-programming](https://github.com/pongsakornsaks-KU/quantum-programming), then open the repository directory.

```powershell
git clone https://github.com/pongsakornsaks-KU/quantum-programming.git
cd quantum-programming
```

Use the setup commands above from this directory.
