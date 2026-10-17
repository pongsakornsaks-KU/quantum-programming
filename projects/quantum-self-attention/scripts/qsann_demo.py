"""
Quantum Self-Attention Neural Network (QSANN) - Demo Script
Based on Paper: "Quantum Self-Attention Neural Networks for Text Classification" (arXiv:2205.05625v2)

This script provides:
1. Classical Self-Attention (CSANN) baseline
2. Quantum Self-Attention (QSANN / GPQSA) using PennyLane
3. Graphical Quantum Circuit Diagrams (Saved as PNG images for presentation slides)
4. Heatmap Comparison of Attention Weights (Classical vs Quantum)
5. Fixed Autograd Training Loop (Loss decreases over epochs)
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
# pyrefly: ignore [missing-import]
import pennylane as qml
# pyrefly: ignore [missing-import]
from pennylane import numpy as pnp

FIGURES_DIR = Path(__file__).resolve().parents[1] / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Qiskit is used only to draw presentation-quality circuit diagrams. PennyLane
# remains the execution/training backend, so visualization cannot change the
# model's numerical behavior.
try:
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
    from qiskit.circuit import ParameterVector
    from qiskit.visualization import circuit_drawer
    QISKIT_DRAWING_AVAILABLE = True
    QISKIT_IMPORT_ERROR = None
except ImportError as exc:
    QISKIT_DRAWING_AVAILABLE = False
    QISKIT_IMPORT_ERROR = exc

# Set random seeds for reproducibility
np.random.seed(42)

# ==========================================
# 1. PARAMETERS & CONFIGURATION
# ==========================================
NUM_QUBITS = 2          # n = 2 qubits
ENCODER_LAYERS = 1      # D_enc in the paper
ANSATZ_LAYERS = 1       # D_q = D_k = D_v in the paper
VEC_DIM = NUM_QUBITS * (ENCODER_LAYERS + 2)  # d = n(D_enc + 2) = 6
NUM_WORDS = 4           # S = 4 words in input sequence

# The paper uses Z_1...Z_n, X_1...X_n, Y_1...Y_n as the d value
# observables when D_enc=1. This compact demo implements that exact setting.
if ENCODER_LAYERS != 1:
    raise ValueError(
        "This demo currently supports ENCODER_LAYERS=1 so VEC_DIM=3*NUM_QUBITS "
        "matches the paper's Z/X/Y value observables."
    )

print("="*70)
print("  QSANN DEMO: Quantum vs Classical Self-Attention for Text Classification")
print("="*70)
print(
    f"Configuration: {NUM_QUBITS} Qubits | Vector Dimension = {VEC_DIM} | "
    f"D_enc = {ENCODER_LAYERS} | D_q/k/v = {ANSATZ_LAYERS} | "
    f"Sequence Length = {NUM_WORDS} words\n"
)

# Toy Input Sequence: "quantum computing is powerful"
WORD_LABELS = ["quantum", "computing", "is", "powerful"]
X_input = pnp.array([
    [ 0.5, -0.2,  0.3,  0.1, -0.4,  0.2],    # "quantum"
    [-0.8,  0.6, -0.1,  0.4,  0.2, -0.3],    # "computing"
    [ 0.1,  0.3,  0.2, -0.2,  0.1,  0.4],    # "is"
    [ 0.9, -0.5,  0.4,  0.2, -0.3,  0.6]     # "powerful"
], requires_grad=False)

print(f"Input Sequence Vectors X (shape: {NUM_WORDS}x{VEC_DIM}):")
for idx, x in enumerate(X_input):
    print(f"  Word {idx+1} ({WORD_LABELS[idx]}): {x}")
print()

# ==========================================
# 2. CLASSICAL SELF-ATTENTION (CSANN BASELINE)
# ==========================================
class ClassicalSelfAttention:
    """Standard Classical Transformer Self-Attention Layer (Vaswani et al.)"""
    def __init__(self, d_in=VEC_DIM, d_out=VEC_DIM):
        self.W_q = np.random.randn(d_in, d_out) * 0.1
        self.W_k = np.random.randn(d_in, d_out) * 0.1
        self.W_v = np.random.randn(d_in, d_out) * 0.1
        self.W_fc = np.random.randn(d_out, 1) * 0.1
        self.b_fc = 0.0

    def num_parameters(self):
        qkv_params = self.W_q.size + self.W_k.size + self.W_v.size
        classifier_params = self.W_fc.size + 1
        return qkv_params + classifier_params

    def parameter_breakdown(self):
        return {
            "query_matrix": self.W_q.size,
            "key_matrix": self.W_k.size,
            "value_matrix": self.W_v.size,
            "classifier": self.W_fc.size + 1,
            "total": self.num_parameters(),
        }

    def forward(self, X):
        Q = X @ self.W_q
        K = X @ self.W_k
        V = X @ self.W_v

        scores = (Q @ K.T) / np.sqrt(VEC_DIM)
        exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        attn_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)

        V_attn = attn_weights @ V
        Y_out = X + V_attn
        
        pooled = np.mean(Y_out, axis=0)
        logit = pooled @ self.W_fc + self.b_fc
        pred = 1.0 / (1.0 + np.exp(-logit))
        return Y_out, attn_weights, pred

csann = ClassicalSelfAttention()
csann_y, csann_attn, csann_pred = csann.forward(X_input)

print("-" * 70)
print("CLASSICAL SELF-ATTENTION (CSANN) - BEFORE TRAINING:")
csann_param_breakdown = csann.parameter_breakdown()
print(
    "Q/K/V Parameters: "
    f"{csann_param_breakdown['query_matrix']} + "
    f"{csann_param_breakdown['key_matrix']} + "
    f"{csann_param_breakdown['value_matrix']} = "
    f"{3 * VEC_DIM * VEC_DIM}"
)
print(f"Classifier Parameters: {csann_param_breakdown['classifier']}")
print(f"Total Parameters: {csann.num_parameters()}")
print(f"Predicted Probability (untrained): {csann_pred[0]:.4f}")
print("-" * 70)
print()

# ==========================================
# 2B. CLASSICAL TRAINING LOOP
# ==========================================
print("TRAINING CLASSICAL SELF-ATTENTION (10 EPOCHS)...")
print(f"{'Epoch':<10} | {'Loss (MSE)':<15} | {'Prediction':<15}")
print("-" * 45)

lr_c = 0.5
eps = 1e-5
target_c = 1.0

for epoch in range(1, 11):
    # Numerical gradient descent (finite differences)
    for param in [csann.W_q, csann.W_k, csann.W_v, csann.W_fc]:
        grad = np.zeros_like(param)
        for idx in np.ndindex(param.shape):
            orig = param[idx]
            param[idx] = orig + eps
            loss_p = (csann.forward(X_input)[2][0] - target_c) ** 2
            param[idx] = orig - eps
            loss_m = (csann.forward(X_input)[2][0] - target_c) ** 2
            param[idx] = orig
            grad[idx] = (loss_p - loss_m) / (2 * eps)
        param -= lr_c * grad
    # Bias gradient
    orig_b = csann.b_fc
    csann.b_fc = orig_b + eps
    loss_p = (csann.forward(X_input)[2][0] - target_c) ** 2
    csann.b_fc = orig_b - eps
    loss_m = (csann.forward(X_input)[2][0] - target_c) ** 2
    csann.b_fc = orig_b
    csann.b_fc -= lr_c * (loss_p - loss_m) / (2 * eps)

    _, _, pred_c = csann.forward(X_input)
    loss_c = (pred_c[0] - target_c) ** 2
    print(f"{epoch:<10} | {float(loss_c):<15.6f} | {float(pred_c[0]):<15.4f}")

# Store trained classical results
_, csann_trained_attn, csann_trained_pred = csann.forward(X_input)
print(f"\nClassical Trained Attention Matrix:")
print(csann_trained_attn)
print("-" * 70)
print()

# ==========================================
# 3. QUANTUM SELF-ATTENTION (QSANN / GPQSA)
# ==========================================
dev = qml.device("default.qubit", wires=NUM_QUBITS)

def ring_entanglement():
    """CNOT ring used by the strongly-entangled ansatz in Fig. 2."""
    if NUM_QUBITS < 2:
        return
    for q in range(NUM_QUBITS):
        qml.CNOT(wires=[q, (q + 1) % NUM_QUBITS])

def quantum_encoder(x_vec):
    """
    Data Encoding Ansatz U_enc(x_s):
    Encodes classical vector into quantum state |psi_s>
    Eq. (3): |psi_s> = U_enc(x_s) H^{tensor n} |0^n>

    For the paper's strongly-entangled encoder, d=n(D_enc+2). Every
    embedding component is used once as a data-dependent RX/RY angle.
    These angles are input data, not trainable model parameters.
    """
    if len(x_vec) != VEC_DIM:
        raise ValueError(f"Expected an embedding of length {VEC_DIM}, got {len(x_vec)}")

    for q in range(NUM_QUBITS):
        qml.Hadamard(wires=q)

    idx = 0
    for q in range(NUM_QUBITS):
        qml.RX(x_vec[idx], wires=q)
        idx += 1
    for q in range(NUM_QUBITS):
        qml.RY(x_vec[idx], wires=q)
        idx += 1
    for _ in range(ENCODER_LAYERS):
        ring_entanglement()
        for q in range(NUM_QUBITS):
            qml.RY(x_vec[idx], wires=q)
            idx += 1

def strongly_entangled_ansatz(params):
    """
    Parameterized Quantum Circuit (PQC) template used for U_q, U_k, U_v
    Strongly-entangled ansatz from Fig. 2 of the paper:
      1. one RX and one RY angle per qubit;
      2. D repeated blocks of a CNOT ring and one RY angle per qubit.

    Therefore, one PQC has n(D+2) trainable parameters, not 3nD.
    """
    expected_params = NUM_QUBITS * (ANSATZ_LAYERS + 2)
    if len(params) != expected_params:
        raise ValueError(f"Expected {expected_params} ansatz parameters, got {len(params)}")

    idx = 0
    for q in range(NUM_QUBITS):
        qml.RX(params[idx], wires=q)
        idx += 1
    for q in range(NUM_QUBITS):
        qml.RY(params[idx], wires=q)
        idx += 1
    for _ in range(ANSATZ_LAYERS):
        ring_entanglement()
        for q in range(NUM_QUBITS):
            qml.RY(params[idx], wires=q)
            idx += 1

PARAMS_PER_ANSATZ = NUM_QUBITS * (ANSATZ_LAYERS + 2)

@qml.qnode(dev, interface="autograd")
def query_qnode(x_vec, theta_q):
    quantum_encoder(x_vec)
    strongly_entangled_ansatz(theta_q)
    return qml.expval(qml.PauliZ(0))

@qml.qnode(dev, interface="autograd")
def key_qnode(x_vec, theta_k):
    quantum_encoder(x_vec)
    strongly_entangled_ansatz(theta_k)
    return qml.expval(qml.PauliZ(0))

@qml.qnode(dev, interface="autograd")
def value_qnode(x_vec, theta_v):
    quantum_encoder(x_vec)
    strongly_entangled_ansatz(theta_v)
    # Eq. (5): d classical value features from d Pauli expectations.
    # For D_enc=1, d=3n and the paper selects Z_i, X_i, Y_i.
    return [
        *[qml.expval(qml.PauliZ(q)) for q in range(NUM_QUBITS)],
        *[qml.expval(qml.PauliX(q)) for q in range(NUM_QUBITS)],
        *[qml.expval(qml.PauliY(q)) for q in range(NUM_QUBITS)],
    ]

class QuantumSelfAttention:
    """
    Gaussian Projected Quantum Self-Attention (GPQSA) Layer
    Implements Equations (3) - (7) from the paper.
    """
    def __init__(self):
        self.theta_q = pnp.random.normal(0, 0.1, size=(PARAMS_PER_ANSATZ,), requires_grad=True)
        self.theta_k = pnp.random.normal(0, 0.1, size=(PARAMS_PER_ANSATZ,), requires_grad=True)
        self.theta_v = pnp.random.normal(0, 0.1, size=(PARAMS_PER_ANSATZ,), requires_grad=True)
        self.w_fc = pnp.random.normal(0, 0.1, size=(VEC_DIM,), requires_grad=True)
        self.b_fc = pnp.array(0.0, requires_grad=True)

    def total_params(self):
        return len(self.theta_q) + len(self.theta_k) + len(self.theta_v) + len(self.w_fc) + 1

    def parameter_breakdown(self):
        return {
            "query_pqc": len(self.theta_q),
            "key_pqc": len(self.theta_k),
            "value_pqc": len(self.theta_v),
            "classifier": len(self.w_fc) + 1,
            "encoder_data_angles_per_word": VEC_DIM,
            "total_trainable": self.total_params(),
        }

    def forward(self, X, theta_q, theta_k, theta_v, w_fc, b_fc):
        S = X.shape[0]
        
        # 1. Compute Quantum Query & Key scalar measurements
        Z_q = pnp.array([query_qnode(X[s], theta_q) for s in range(S)])
        Z_k = pnp.array([key_qnode(X[j], theta_k) for j in range(S)])

        # 2. Compute Value vectors o_j for each word
        O_v = pnp.array([value_qnode(X[j], theta_v) for j in range(S)])

        # 3. Gaussian Distance Attention Kernel (Eq. 7): alpha_{s,j} = exp( - (<Z_q>_s - <Z_k>_j)^2 )
        attn_list = []
        for s in range(S):
            row = []
            for j in range(S):
                diff = Z_q[s] - Z_k[j]
                row.append(pnp.exp(-(diff**2)))
            attn_list.append(row)
        attn_matrix = pnp.array(attn_list)

        # Row normalization in Eq. (7); this is not another softmax.
        row_sums = pnp.sum(attn_matrix, axis=1, keepdims=True)
        norm_attn = attn_matrix / row_sums

        # 4. Residual Output update (Eq. 6): y_s^{(1)} = y_s^{(0)} + sum_j alpha_{s,j} * o_j
        V_attn = norm_attn @ O_v
        Y_out = X + V_attn

        # 5. Pooling & Fully-Connected Output Prediction
        mean_pooled = pnp.mean(Y_out, axis=0)
        logit = pnp.dot(mean_pooled, w_fc) + b_fc
        pred = 1.0 / (1.0 + pnp.exp(-logit))

        return Y_out, norm_attn, pred

qsann = QuantumSelfAttention()
qsann_y, qsann_attn, qsann_pred = qsann.forward(
    X_input, qsann.theta_q, qsann.theta_k, qsann.theta_v, qsann.w_fc, qsann.b_fc
)

print("QUANTUM SELF-ATTENTION (QSANN / GPQSA) RESULT:")
qsann_param_breakdown = qsann.parameter_breakdown()
print(
    "Q/K/V Trainable Parameters: "
    f"{qsann_param_breakdown['query_pqc']} + "
    f"{qsann_param_breakdown['key_pqc']} + "
    f"{qsann_param_breakdown['value_pqc']} = "
    f"{3 * PARAMS_PER_ANSATZ}"
)
print(f"Classifier Parameters: {qsann_param_breakdown['classifier']}")
print(
    "Encoder Data Angles per Word: "
    f"{qsann_param_breakdown['encoder_data_angles_per_word']} "
    "(input data; not trainable parameters)"
)
print(f"Total Parameters: {qsann.total_params()}")
parameter_reduction = 100.0 * (
    csann.num_parameters() - qsann.total_params()
) / csann.num_parameters()
print(
    "Parameter Comparison: "
    f"CSANN {csann.num_parameters()} vs QSANN {qsann.total_params()} "
    f"({parameter_reduction:.1f}% fewer trainable parameters)"
)
print("Quantum Gaussian Projected Self-Attention Matrix (GPQSA):")
print(qsann_attn)
print(f"Predicted Probability: {float(qsann_pred):.4f}")
print("-" * 70)
print()

# ==========================================
# 4. GENERATING GRAPHICAL CIRCUIT NOTATIONS & HEATMAPS
# ==========================================
print("GENERATING QISKIT CIRCUIT DIAGRAMS & HEATMAPS FOR SLIDES...")

def qiskit_ring_entanglement(circuit):
    """Append the same CNOT ring used by the executable PennyLane model."""
    if NUM_QUBITS < 2:
        return
    for q in range(NUM_QUBITS):
        circuit.cx(q, (q + 1) % NUM_QUBITS)


def build_qiskit_encoder_box():
    """Create the H + U_enc(x_s) body with symbolic embedding angles."""
    encoder = QuantumCircuit(NUM_QUBITS, name="State preparation")
    x_angles = ParameterVector("x", VEC_DIM)

    for q in range(NUM_QUBITS):
        encoder.h(q)

    idx = 0
    for q in range(NUM_QUBITS):
        encoder.rx(x_angles[idx], q)
        idx += 1
    for q in range(NUM_QUBITS):
        encoder.ry(x_angles[idx], q)
        idx += 1
    for _ in range(ENCODER_LAYERS):
        qiskit_ring_entanglement(encoder)
        for q in range(NUM_QUBITS):
            encoder.ry(x_angles[idx], q)
            idx += 1

    return encoder


def build_qiskit_pqc_box(parameter_name):
    """Create U_q/U_k/U_v with symbolic trainable angles."""
    pqc = QuantumCircuit(NUM_QUBITS, name=parameter_name)
    theta = ParameterVector(parameter_name, PARAMS_PER_ANSATZ)

    idx = 0
    for q in range(NUM_QUBITS):
        pqc.rx(theta[idx], q)
        idx += 1
    for q in range(NUM_QUBITS):
        pqc.ry(theta[idx], q)
        idx += 1
    for _ in range(ANSATZ_LAYERS):
        qiskit_ring_entanglement(pqc)
        for q in range(NUM_QUBITS):
            pqc.ry(theta[idx], q)
            idx += 1

    return pqc


def build_qiskit_query_circuit():
    """Query circuit: state preparation -> trainable U_q -> Z measurement."""
    qubits = QuantumRegister(NUM_QUBITS, "q")
    z_query = ClassicalRegister(1, "z_query")
    circuit = QuantumCircuit(qubits, z_query, name="QSANN Query")

    encoder = build_qiskit_encoder_box()
    query_pqc = build_qiskit_pqc_box("theta_q")
    circuit.box(
        encoder,
        list(qubits),
        [],
        label="1. H + U_enc(x_s): embedding -> |psi_s>",
    )
    circuit.box(
        query_pqc,
        list(qubits),
        [],
        label="2. Trainable PQC U_q(theta_q)",
    )
    circuit.barrier(*qubits, label="3. Measure Z on q[0]")
    circuit.measure(qubits[0], z_query[0])
    return circuit


def build_qiskit_value_circuit():
    """Show the three separate measurement settings needed for Z/X/Y values."""
    q_z = QuantumRegister(NUM_QUBITS, "z_basis")
    q_x = QuantumRegister(NUM_QUBITS, "x_basis")
    q_y = QuantumRegister(NUM_QUBITS, "y_basis")
    c_z = ClassicalRegister(NUM_QUBITS, "measure_z")
    c_x = ClassicalRegister(NUM_QUBITS, "measure_x")
    c_y = ClassicalRegister(NUM_QUBITS, "measure_y")
    circuit = QuantumCircuit(q_z, q_x, q_y, c_z, c_x, c_y, name="QSANN Value")

    encoder = build_qiskit_encoder_box()
    value_pqc = build_qiskit_pqc_box("theta_v")

    # Z, X, and Y do not commute, so these registers represent three separate
    # executions of the same U_enc + U_v circuit with shared parameters.
    measurement_settings = (
        (q_z, c_z, "Z basis", ()),
        (q_x, c_x, "X basis", ("h",)),
        (q_y, c_y, "Y basis", ("sdg", "h")),
    )

    for qreg, creg, basis_label, basis_rotations in measurement_settings:
        circuit.box(
            encoder,
            list(qreg),
            [],
            label="1. H + U_enc(x_s)",
        )
        circuit.box(
            value_pqc,
            list(qreg),
            [],
            label="2. Trainable PQC U_v(theta_v)",
        )
        circuit.barrier(*qreg, label=f"3. {basis_label} measurement")
        for rotation in basis_rotations:
            for qubit in qreg:
                getattr(circuit, rotation)(qubit)
        circuit.measure(qreg, creg)

    return circuit


QISKIT_DRAW_STYLE = {
    "name": "iqp",
    "backgroundcolor": "#FFFFFF",
    "fontsize": 11,
    "subfontsize": 8,
}


def add_qiskit_query_stage_headers(fig):
    """Add visible headers above Qiskit's otherwise unlabeled red boxes."""
    fig.set_size_inches(16, 4.8)
    fig.subplots_adjust(top=0.62, bottom=0.17)

    header_style = {
        "ha": "center",
        "va": "center",
        "fontsize": 11,
        "fontweight": "bold",
        "color": "#202124",
    }

    fig.text(
        0.25,
        0.78,
        "1. DATA ENCODING / STATE PREPARATION\n"
        r"$H + U_{enc}(x_s):$ embedding $\rightarrow |\psi_s\rangle$"
        "\n(data angles; not trainable)",
        bbox={
            "boxstyle": "round,pad=0.45",
            "facecolor": "#D9EFFA",
            "edgecolor": "#FF4D5A",
            "linewidth": 1.8,
        },
        **header_style,
    )
    fig.text(
        0.59,
        0.78,
        "2. QUERY ANSATZ / TRAINABLE PQC\n"
        r"$U_q(\theta_q):$ learns the query feature"
        "\n(theta_q is optimized during training)",
        bbox={
            "boxstyle": "round,pad=0.45",
            "facecolor": "#FFF0C7",
            "edgecolor": "#FF4D5A",
            "linewidth": 1.8,
        },
        **header_style,
    )

