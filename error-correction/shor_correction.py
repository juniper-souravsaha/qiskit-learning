from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import random

# Define registers
q = QuantumRegister(15, 'q')     # 9 data + 6 ancilla
c = ClassicalRegister(3, 'c')    # Logical qubit measurement
qc = QuantumCircuit(q, c)

# --- Encoding: Logical |1⟩ using Shor Code ---
qc.x(q[0])  # Encode logical |1⟩
qc.cx(q[0], q[3])
qc.cx(q[0], q[6])

# Hadamard for phase encoding
for i in [0, 3, 6]:
    qc.h(q[i])

# Phase flip protection (3 times repetition)
for i, j, k in [(0,1,2), (3,4,5), (6,7,8)]:
    qc.cx(i, j)
    qc.cx(i, k)

qc.barrier()

# --- Inject Random Error ---
error_qubit = random.randint(0, 8)
error_type = random.choice(['x', 'z'])
print(f"Injecting {error_type.upper()} error on qubit {error_qubit}")
if error_type == 'x':
    qc.x(q[error_qubit])
else:
    qc.z(q[error_qubit])
qc.barrier()

# --- Phase Flip Error Detection using ancilla q[9], q[10], q[11] ---
for block_start, anc in zip([0, 3, 6], [9, 10, 11]):
    for i in range(3):
        qc.cx(q[block_start + i], anc)
    for i in range(3):
        qc.h(q[block_start + i])
qc.barrier()

# --- Phase Flip Correction ---
qc.ccx(q[9], q[10], q[6])
qc.ccx(q[9], q[11], q[3])
qc.ccx(q[10], q[11], q[0])
qc.barrier()

# Undo Hadamard before bit flip correction
for i in [0, 3, 6]:
    qc.h(q[i])
qc.barrier()

# --- Bit Flip Error Detection using ancilla q[12], q[13], q[14] ---
for block_start, anc in zip([0, 3, 6], [12, 13, 14]):
    for i in range(3):
        qc.cx(q[block_start + i], anc)
qc.barrier()

# --- Bit Flip Correction ---
qc.ccx(q[12], q[13], q[6])
qc.ccx(q[12], q[14], q[3])
qc.ccx(q[13], q[14], q[0])
qc.barrier()

# --- Final Measurement of logical qubit ---
qc.measure(q[0], c[0])
qc.measure(q[3], c[1])
qc.measure(q[6], c[2])
qc.draw('mpl', scale=0.5, style='iqx')

# --- Run the circuit ---
simulator = AerSimulator()
tqc = transpile(qc, simulator)
result = simulator.run(tqc, shots=1024).result()
counts = result.get_counts()

# --- Show Results ---
plot_histogram(counts)
plt.title("Shor 9-Qubit Code: Logical Output After Error Correction")
plt.show()

print("Counts:", counts)