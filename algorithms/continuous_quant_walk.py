import numpy as np
from qiskit.quantum_info import Operator
from qiskit import QuantumCircuit
import scipy

# 3-node cycle graph
A = np.array([[0, 1, 1],
              [1, 0, 1],
              [1, 1, 0]])
gamma = 1.0
t = 1.0
H = gamma * A
U = scipy.linalg.expm(-1j * H * t)  # Unitary evolution

qc = QuantumCircuit(3)
qc.unitary(Operator(U), [0, 1, 2], label="CTQW")
qc.draw()