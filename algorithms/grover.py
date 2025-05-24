import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt

# --- Step 1: Initialize Superposition ---
def initialize_superposition(qc, qubits):
    qc.h(qubits)
    qc.barrier()
    return qc

# --- Step 2: Oracle for any target string ---
def grover_oracle(qc, target_string):
    n = len(target_string)
    qubits = list(range(n))
    
    # Flip qubits where target bit is '0'
    for i, bit in enumerate(target_string):
        if bit == '0':
            qc.x(i)
    
    # Multi-controlled-Z using H-MCX-H trick
    qc.h(n-1)
    qc.mcx(qubits[:-1], qubits[-1])
    qc.h(n-1)
    
    # Flip back
    for i, bit in enumerate(target_string):
        if bit == '0':
            qc.x(i)
    
    qc.barrier()
    return qc

# --- Step 3: Diffusion Operator (Generalized) ---
def diffuser(qc, qubits):
    n = len(qubits)
    
    qc.h(qubits)
    qc.x(qubits)
    
    qc.h(n-1)
    qc.mcx(qubits[:-1], qubits[-1])
    qc.h(n-1)
    
    qc.x(qubits)
    qc.h(qubits)
    
    qc.barrier()
    return qc

# --- Step 4: Build Full Grover Circuit ---
def build_grover_circuit(n_qubits, target_string, iterations=1):
    qc = QuantumCircuit(n_qubits)
    qubits = list(range(n_qubits))
    
    initialize_superposition(qc, qubits)
    
    for _ in range(iterations):
        build_grover_step(qc, target_string)
    
    qc.measure_all()
    return qc

# --- Grover Circuit per Iteration ---
def build_grover_step(qc, target_string):
    n = len(target_string)
    qubits = list(range(n))
    grover_oracle(qc, target_string)
    diffuser(qc, qubits)


# --- Step 5: Simulate and Plot Results ---
def simulate_and_plot(qc, shots=1024):
    backend = AerSimulator()
    job = backend.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts()
    # qc.draw('mpl')
    plot_histogram(counts)
    plt.show()
    
    return counts

# --- MAIN PROGRAM ---
if __name__ == "__main__":
    # n_qubits = 15
    # target = '101100101010111'
    n_qubits = 5
    target = '10111'
    iterations = 1  # 1 iteration is optimal if 1 solution (approximately)
    
    grover_circuit = build_grover_circuit(n_qubits, target, iterations)
    counts = simulate_and_plot(grover_circuit)
    print(counts)

# def simulate(qc, shots=1024):
#     backend = AerSimulator()
#     job = backend.run(qc, shots=shots)
#     result = job.result()
#     counts = result.get_counts()
#     return counts

# # --- Animate Grover Iterations ---
# def animate_grover(target_string, max_iterations=10, shots=1024):
#     n_qubits = len(target_string)
#     qubits = list(range(n_qubits))
    
#     qc = QuantumCircuit(n_qubits)
#     initialize_superposition(qc, qubits)
    
#     counts_list = []
#     circuit_snapshots = [qc.copy()]  # Save initial superposition
    
#     for _ in range(max_iterations):
#         build_grover_step(qc, target_string)
#         circuit_snapshots.append(qc.copy())  # Save after each iteration

#     # Simulate and collect counts for each step
#     for snapshot in circuit_snapshots:
#         snapshot.measure_all()
#         counts = simulate(snapshot, shots=shots)
#         counts_list.append(counts)
#         snapshot.data.pop()  # Remove measurement for next snapshot
    
#     # Animation
#     for i, counts in enumerate(counts_list):
#         plt.figure(figsize=(10,6))
#         plot_histogram(counts, title=f"Grover iteration {i}")
#         plt.show()

# # # --- MAIN ---
# # if __name__ == "__main__":
# #     target = '1011'  # 4 qubits example
# #     animate_grover(target, max_iterations=5)

# def make_oracle(qc, marked_states):
#     n = qc.num_qubits
#     for state in marked_states:
#         # Flip qubits according to |state>
#         for i, bit in enumerate(reversed(state)):
#             if bit == '0':
#                 qc.x(i)
#         qc.h(n-1)  # target qubit
#         qc.mcx(list(range(n-1)), n-1)  # multi-controlled X
#         qc.h(n-1)
#         for i, bit in enumerate(reversed(state)):
#             if bit == '0':
#                 qc.x(i)
#     return qc

# def make_diffuser(n):
#     qc = QuantumCircuit(n)
#     qc.h(range(n))
#     qc.x(range(n))
#     qc.h(n-1)
#     qc.mcx(list(range(n-1)), n-1)
#     qc.h(n-1)
#     qc.x(range(n))
#     qc.h(range(n))
#     qc.name = "Diffuser"
#     return qc

# # --- MAIN ---
# if __name__ == "__main__":
#     n_qubits = 4
#     qc = QuantumCircuit(n_qubits)

#     # --------------- Initialize --------------
#     qc.h(range(n_qubits))  # Apply Hadamard to all qubits

#     # --------------- Oracle for multiple solutions --------------
#     oracle = make_oracle(QuantumCircuit(n_qubits), ['0011', '0100'])  # marked states
#     diff = make_diffuser(n_qubits)  # Diffuser should act on all qubits

#     # --------------- Grover Iterations --------------
#     grover_steps = int(np.pi / 4 * np.sqrt(2**n_qubits / len(['0011', '0100'])))
#     for _ in range(grover_steps):
#         qc.append(oracle.to_gate(), range(n_qubits))
#         qc.append(diff.to_gate(), range(n_qubits))

#     # --------------- Measurement --------------
#     qc.measure_all()

#     # --------------- Simulation --------------
#     simulator = AerSimulator()
#     tqc = transpile(qc, simulator)
#     result = simulator.run(tqc, shots=1024).result()
#     counts = result.get_counts()

#     # --------------- Result --------------
#     print(counts)
#     # plot_histogram(counts)
#     plt.show()