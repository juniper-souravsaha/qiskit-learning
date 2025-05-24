import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_vector

def bloch_vector_after_rotation(gate: str, theta: float):
    qc = QuantumCircuit(1)

    if gate == 'rx':
        qc.rx(theta, 0)
    elif gate == 'ry':
        qc.ry(theta, 0)
    elif gate == 'rz':
        qc.rz(theta, 0)
    else:
        raise ValueError("Gate must be 'rx', 'ry', or 'rz'")

    state = Statevector.from_instruction(qc)
    a, b = state.data  # state = a|0⟩ + b|1⟩

    # Compute Bloch vector: (x, y, z)
    x = 2 * np.real(np.conj(a) * b)
    y = 2 * np.imag(np.conj(b) * a)
    z = np.abs(a)**2 - np.abs(b)**2

    return np.array([x, y, z])

# Plotting
angles = [0, np.pi/4, np.pi/2, np.pi, 3*np.pi/2]
angle_labels = ["0", "π/4", "π/2", "π", "3π/2"]
gates = ['rx', 'ry', 'rz']

fig, axes = plt.subplots(len(gates), len(angles), figsize=(15, 9), subplot_kw={'projection': '3d'})

for i, gate in enumerate(gates):
    for j, theta in enumerate(angles):
        bloch_vec = bloch_vector_after_rotation(gate, theta)
        ax = axes[i][j]
        plot_bloch_vector(bloch_vec, ax=ax)
        # symbolic_theta = latex(N(theta / pi)) + r"\pi"
        # ax.set_title(f"{gate.upper()}({symbolic_theta})")
        ax.set_title(f'{gate.upper()}({angle_labels[j]})')

plt.tight_layout()
plt.show()