try:
    if not QISKIT_DRAWING_AVAILABLE:
        raise ImportError(
            "Qiskit drawing imports are unavailable. Install the visualization "
            "extras with: pip install 'qiskit[visualization]'"
        ) from QISKIT_IMPORT_ERROR

    # 1. Query: one Z expectation value on q[0].
    query_circuit = build_qiskit_query_circuit()
    fig = circuit_drawer(
        query_circuit,
        output="mpl",
        style=QISKIT_DRAW_STYLE,
        fold=-1,
        scale=0.85,
        plot_barriers=True,
        cregbundle=False,
        barrier_label_len=32,
    )
    add_qiskit_query_stage_headers(fig)
    fig.suptitle("QSANN Query Circuit - Qiskit", fontsize=14, fontweight="bold", y=0.97)
    query_img_path = FIGURES_DIR / "qsann_circuit_query.png"
    fig.savefig(query_img_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f" Saved Qiskit Query Circuit diagram: {query_img_path}")

    # 2. Value: separate Z/X/Y settings, each using the same circuit parameters.
    value_circuit = build_qiskit_value_circuit()
    fig = circuit_drawer(
        value_circuit,
        output="mpl",
        style=QISKIT_DRAW_STYLE,
        fold=-1,
        scale=0.72,
        plot_barriers=True,
        cregbundle=False,
        barrier_label_len=32,
    )
    fig.suptitle(
        "QSANN Value Circuit - separate Z/X/Y measurement settings",
        fontsize=14,
        fontweight="bold",
    )
    value_img_path = FIGURES_DIR / "qsann_circuit_value.png"
    fig.savefig(value_img_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f" Saved Qiskit Value Circuit diagram: {value_img_path}")

