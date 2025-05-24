import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_state_city
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt

def qft_rotations(circuit, n):
    if n == 0:
        return
    n -= 1
    circuit.h(n)
    for qubit in range(n):
        circuit.cp(np.pi / 2**(n - qubit), qubit, n)
    qft_rotations(circuit, n)

def swap_registers(circuit, n):
    for qubit in range(n // 2):
        circuit.swap(qubit, n - qubit - 1)

def qft(circuit, n):
    qft_rotations(circuit, n)
    swap_registers(circuit, n)
    return circuit

def prepare_qft_basis_state(nqubits, k):
    """Prepares a QFT basis state |ψ_k⟩ for k in 0..2^n-1"""
    qc = QuantumCircuit(nqubits)
    binary_k = f"{k:0{nqubits}b}"  # Binary string with leading zeros

    for i in range(nqubits):
        qc.h(i)
        phase = 0
        for j in range(i, nqubits):
            if binary_k[j] == '1':
                phase += 1 / (2 ** (j - i + 1))
        qc.p(2 * np.pi * phase, i)
    
    return qc

def inverse_qft(circuit, n):
    qft_circ = qft(QuantumCircuit(n), n)
    qft_circ.draw("mpl")
    inv_qft = qft_circ.inverse()
    circuit.append(inv_qft, circuit.qubits[:n])
    return circuit.decompose()

# ----- MAIN -----
n_qubits = 3
number = 5

# qft circuit
qc = prepare_qft_basis_state(n_qubits, number)
# qc.draw("mpl")

# Apply inverse QFT
qc = inverse_qft(qc, n_qubits)
# qc.measure_all()
qc.draw("mpl")
# Save statevector
qc.save_statevector()

# Simulate
sim = AerSimulator(method='statevector')
tqc = transpile(qc, sim)
# result = sim.run(tqc).result()
# state = result.get_statevector()

# Visualize
# plot_state_city(state, title=f"Statevector after inverse QFT (encoded {number})")
plt.show()

result = sim.run(tqc, shots=1024).result()
counts = result.get_counts()
print(counts)



# def qft(n):
#     qc = QuantumCircuit(n)
#     for i in range(n):
#         qc.h(i)
#         for j in range(i+1, n):
#             qc.cp(pi / (2 ** (j - i)), j, i)
#     qc.reverse_bits()
#     return qc