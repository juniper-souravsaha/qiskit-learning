from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram

from data.const import DEFAULT_SHOTS

def bernstein_vazirani(s: str) -> QuantumCircuit:
    n = len(s)
    qc = QuantumCircuit(n + 1, n)

    # Step 1: Initialize the ancilla in |1>
    qc.x(n)

    # Step 2: Apply Hadamard to all qubits
    qc.h(range(n + 1))

    s = s[::-1] # reverse s to fit qiskit's qubit ordering
    # Step 3: Apply the oracle U_f based on s
    for i, bit in enumerate(s):
        if bit == '1':
            qc.cx(i, n)

    # Step 4: Apply Hadamard to first n qubits
    qc.h(range(n))

    # Step 5: Measure first n qubits
    qc.measure(range(n), range(n))

    return qc

s = "1010"  # Hidden string
qc = bernstein_vazirani(s)
qc.draw('mpl')  # Optional: visualize

sim = AerSimulator()
tqc = transpile(qc, sim)
result = sim.run(tqc, shots=DEFAULT_SHOTS).result()
counts = result.get_counts()

print("Measurement:", counts)
plot_histogram(counts)
plt.show()