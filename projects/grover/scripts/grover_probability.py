import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

output_dir = Path(__file__).resolve().parents[1] / "figures"
output_dir.mkdir(exist_ok=True)


def plot_grover(n, target, filename, iterations=30):
    size = 2**n
    state = np.ones(size, dtype=complex) / np.sqrt(size)
    oracle = np.eye(size)
    oracle[int(target, 2), int(target, 2)] = -1
    diffuser = 2 * np.outer(state, state) - np.eye(size)

    probabilities = [abs(state[int(target, 2)]) ** 2]
    for _ in range(iterations):
        state = diffuser @ oracle @ state
        probabilities.append(abs(state[int(target, 2)]) ** 2)

    k = np.arange(iterations + 1)
    k_smooth = np.linspace(0, iterations, 1000)
    theta = np.arcsin(1 / np.sqrt(size))

    plt.figure()
    plt.plot(k_smooth, np.sin((2 * k_smooth + 1) * theta) ** 2, label="Theory")
    plt.scatter(k, probabilities, color="crimson", zorder=3, label="Iterations")
    plt.xlabel("Number of AA iterations")
    plt.ylabel(f"Probability of |{target}>")
    plt.title(f"Grover's algorithm: {n} qubits, target |{target}>")
    plt.xticks(range(0, iterations + 1, 2))
    plt.ylim(0, 1.05)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / filename, dpi=300, bbox_inches="tight")


def plot_shot_distributions(target="101", grover_iterations=2):
    n, size = len(target), 2 ** len(target)
    state = np.ones(size, dtype=complex) / np.sqrt(size)
    oracle = np.eye(size)
    oracle[int(target, 2), int(target, 2)] = -1
    diffuser = 2 * np.outer(state, state) - np.eye(size)

    for _ in range(grover_iterations):
        state = diffuser @ oracle @ state

    probabilities = np.abs(state) ** 2
    labels = [format(i, f"0{n}b") for i in range(size)]
    colors = ["crimson" if label == target else "steelblue" for label in labels]
    rng = np.random.default_rng(42)

    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharey=True)
    for ax, shots in zip(axes.flat, [1, 10, 100, 1_000, 10_000, 100_000]):
        counts = rng.multinomial(shots, probabilities)
        ax.bar(labels, counts / shots, color=colors)
        ax.set_title(f"{shots:,} shots")
        ax.set_xlabel("Measured state")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(axis="y", alpha=0.3)

    axes[0, 0].set_ylabel("Relative frequency")
    axes[1, 0].set_ylabel("Relative frequency")
    fig.suptitle(f"Measurement distribution: target |{target}>, {grover_iterations} AA iterations")
    fig.tight_layout()
    fig.savefig(output_dir / "grover_3qubits_101_shot_distributions.png", dpi=300,
                bbox_inches="tight")


plot_grover(2, "01", "grover_2qubits_01.png")
plot_grover(3, "101", "grover_3qubits_101.png")
plot_shot_distributions()
plt.show()
