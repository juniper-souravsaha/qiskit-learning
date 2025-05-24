import matplotlib.pyplot as plt
import numpy as np
import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit.circuit.library import Diagonal, GroverOperator, QFT

def create_oracle():
    """
    Oracle represented as a diagonal matrix with -1 for marked states (5 out of 16).
    This encodes the function f(x) = 1 for the solutions.
    """
    phase_vector = [1,1,-1,1,1,1,1,-1,1,1,-1,-1,1,1,-1,1]  # 5 marked states
    return Diagonal(phase_vector)

def create_grover_operator(oracle, n_iterations):
    """
    Constructs repeated Grover operator using the given oracle.
    Grover operator is: G = D * O, where O is oracle and D is the diffuser.
    """
    grover_op = GroverOperator(oracle).repeat(n_iterations).to_gate()
    grover_op.label = f"Grover^{n_iterations}"
    return grover_op

def apply_controlled_grover(qc, oracle, t, n):
    """
    Applies controlled Grover iterations on the search register (n qubits),
    controlled by each of the counting register (t qubits).
    """
    n_iterations = 1
    for qubit in range(t):
        grover_gate = create_grover_operator(oracle, n_iterations)
        controlled_gate = grover_gate.control()
        qc.append(controlled_gate, [qubit] + list(range(t, t+n)))
        n_iterations *= 2

def quantum_counting_circuit(t, n):
    """
    Constructs full quantum counting circuit with:
    - t counting qubits
    - n search (oracle) qubits
    """
    oracle = create_oracle()
    qc = QuantumCircuit(t + n, t)

    # Step 1: Initialize all qubits to |+> state (Hadamards)
    qc.h(range(t + n))

    # Step 2: Apply controlled Grover iterations
    apply_controlled_grover(qc, oracle, t, n)

    # Step 3: Apply inverse QFT to counting qubits
    qft_dagger = QFT(t, inverse=True).to_gate()
    qft_dagger.label = "QFT_dagger"
    qc.append(qft_dagger, range(t))

    # Step 4: Measure the counting register
    qc.measure(range(t), range(t))

    return qc

def analyze_results(hist, t, n):
    """
    Post-processing the measurement to estimate the number of solutions M.
    Uses: M = N * sin^2(theta/2) where theta = 2*pi*phi
    """
    measured_str = max(hist, key=hist.get)
    measured_int = int(measured_str, 2)
    print(f"Register Output (binary) = {measured_str}")
    print(f"Register Output (decimal) = {measured_int}")

    # Phase estimation
    phi = measured_int / (2**t)
    theta = 2 * math.pi * phi
    print(f"Estimated phase (theta) = {theta:.5f} radians")

    N = 2**n
    M = N * (math.sin(theta / 2) ** 2)
    print(f"Estimated number of solutions M = {M:.2f} out of N = {N}")

    # Theoretical error bound from QPE analysis
    m = t - 1
    err = (math.sqrt(2*M*N) + N/(2**(m+1))) * (2**-m)
    print(f"Error bound: < {err:.2f}")

def run_quantum_counting(t=4, n=4):
    qc = quantum_counting_circuit(t, n)
    qc.draw('mpl')

    sim = AerSimulator()
    transpiled_qc = transpile(qc, sim)
    result = sim.run(transpiled_qc).result()
    hist = result.get_counts()

    plot_histogram(hist)
    plt.show()

    analyze_results(hist, t, n)

# Example run
if __name__ == "__main__":
    run_quantum_counting(t=4, n=4)