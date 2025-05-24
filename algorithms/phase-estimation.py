import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

def construct_qpe(theta, num_estimation_qubits):
    """
    Construct Quantum Phase Estimation circuit.
    - theta: phase such that U|ψ> = e^{2πiθ}|ψ>
    - num_estimation_qubits: number of qubits for estimating θ (more bits → more precision)
    """

    # Total qubits: estimation register + 1 eigenstate qubit
    qc = QuantumCircuit(num_estimation_qubits + 1, num_estimation_qubits)

    # Step 1: Apply Hadamard to all estimation qubits
    # Creates uniform superposition: (1/√2^t) Σ_k |k⟩
    qc.h(range(num_estimation_qubits))

    # Step 2: Prepare the eigenstate |ψ⟩
    # We use |1⟩, which is an eigenstate of RZ gate (used below)
    qc.x(num_estimation_qubits)

    # Step 3: Apply controlled unitary powers: CU^{2^k}
    # Each estimation qubit controls U^{2^k} applied to the eigenstate
    # U = RZ(2πθ), so U^{2^k} = RZ(2πθ * 2^k)
    for k in range(num_estimation_qubits):
        repetitions = 2**k
        for _ in range(repetitions):
            # cp(2πθ) ≡ controlled-RZ(2πθ)
            qc.cp(2 * np.pi * theta, k, num_estimation_qubits)

    # Step 4: Apply inverse Quantum Fourier Transform
    # Converts phase-encoded amplitudes to computational basis states
    qc.compose(inverse_qft(num_estimation_qubits), inplace=True)

    # Step 5: Measure estimation register
    qc.measure(range(num_estimation_qubits), range(num_estimation_qubits))

    return qc

def inverse_qft(n):
    """
    Inverse Quantum Fourier Transform.
    Uncomputes the QFT: turns phase into binary.
    """
    qc = QuantumCircuit(n)
    for j in reversed(range(n)):
        for m in range(j):
            # Apply inverse controlled phase rotations
            qc.cp(-np.pi / 2**(j - m), m, j)
        qc.h(j)
    return qc

# --- MAIN ---
# say, φ = 0.375 = 3/8 => result ~= ∣3⟩=∣011⟩
# say, φ = 0.125 = 1/8 => result ~= ∣1⟩=∣001⟩
# say, φ = 0.625 = 5/8 => result ~= ∣5⟩=∣101⟩
theta = 0.125  # We want to estimate this θ (1/8)
n = 3          # Use 3 qubits to estimate (gives precision of 1/8)

qpe_circuit = construct_qpe(theta, n)
qpe_circuit.draw('mpl', filename='gen-images/qpe_circuit.png')
# Run the circuit using statevector simulator
sim = AerSimulator()
compiled = transpile(qpe_circuit, sim)
result = sim.run(compiled, shots=1024).result()
counts = result.get_counts()

# Plot and show histogram
plot_histogram(counts)
plt.title("QPE Result for θ = 0.125")
plt.show()

# Convert most frequent binary output to decimal
max_key = max(counts, key=counts.get)
phase_decimal = int(max_key, 2) / (2**n)
print(f"Estimated phase: {phase_decimal:.3f} (binary: {max_key})")