except Exception as e:
    print(f"Could not generate Qiskit circuit diagrams: {e}")
    print("Install the drawing dependency with: pip install 'qiskit[visualization]'")

print("-" * 70)
print()

# ==========================================
# 5. FIXED AUTOGRAD TRAINING LOOP (OPTIMIZATION)
# ==========================================
print("RUNNING TRAINING LOOP (10 EPOCHS) WITH PENNYLANE AUTOGRAD...")
target_label = pnp.array(1.0, requires_grad=False)

opt = qml.GradientDescentOptimizer(stepsize=0.3)

theta_q = pnp.copy(qsann.theta_q)
theta_k = pnp.copy(qsann.theta_k)
theta_v = pnp.copy(qsann.theta_v)
w_fc = pnp.copy(qsann.w_fc)
b_fc = pnp.copy(qsann.b_fc)

def loss_func(t_q, t_k, t_v, w, b):
    _, _, pred = qsann.forward(X_input, t_q, t_k, t_v, w, b)
    return (pred - target_label)**2

params = (theta_q, theta_k, theta_v, w_fc, b_fc)

print(f"{'Epoch':<10} | {'Loss (MSE)':<15} | {'Prediction':<15}")
print("-" * 45)

for epoch in range(1, 11):
    params, cost = opt.step_and_cost(loss_func, *params)
    _, _, current_pred = qsann.forward(X_input, params[0], params[1], params[2], params[3], params[4])
    print(f"{epoch:<10} | {float(cost):<15.6f} | {float(current_pred):<15.4f}")

