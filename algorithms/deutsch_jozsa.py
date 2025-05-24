from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
import numpy as np
import random

from data.const import DEFAULT_SHOTS

def deutsch_jozsa(n: int, f_type: str = "balanced") -> QuantumCircuit:
    """
    Deutsch-Jozsa Algorithm.
    
    Args:
        n: Number of input qubits (not counting ancilla).
        f_type: 'constant' or 'balanced'
    
    Returns:
        QuantumCircuit
    """
    # Create circuit with n input qubits + 1 ancilla, and n classical bits
    qc = QuantumCircuit(n + 1, n)

    # Step 1: Prepare ancilla |1>
    qc.x(n)
    # qc.x(range(n))  # Prepare input qubits |0>
    qc.h(n)

    # Step 2: Hadamard on all qubits
    qc.h(range(n))

    # Step 3: Apply oracle (modularized)
    oracle_deutsch_jozsa(qc, n, f_type)

    # Step 4: Hadamard again on input qubits
    qc.h(range(n))

    # Step 5: Measure input qubits
    qc.measure(range(n), range(n))

    return qc

def oracle_deutsch_jozsa(qc: QuantumCircuit, n: int, f_type: str = "balanced") -> list[int]:
    """
    Applies the oracle U_f to the circuit qc.
    
    For constant: returns f(x) = 0 or 1
    For balanced: returns a vector a such that f(x) = a⋅x mod 2
    
    Args:
        qc: QuantumCircuit with n+1 qubits
        n: number of input qubits
        f_type: 'constant' or 'balanced'
    
    Returns:
        List representing the function (either constant value or vector a)
    """
    if f_type == "constant":
        bit = random.choice([0, 1])
        if bit == 1:
            qc.x(n)  # Flip ancilla for all x → f(x) = 1
        return [bit]

    elif f_type == "balanced":
        # Define a balanced function f(x) = a⋅x (mod 2)
        a = [random.choice([0, 1]) for _ in range(n)]
        while all(ai == 0 for ai in a):  # ensure non-zero
            a = [random.choice([0, 1]) for _ in range(n)]
        for i in range(n):
            if a[i] == 1:
                qc.cx(i, n)
        return a

    else:
        raise ValueError("f_type must be 'constant' or 'balanced'")

# Example usage
qc = deutsch_jozsa(n=3, f_type="constant")
qc.draw("mpl")

sim = AerSimulator()
tqc = transpile(qc, sim)
result = sim.run(tqc, shots=DEFAULT_SHOTS).result()
counts = result.get_counts()


plot_histogram(counts)
plt.show()
# Check result
if '000' in counts and counts['000'] == DEFAULT_SHOTS:
    print("Oracle is likely CONSTANT.")
else:
    print("Oracle is BALANCED.")


# # Check result incase of input 111
# if '111' in counts and counts['111'] == DEFAULT_SHOTS:
#     print("Oracle is likely CONSTANT.")
# else:
#     print("Oracle is BALANCED.")