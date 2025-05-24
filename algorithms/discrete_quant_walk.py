from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# Parameters
num_positions = 8  # positions = 3 qubits
num_steps = 5

# Registers
pos = QuantumRegister(3, 'pos')  # 3 qubits for 8 positions
coin = QuantumRegister(1, 'coin')  # 1 qubit coin
c = ClassicalRegister(3, 'c')  # measurement for position
qc = QuantumCircuit(pos, coin, c)

# Initialize to middle position (e.g., pos 4) and coin state |0⟩
qc.x(pos[2])  # |100⟩ = pos 4

# Define shift operator
def shift_op(qc):
    for i in range(8):
        bin_str = f"{i:03b}"
        for j in range(3):
            if bin_str[j] == '1':
                qc.x(pos[2-j])
        # Controlled increment/decrement based on coin state
        qc.mcx([coin[0]] + list(pos), pos[0])  # Fake shift logic
        for j in range(3):
            if bin_str[j] == '1':
                qc.x(pos[2-j])

# Walk
for _ in range(num_steps):
    qc.h(coin)       # Coin flip
    shift_op(qc)     # Shift depending on coin state
    qc.barrier()

# Measure position
qc.measure(pos, c)

# Simulate
sim = AerSimulator()
tqc = transpile(qc, sim)
result = sim.run(tqc, shots=1024).result()
counts = result.get_counts()
plot_histogram(counts)
plt.title(f"Quantum Walk: {num_steps} steps on line with 8 positions")
plt.show()