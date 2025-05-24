from qiskit import QuantumCircuit, ClassicalRegister, transpile
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
from data.const import DEFAULT_SHOTS

# Create quantum and classical registers
qc = QuantumCircuit(5, 3)
# Step 1: Encode logical qubit into 3 physical qubits (|+⟩)
qc.h(0)             # Create (|0⟩ + |1⟩)/√2
qc.cx(0, 1)
qc.cx(0, 2)

# Step 2: Simulate a bit-flip error on qubit 1
qc.x(1)

# Step 3: Syndrome extraction using ancilla qubits 3 and 4
qc.cx(0, 3)
qc.cx(1, 3)
qc.cx(1, 4)
qc.cx(2, 4)

# Step 4: Measure syndrome bits into classical bits 0 and 1
qc.measure(3, 0)  # syndrome bit s1
qc.measure(4, 1)  # syndrome bit s2

# Step 5: Conditional correction based on syndrome
with qc.if_test((qc.clbits[0], 1)):
    with qc.if_test((qc.clbits[1], 0)):
        qc.x(2)  # syndrome 01 → fix qubit 2

with qc.if_test((qc.clbits[0], 0)):
    with qc.if_test((qc.clbits[1], 1)):
        qc.x(0)  # syndrome 10 → fix qubit 0

with qc.if_test((qc.clbits[0], 1)):
    with qc.if_test((qc.clbits[1], 1)):
        qc.x(1)  # syndrome 11 → fix qubit 1

# Step 6: Decode (optional) and final measurement of logical qubit
qc.cx(0, 1)
qc.cx(0, 2)
qc.h(0)

# Final measurement of logical qubit
qc.measure(0, 2)
qc.draw('mpl', scale=0.5, style='iqx')
# Simulate circuit
sim = AerSimulator()
tqc = transpile(qc, sim)
result = sim.run(tqc, shots=DEFAULT_SHOTS).result()
counts = result.get_counts()

# Plot result
plot_histogram(counts)
plt.title("Bit Flip Code: Final Logical Qubit Measurement")
plt.show()

print("Counts:", counts)