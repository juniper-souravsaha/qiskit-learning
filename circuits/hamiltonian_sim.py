import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector, Pauli, SparsePauliOp
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import state_fidelity
import matplotlib.pyplot as plt

# Define Hamiltonian: {"XZX": 2, "ZYI": 5, "IYZ": 7}
hamiltonian_dict = {
    "XZX": 2,
    "ZYI": 5,
    "IYZ": 7
}
paulis = list(hamiltonian_dict.keys())
weights = list(hamiltonian_dict.values())

# Convert to SparsePauliOp
sparse_pauli_op = SparsePauliOp(paulis, coeffs=np.array(weights))

# Time of evolution
T = 1 / (2 * np.pi)

# Create PauliEvolutionGate for exact evolution
evolution_gate = PauliEvolutionGate(sparse_pauli_op, time=T)

# Initial state |000>
qr = QuantumRegister(3, "q")
qc_exact = QuantumCircuit(qr)
qc_exact.append(evolution_gate, qr[::-1])

# Simulate the circuit using statevector
state_exact = Statevector.from_instruction(qc_exact)

from hamiltonian_sim_cust import hamiltonian_simulation  # your code

qr2 = QuantumRegister(3, 'q')
qc_custom = hamiltonian_simulation(hamiltonian_dict, qr2, t=-T, trotter_number=1)

state_custom = Statevector.from_instruction(qc_custom)

# Fidelity comparison
fidelity = state_fidelity(state_custom, state_exact)

print("Fidelity between Trotterized and exact evolution:", fidelity)

# Optional: Show full statevectors
print("\nTrotterized:\n", state_custom)
print("\nExact:\n", state_exact)

qc_exact.decompose().draw("mpl")
plt.show()