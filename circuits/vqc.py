import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import Estimator
from scipy.optimize import minimize

# --- Step 1: Prepare dataset with 2 features ---
X, y = make_classification(n_samples=200, n_features=2, n_informative=2, n_redundant=0,
                           n_clusters_per_class=1, class_sep=2.0, random_state=42)
X = MinMaxScaler().fit_transform(X) * np.pi  # Normalize to [0, π]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

num_qubits = X.shape[1]

# --- Step 2: Define feature map (encode x with Ry) ---
def feature_map(x_val):
    qc = QuantumCircuit(num_qubits)
    for i in range(num_qubits):
        qc.ry(float(x_val[i]), i)
    return qc

# --- Step 3: Variational ansatz (with CZ entanglement) ---
def ansatz(theta_vals):
    qc = QuantumCircuit(num_qubits)
    for i in range(num_qubits):
        qc.ry(theta_vals[i], i)
    for i in range(num_qubits - 1):
        qc.cz(i, i + 1)
    return qc

# --- Step 4: Full circuit = feature map + ansatz ---
def construct_vqc(x_val, theta_vals):
    qc = QuantumCircuit(num_qubits)
    qc.compose(feature_map(x_val), inplace=True)
    qc.compose(ansatz(theta_vals), inplace=True)
    return qc

# --- Step 5: Objective function using MSE loss ---
estimator = Estimator()
observable = SparsePauliOp("Z" * num_qubits)

def objective(params):
    losses = []
    for xi, yi in zip(X_train, y_train):
        circuit = construct_vqc(xi, params)
        job = estimator.run(
            circuits=[circuit],
            observables=[observable],
        )
        expval = job.result().values[0]
        pred = (1 - expval) / 2  # map from [-1, 1] to [0, 1]
        losses.append((pred - yi) ** 2)
    return np.mean(losses)

# --- Step 6: Train the VQC ---
initial_params = np.random.rand(num_qubits)
res = minimize(objective, initial_params, method="COBYLA")
trained_params = res.x
print(f"✅ Trained parameters: {trained_params}")

# --- Step 7: Prediction function ---
def predict(x_val):
    circuit = construct_vqc(x_val, trained_params)
    job = estimator.run(
        circuits=[circuit],
        observables=[observable],
    )
    expval = job.result().values[0]
    return int((1 - expval) / 2 > 0.5)

# --- Step 8: Evaluate test accuracy ---
preds = [predict(xi) for xi in X_test]
accuracy = accuracy_score(y_test, preds)
print(f"✅ Test Accuracy: {accuracy:.2f}")