from qiskit import QuantumCircuit, transpile, ClassicalRegister, QuantumRegister
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
from circuits.bell_state import bell_pair_beta
from qiskit.result.utils import marginal_counts

def teleportation_circuit(alpha=1, beta=0):
    # Step 0: Create quantum circuit with 3 qubits and 2 classical bits
    qr = QuantumRegister(3, name='quantum')
    cr = ClassicalRegister(2, name='classical')
    qc = QuantumCircuit(qr, cr, name='Teleportation')

    # Step 1: Prepare state to teleport on qubit 0
    qc.initialize([alpha, beta], 0)
    qc.barrier()

    # Step 2: Create Bell pair (qubits 1 and 2)
    bell_pair = bell_pair_beta(a=0, b=0, q0=1, q1=2)
    qc.compose(bell_pair, inplace=True)
    qc.barrier()

    # Step 3: Alice's Bell measurement (on qubits 0 and 1)
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier()

    # Step 4: Measure Alice's qubits and store in classical bits
    qc.measure(0, cr[0])
    qc.measure(1, cr[1])

    # Step 5: Bob's conditional correction on qubit 2
    with qc.if_test((cr[0],1)):
        qc.x(2)
    with qc.if_test((cr[1],1)):
        qc.z(2)

    return qc

# Choose a state to teleport
alpha = 1 / 2**0.5
beta = 1 / 2**0.5

qc = teleportation_circuit(alpha, beta)
# Need to add a new ClassicalRegister
# to see the result
cr_result = ClassicalRegister(1)
qc.add_register(cr_result)
qc.measure(2,2)
qc.draw('mpl')  # Optional: visualize

# # Simulate final state before measurement
# sv = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
# print("Statevector before measurement:")
# print(sv)

# Run simulation
sim = AerSimulator()
tqc = transpile(qc, sim)
tqc.save_statevector()
result = sim.run(tqc, shots=1024).result()
counts = result.get_counts()
print(counts)
# for each qubit, get the marginal counts(distribution)
qubit_counts = [marginal_counts(counts, [qubit]) for qubit in range(3)]
print(qubit_counts)
# plot_histogram(qubit_counts)
# plot_histogram(counts)
# plt.show()
