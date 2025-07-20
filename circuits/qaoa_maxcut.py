import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import Estimator  # Compatible with BaseEstimatorV2
from scipy.optimize import minimize

# -- Max-Cut graph: triangle --
edges = [(0, 1), (1, 2), (0, 2)]
n_qubits = 3

# -- Construct Max-Cut Hamiltonian: H = ∑ (1 - Zi Zj)/2 --
hamiltonian = sum(
    0.5 * (SparsePauliOp("I" * i + "Z" + "I" * (j - i - 1) + "Z" + "I" * (n_qubits - j - 1), coeffs=[-1])
           + SparsePauliOp("I" * n_qubits, coeffs=[1]))
    for i, j in edges
)

# -- QAOA ansatz circuit with depth p=1 --
beta = Parameter("β")
gamma = Parameter("γ")
qr = QuantumRegister(n_qubits)
qc = QuantumCircuit(qr)

# Hadamards
qc.h(qr)

# Cost unitary
for i, j in edges:
    qc.cx(qr[i], qr[j])
    qc.rz(-2 * gamma, qr[j])
    qc.cx(qr[i], qr[j])

# Mixer unitary
for i in range(n_qubits):
    qc.rx(2 * beta, qr[i])

# -- Estimator --
estimator = Estimator()

energy_history = []
param_history = []

def energy_expectation(params):
    b, g = params
    job = estimator.run(
        circuits=[qc],
        observables=[hamiltonian],
        parameter_values=[[b, g]]
    )
    energy = job.result().values[0]
    energy_history.append(energy)
    param_history.append((b, g))
    return energy

# -- Optimization --
x0 = [0.1, 0.1]
res = minimize(energy_expectation, x0, method="COBYLA")

print("\nOptimal β, γ:", res.x)
print("Minimum energy:", res.fun)

# -- Plot energy over iterations --
plt.plot(energy_history, marker="o")
plt.xlabel("Iteration")
plt.ylabel("Energy")
plt.title("QAOA Energy Optimization")
plt.grid(True)
plt.show()

from qiskit_aer import AerSimulator
from qiskit import transpile
from qiskit.visualization import plot_histogram

# -- Bind optimal parameters to the circuit --
opt_qc = qc.assign_parameters({beta: res.x[0], gamma: res.x[1]}, inplace=False)

# -- Transpile and simulate --
simulator = AerSimulator()
t_qc = transpile(opt_qc.measure_all(inplace=False), simulator)
result = simulator.run(t_qc, shots=1000).result()
counts = result.get_counts()


# Define cost function (Max-Cut size) for each bitstring
def maxcut_value(bitstring, edges):
    cost = 0
    for i, j in edges:
        if bitstring[i] != bitstring[j]:
            cost += 1
    return cost

# Compute Max-Cut values
cut_scores = {k: maxcut_value(k[::-1], edges) for k in counts}

# Display counts
print("Measurement Results:")
for k, v in sorted(counts.items(), key=lambda item: -item[1]):
    print(f"{k}: {v} shots, Max-Cut: {cut_scores[k]}")

# Color bars by Max-Cut value
colors = ['red' if cut_scores[k] < max(cut_scores.values()) else 'green' for k in counts]


# -- Plot histogram of bitstring results --
plot_histogram(counts, color=colors, title="QAOA Max-Cut Solution Probabilities")
plt.show()