# Store trained quantum results
_, qsann_trained_attn, qsann_trained_pred = qsann.forward(
    X_input, params[0], params[1], params[2], params[3], params[4]
)
print(f"\nQuantum Trained Attention Matrix:")
print(qsann_trained_attn)
print("-" * 70)
print()

# ==========================================
# 6. POST-TRAINING ATTENTION HEATMAP COMPARISON
# ==========================================
print("GENERATING POST-TRAINING ATTENTION HEATMAP...")
try:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    im1 = ax1.imshow(csann_trained_attn, cmap="YlGnBu", vmin=0, vmax=1)
    ax1.set_title("Classical Self-Attention (Trained)")
    ax1.set_xticks(range(NUM_WORDS))
    ax1.set_yticks(range(NUM_WORDS))
    ax1.set_xticklabels(WORD_LABELS, rotation=45, ha="right")
    ax1.set_yticklabels(WORD_LABELS)
    for i in range(NUM_WORDS):
        for j in range(NUM_WORDS):
            ax1.text(j, i, f"{csann_trained_attn[i, j]:.2f}", ha="center", va="center", color="black", fontsize=8)

    qsann_attn_np = np.array(qsann_trained_attn)
    im2 = ax2.imshow(qsann_attn_np, cmap="OrRd", vmin=0, vmax=1)
    ax2.set_title("Quantum GPQSA (Trained)")
    ax2.set_xticks(range(NUM_WORDS))
    ax2.set_yticks(range(NUM_WORDS))
    ax2.set_xticklabels(WORD_LABELS, rotation=45, ha="right")
    ax2.set_yticklabels(WORD_LABELS)
    for i in range(NUM_WORDS):
        for j in range(NUM_WORDS):
            ax2.text(j, i, f"{qsann_attn_np[i, j]:.2f}", ha="center", va="center", color="black", fontsize=8)

    plt.suptitle("Post-Training Attention: Classical vs Quantum GPQSA", fontsize=14)
    plt.tight_layout()
    heatmap_img_path = FIGURES_DIR / "attention_comparison.png"
    fig.savefig(heatmap_img_path, dpi=300)
    plt.close(fig)
    print(f" Saved Heatmap PNG: {heatmap_img_path}")
except Exception as e:
    print(f"Could not generate heatmap: {e}")

print("="*70)
print("  QSANN DEMO COMPLETED SUCCESSFULLY!")
print("="*70)
