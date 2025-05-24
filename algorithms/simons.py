import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt

from data.const import DEFAULT_SHOTS

# Oracle for f(x) = f(x ⊕ s) with s = 101
def simon_oracle(n=3, s='101'):
    s = s[::-1] # reverse b for easy iteration
    qc_o = QuantumCircuit(2 * n)

    # Copy input x to output
    for i in range(n):
        qc_o.cx(i, n + i)

    if '1' not in s:
        return qc_o  # 1:1 mapping, so just exit
    i = s.find('1') # index of first non-zero bit in b
    # Do |x> -> |s.x> on condition that q_i is 1
    for j in range(n):
        if s[j] == '1':
            qc_o.cx(i, (j)+n)
    
    return qc_o

# Simon's Algorithm Circuit
def simons_algorithm(n=3, s='101'):
    qc = QuantumCircuit(2 * n, n)

    # Step 1: Hadamard on input register
    for i in range(n):
        qc.h(i)

    # Step 2: Apply oracle
    oracle = simon_oracle(n, s)
    qc.compose(oracle, inplace=True)

    # Step 3: Hadamard again on input register
    for i in range(n):
        qc.h(i)

    # Step 4: Measurement of input register
    for i in range(n):
        qc.measure(i, i)

    return qc

# Classical post-processing to solve for hidden string s
def solve_linear_mod2(equations: list[str]) -> str:
    n = len(equations[0])
    m = len(equations)
    A = np.array([[int(bit) for bit in eq] for eq in equations], dtype=np.uint8)

    row = 0
    for col in range(n):
        pivot = None
        for r in range(row, m):
            if A[r][col] == 1:
                pivot = r
                break
        if pivot is None:
            continue
        A[[row, pivot]] = A[[pivot, row]]
        for r in range(m):
            if r != row and A[r][col] == 1:
                A[r] ^= A[row]
        row += 1

    # Try non-zero solution for s
    for guess in range(1, 2**n):
        s = np.array([(guess >> i) & 1 for i in reversed(range(n))], dtype=np.uint8)
        if np.all((A @ s) % 2 == 0):
            return ''.join(str(b) for b in s)

    return "No solution found"

# Build and run
n = 3
s = '110'
qc = simons_algorithm(n, s)
# qc.draw('mpl')  # Optional: visualize

# Run the circuit
sim = AerSimulator()
tqc = transpile(qc, sim)
result = sim.run(tqc, shots=DEFAULT_SHOTS).result()
counts = result.get_counts()

# # Display result
# plot_histogram(counts)
# plt.show()

# counts = result.quasi_dists[0]

print("Measurement Results:")
for bitstring, prob in counts.items():
    print(f"{bitstring}: {prob:.3f}")

equations = [k for k in counts.keys() if k != '0' * len(s)]
print(f"\nEquations from measurements: {equations}")
s_found = solve_linear_mod2(equations)
print(f"\nRecovered hidden string s: {s_found}")