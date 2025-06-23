from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# 1 coin qubit + 2 position qubits
n_steps = 3
qc = QuantumCircuit(3, name='quantum_walk')

def apply_coin(qc, coin):
    qc.h(coin)

def apply_shift(qc, coin, pos0, pos1):
    # Shift right if coin == 1
    qc.cx(coin, pos0)
    qc.cx(coin, pos1)

    # Shift left if coin == 0 (simulate via X-coin and reuse)
    qc.x(coin)
    qc.cx(coin, pos0)
    qc.cx(coin, pos1)
    qc.x(coin)

# Initial state: |0⟩_pos ⊗ |1⟩_coin (coin in |1⟩)
qc.x(0)  # Set coin to |1⟩

for _ in range(n_steps):
    apply_coin(qc, 0)
    apply_shift(qc, 0, 1, 2)

# Get final statevector
state = Statevector.from_instruction(qc)
counts = state.probabilities_dict()

# Plot probabilities of position+coin
plot_histogram(counts)
plt.title(f"{n_steps}-step Quantum Walk (DTQW)")
plt.show()