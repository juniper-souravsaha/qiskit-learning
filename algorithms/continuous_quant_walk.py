import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm

# Adjacency matrix of a 4-node line graph
A = np.array([
    [0, 1, 0, 0],
    [1, 0, 1, 0],
    [0, 1, 0, 1],
    [0, 0, 1, 0]
])

# Initial state: walker at node 1 (|1⟩)
psi0 = np.zeros(4, dtype=complex)
psi0[1] = 1.0

def evolve_ctqw(H, psi0, times):
    return [expm(-1j * H * t) @ psi0 for t in times]

times = np.linspace(0, 10, 200)
states = evolve_ctqw(A, psi0, times)

# Extract probabilities at each time step
probs = np.abs(np.array(states))**2

# Plot the probability evolution
plt.figure(figsize=(10, 6))
for i in range(4):
    plt.plot(times, probs[:, i], label=f'Node {i}')
plt.title('CTQW on 4-node Line Graph')
plt.xlabel('Time')
plt.ylabel('Probability')
plt.legend()
plt.grid(True)
plt.show()