import random
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from data.const import DEFAULT_SHOTS

# Randomly select a qubit to flip (0, 1, 2) or None for no error
error_qubit = random.choice([0, 1, 2, None])
print(f"Phase flip applied on qubit: {error_qubit}" if error_qubit is not None else "No error applied.")

# Quantum and classical registers
qreg = QuantumRegister(5, 'q')      # 3 data qubits + 2 ancilla for syndrome
creg = ClassicalRegister(3, 'c')    # 2 bits for syndrome + 1 for final measurement
qc = QuantumCircuit(qreg, creg)

# Step 1: Encode logical qubit |+> as (|+++⟩)
qc.h(qreg[0])       # |+⟩ = H|0⟩
qc.cx(qreg[0], qreg[1])
qc.cx(qreg[0], qreg[2])

# Step 2: Apply random phase flip error if selected
if error_qubit is not None:
    qc.z(qreg[error_qubit])

# Step 3: Transform to bit-flip code using Hadamard basis
qc.h(qreg[0])
qc.h(qreg[1])
qc.h(qreg[2])

# Step 4: Syndrome extraction using ancilla qubits
qc.cx(qreg[0], qreg[3])
qc.cx(qreg[1], qreg[3])
qc.cx(qreg[1], qreg[4])
qc.cx(qreg[2], qreg[4])

# Step 5: Measure the ancillas to extract error syndrome
qc.measure(qreg[3], creg[0])  # syndrome bit 1
qc.measure(qreg[4], creg[1])  # syndrome bit 2

# Step 6: Conditional correction based on measured syndrome
# Correction map:
# 10 -> Z on qubit 0
# 11 -> Z on qubit 1
# 01 -> Z on qubit 2

with qc.if_test((creg, 2)):  # binary 10
    qc.z(qreg[0])

with qc.if_test((creg, 3)):  # binary 11
    qc.z(qreg[1])

with qc.if_test((creg, 1)):  # binary 01
    qc.z(qreg[2])

# Step 7: Undo the basis change (Hadamard)
qc.h(qreg[0])
qc.h(qreg[1])
qc.h(qreg[2])

# Step 8: Decode (reverse of encoding)
qc.cx(qreg[0], qreg[1])
qc.cx(qreg[0], qreg[2])
qc.h(qreg[0])

# Step 9: Final measurement of the logical qubit
qc.measure(qreg[0], creg[2])  # final result in classical bit 2
qc.draw('mpl', scale=0.5, style='iqx')

# Simulation
sim = AerSimulator()
tqc = transpile(qc, sim)
result = sim.run(tqc, shots=DEFAULT_SHOTS).result()
counts = result.get_counts()

# Plot result
plot_histogram(counts)
plt.title("Phase Flip Code: Final Logical Qubit Measurement")
plt.show()

# Note: In Qiskit, the bitstring is shown in reverse order of classical registers, i.e., 'abc' really means [c2, c1, c0]
# So, the bit string 'abc' corresponds to:
# a = c0 (syndrome 1)
# b = c1 (syndrome 2)
# c = final logical measurement (0 or 1)
print("Measurement counts:", counts)