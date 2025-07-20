import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import XGate, ZGate
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_bloch_multivector

# --- Step 1: Define the LCU Hamiltonian ---
# H = 0.5 * X + 0.5 * Z
coeffs = [0.5, 0.5]
units = [XGate(), ZGate()]  # Corresponding unitaries

# --- Step 2: Setup Quantum Registers ---
anc = QuantumRegister(1, name='anc')     # Ancilla qubit
sys = QuantumRegister(1, name='q')       # System qubit
cl = ClassicalRegister(1, name='c')      # Classical bit for ancilla

qc = QuantumCircuit(anc, sys, cl)

# --- Step 3: Prepare Ancilla Superposition (based on coeffs) ---
qc.h(anc[0])  # Creates (|0⟩ + |1⟩)/√2 for equal weights

# --- Step 4: Controlled-U operations (controlled-X and controlled-Z) ---
# Apply controlled-X (acts when anc=0)
qc.cx(anc[0], sys[0])

# Apply controlled-Z (via HZH = X)
qc.h(sys[0])           # HZH = X
qc.cx(anc[0], sys[0])
qc.h(sys[0])

# --- Step 5: Uncompute Ancilla Superposition ---
qc.h(anc[0])  # Reverse the initial superposition

# --- Step 6: Measure ancilla to postselect for anc=0 ---
qc.measure(anc[0], cl[0])

# --- Step 7: Simulate the Circuit ---
qc.save_statevector()
simulator = AerSimulator()
result = simulator.run(qc).result()
counts = result.get_counts()
print("Measurement counts (postselection on ancilla=0):", counts)

# --- Step 8: Extract final statevector and reduce to system qubit only ---
statevec = result.data()['statevector']
statevector = Statevector(statevec)

# Convert to density matrix and trace out ancilla
dm_full = DensityMatrix(statevector)
dm_system = partial_trace(dm_full, [0])  # Trace out ancilla (qubit index 0)

# --- Step 9: Print and visualize ---
print("\nFinal (postselected) system state (as DensityMatrix):")
print(dm_system)

# Plot Bloch vector of the system qubit
plot_bloch_multivector(dm_system)
plt.show()