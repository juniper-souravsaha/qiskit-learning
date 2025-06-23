from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Operator
from fractions import Fraction
import matplotlib.pyplot as plt
import numpy as np


def modexp_operator(a, power, N, n_qubits):
    """Returns a unitary Operator that computes modular multiplication by a^{2^power} mod N"""
    dim = 2 ** n_qubits
    U = np.zeros((dim, dim))

    # Only define the mapping for values < N (others act like identity)
    for x in range(dim):
        if x < N:
            y = (pow(a, 2**power, N) * x) % N
        else:
            y = x  # leave high-index basis states unchanged
        U[y, x] = 1

    return Operator(U)

def controlled_modexp_gate(a, N, power, n_qubits):
    """Returns a controlled modular exponentiation gate"""
    op = modexp_operator(a, power, N, n_qubits)
    gate = op.to_instruction()
    return gate.control()

def inverse_qft(n):
    qc = QuantumCircuit(n)
    for j in range(n//2):
        qc.swap(j, n - j - 1)
    for j in range(n):
        for k in range(j):
            qc.cp(-np.pi/2**(j - k), k, j)
        qc.h(j)
    return qc

def qpe_order_finding(a, N, n_count, n_target):
    qc = QuantumCircuit(n_count + n_target, n_count)

    # Put counting qubits in superposition
    for i in range(n_count):
        qc.h(i)

    # Initialize target to |1⟩
    qc.x(n_count + n_target - 1)

    # Apply controlled modular exponentiation gates
    for j in range(n_count):
        gate = controlled_modexp_gate(a, N, j, n_target)
        control = j
        target = list(range(n_count, n_count + n_target))
        qc.append(gate, [control] + target)

    # Apply inverse QFT
    iqft = inverse_qft(n_count)
    qc.compose(iqft, range(n_count), inplace=True)

    # Measure
    qc.measure(range(n_count), range(n_count))
    return qc

# # Parameters
# a = 7
# N = 15
# n_count = 4  # bits of precision
# n_target = 4  # bits to represent numbers mod N (since 15 < 2^4)

# # Build and simulate circuit
# qc = qpe_order_finding(a=7, N=15, n_count=4, n_target=4)
# sim = AerSimulator()
# compiled = transpile(qc, sim)
# result = sim.run(compiled, shots=1024).result()
# counts = result.get_counts()

# # Plot and analyze
# plot_histogram(counts)
# plt.title("Order Finding via QPE (a=7, N=15)")
# plt.show()

# # Extract result
# measured = max(counts, key=counts.get)
# phase = int(measured, 2) / 2**4
# frac = Fraction(phase).limit_denominator(N)
# r_est = frac.denominator

# print(f"Most likely binary: {measured}")
# print(f"Estimated phase = {phase}")
# print(f"Approximated by fraction: {frac}")
# print(f"Estimated order r = {r_est}")

def find_order(a, N, n_count=None, n_target=None, shots=1024, plot=False):
    from math import gcd
    from qiskit import transpile
    from fractions import Fraction

    if gcd(a, N) != 1:
        print(f"Skipping a = {a} (not coprime with N = {N})")
        return None

    if n_target is None:
        n_target = N.bit_length()
    if n_count is None:
        n_count = 2 * n_target  # safe precision

    qc = qpe_order_finding(a, N, n_count, n_target)

    compiled = transpile(qc, sim)
    result = sim.run(compiled, shots=shots).result()
    counts = result.get_counts()
    measured = max(counts, key=counts.get)

    phase = int(measured, 2) / 2**n_count
    frac = Fraction(phase).limit_denominator(N)
    r = frac.denominator

    if plot:
        plot_histogram(counts)
        plt.title(f"a = {a}, Estimated r = {r}")
        plt.show()

    print(f"a = {a} → estimated phase = {phase:.4f}, approx = {frac}, r = {r}")
    return r

N = 15
sim = AerSimulator()
for a in range(2, N):
    find_order(a, N, plot=False)