# from qiskit.quantum_info import Statevector
import numpy as np
import matplotlib.pyplot as plt
from qiskit import transpile, QuantumCircuit
from qiskit_aer import Aer

from circuits.bell_state import bell_pair_beta
from data.const import DEFAULT_SHOTS


# Measurement basis rotation for Alice
# x=0 -> Z basis (no change), x=1 -> X basis (apply H)
def apply_alice_basis(qc :QuantumCircuit, x: int):
    if x == 1:
        qc.h(0)
    else:
        qc.id(0)

# Measurement basis rotation for Bob
# y=0 -> rotated by +pi/8, y=1 -> rotated by -pi/8
def apply_bob_basis(qc: QuantumCircuit, y: int):
    angle = np.pi / 8 if y == 0 else -np.pi / 8
    # To measure in the rotated basis, we rotate the qubit in the opposite direction before measuring in Z.
    qc.ry(-2 * angle, 1)

# Run one CHSH game round with given x and y
def run_chsh_round(x, y):
    backend = Aer.get_backend("aer_simulator")

    qc = bell_pair_beta(a=0,b=0, q0=0, q1=1)
    apply_alice_basis(qc, x)
    apply_bob_basis(qc, y)
    qc.measure_all()
    qc = transpile(qc, backend)

    # Run with shots
    result = backend.run(qc, shots=DEFAULT_SHOTS).result()
    return result.get_counts()

# Evaluate winning probability for each input pair
input_pairs = [(0,0), (0,1), (1,0), (1,1)]
win_counts = 0

print("Running CHSH rounds for each (x,y) input pair...")
for x, y in input_pairs:
    counts = run_chsh_round(x, y)
    total = sum(counts.values())
    wins = 0
    for bitstring, count in counts.items():
        a = int(bitstring[-1])  # qubit 0
        b = int(bitstring[-2])  # qubit 1
        if (a ^ b) == (x & y):
            wins += count
    win_rate = wins / total
    print(f"x={x}, y={y} -> Win rate: {win_rate:.3f}")
    win_counts += wins

total_shots = DEFAULT_SHOTS * 4
print(f"\nOverall quantum win rate: {win_counts / total_shots:.3f}")