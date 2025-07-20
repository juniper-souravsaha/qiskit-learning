import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import Estimator
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Define Hamiltonian: H = ZZ + XI
hamiltonian = SparsePauliOp(["ZZ", "XI"], coeffs=[1.0, 1.0])

# Define variational ansatz
theta1 = Parameter("θ1")
theta2 = Parameter("θ2")

ansatz = QuantumCircuit(2)
ansatz.ry(theta1, 0)
ansatz.ry(theta2, 1)
ansatz.cx(0, 1)

estimator = Estimator()

# Track energy over iterations
energy_history = []

def energy_expectation(params):
    bound_circuit = ansatz.assign_parameters({theta1: params[0], theta2: params[1]}, inplace=False)
    job = estimator.run(
        circuits=[bound_circuit],
        observables=[hamiltonian],
        parameter_values=[[]]
    )
    energy = job.result().values[0]
    energy_history.append(energy)
    return energy

# Initial parameters
initial_params = [0.1, 0.1]

# Run classical optimization
result = minimize(energy_expectation, initial_params, method="COBYLA")

# Print result
print(f"\nOptimal parameters: θ1 = {result.x[0]:.4f}, θ2 = {result.x[1]:.4f}")
print(f"Estimated ground state energy: {result.fun:.6f}")

# Plot energy over iterations
plt.figure(figsize=(8, 5))
plt.plot(energy_history, marker='o')
plt.title("VQE: Energy vs Iteration")
plt.xlabel("Iteration")
plt.ylabel("Energy")
plt.grid(True)
plt.tight_layout()
plt.show()