import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt

# --- XOR helper gate: computes XOR of a, b into output ---
def XOR(qc, a, b, output):
    qc.cx(a, output)
    qc.cx(b, output)

# --- Oracle: Flips output qubit if all XOR clauses are satisfied ---
def sudoku_oracle(qc, var_qubits, clause_qubits, output_qubit, clause_list):
    # Compute clause results into ancillae
    for i, (q1, q2) in enumerate(clause_list):
        XOR(qc, var_qubits[q1], var_qubits[q2], clause_qubits[i])
    
    # Flip output if all clauses satisfied
    qc.mcx(clause_qubits, output_qubit)
    
    # Uncompute to reset clause ancillae
    for i, (q1, q2) in enumerate(clause_list):
        XOR(qc, var_qubits[q1], var_qubits[q2], clause_qubits[i])

# --- Grover diffuser: Reflects about mean amplitude ---
def diffuser(qubits):
    qc = QuantumCircuit(len(qubits))
    for i in range(len(qubits)):
        qc.h(i)
    for i in range(len(qubits)):
        qc.x(i)
    qc.h(len(qubits) - 1)
    qc.mcx(list(range(len(qubits) - 1)), len(qubits) - 1)
    qc.h(len(qubits) - 1)
    for i in range(len(qubits)):
        qc.x(i)
    for i in range(len(qubits)):
        qc.h(i)
    return qc.to_gate(label="Diffuser")

# --- Grover circuit builder ---
def build_grover_circuit(clause_list, num_iterations=2):
    num_vars = 4
    num_clauses = len(clause_list)

    var_qubits = QuantumRegister(num_vars, name='v')       # Variable qubits
    clause_qubits = QuantumRegister(num_clauses, name='c') # Clause ancillae
    output_qubit = QuantumRegister(1, name='out')          # Output flag qubit
    cbits = ClassicalRegister(num_vars, name='cbits')      # Classical bits

    qc = QuantumCircuit(var_qubits, clause_qubits, output_qubit, cbits)

    # Initialize output qubit to |-⟩ = H • X |1⟩
    qc.initialize([1, -1]/np.sqrt(2), output_qubit)
    
    # Initialize variable qubits in superposition
    qc.h(var_qubits)
    qc.barrier()

    # Perform Grover iterations
    for _ in range(num_iterations):
        sudoku_oracle(qc, var_qubits, clause_qubits, output_qubit[0], clause_list)
        qc.barrier()
        qc.append(diffuser(list(var_qubits)), var_qubits)
        qc.barrier()
    
    # Measure
    qc.measure(var_qubits, cbits)
    return qc

# --- Simulate and visualize ---
def simulate_and_plot(qc, shots=1024):
    backend = AerSimulator()
    tqc = transpile(qc, backend)
    result = backend.run(tqc, shots=shots).result()
    counts = result.get_counts()
    plot_histogram(counts)
    plt.show()
    return counts

# --- Main Execution ---
if __name__ == "__main__":
    # clause_list = [[0, 1], [0, 2], [1, 3], [2, 3]]  # XOR constraints
    clause_list = [[0, 1], [1, 2], [2, 3], [0, 3]]
    qc = build_grover_circuit(clause_list, num_iterations=2)
    counts = simulate_and_plot(qc)
    print(counts)