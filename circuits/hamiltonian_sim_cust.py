import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
import matplotlib.pyplot as plt


def exp_all_z(circuit, quantum_register, pauli_idexes, control_qubit=None, t=1):
    """
    Implements exp(i Z...Z t) using a CNOT ladder and RZ/CRZ.
    """
    if len(pauli_idexes) == 0:
        if control_qubit is not None:
            circuit.p(t, control_qubit)
        return

    # Forward CNOT ladder
    for i in range(len(pauli_idexes) - 1):
        circuit.cx(quantum_register[pauli_idexes[i]], quantum_register[pauli_idexes[i + 1]])

    # RZ or CRZ gate on last qubit
    target = quantum_register[pauli_idexes[-1]]
    if control_qubit is None:
        circuit.rz(-2 * t, target)
    else:
        circuit.crz(-2 * t, control_qubit, target)

    # Reverse CNOT ladder
    for i in reversed(range(len(pauli_idexes) - 1)):
        circuit.cx(quantum_register[pauli_idexes[i]], quantum_register[pauli_idexes[i + 1]])


def exp_pauli(pauli, quantum_register, control_qubit=None, control_register=None, t=1):
    """
    Builds exp(i P t), where P is a Pauli string, using basis change + exp_all_z.
    """
    if len(pauli) != len(quantum_register):
        raise ValueError("Pauli string length must match quantum register length.")

    # Build circuit with both registers if control is active
    if control_qubit is not None:
        if control_register is None:
            raise ValueError("control_register must be provided if control_qubit is used.")
        pauli_circuit = QuantumCircuit(control_register, quantum_register)
        prep = QuantumCircuit(control_register, quantum_register)
    else:
        pauli_circuit = QuantumCircuit(quantum_register)
        prep = QuantumCircuit(quantum_register)

    pauli_idexes = []

    for i, p in enumerate(pauli):
        if p == 'I':
            continue
        elif p == 'Z':
            pauli_idexes.append(i)
        elif p == 'X':
            prep.h(quantum_register[i])
            pauli_idexes.append(i)
        elif p == 'Y':
            prep.sdg(quantum_register[i])
            prep.h(quantum_register[i])
            pauli_idexes.append(i)
        else:
            raise ValueError(f"Invalid Pauli operator '{p}' at index {i}.")

    # Apply: prep → ZZ...Z → unprep
    pauli_circuit = pauli_circuit.compose(prep)
    exp_all_z(pauli_circuit, quantum_register, pauli_idexes, control_qubit, t)
    pauli_circuit = pauli_circuit.compose(prep.inverse())

    return pauli_circuit


def hamiltonian_simulation(hamiltonian, quantum_register=None,
                           control_qubit=None, control_register=None,
                           t=1, trotter_number=1):
    """
    Implements first-order Trotterized exp(i H t) for given Pauli-string Hamiltonian.
    """
    if quantum_register is None:
        n = len(next(iter(hamiltonian)))
        quantum_register = QuantumRegister(n, 'q')

    if control_qubit is not None and control_qubit in quantum_register:
        raise ValueError("Control qubit must not be part of quantum register.")

    if control_qubit is not None:
        if control_register is None:
            raise ValueError("control_register must be provided with control_qubit.")
        circuit = QuantumCircuit(control_register, quantum_register)
    else:
        circuit = QuantumCircuit(quantum_register)

    delta_t = t / trotter_number

    for _ in range(trotter_number):
        for pauli_string, weight in hamiltonian.items():
            term = exp_pauli(
                pauli_string,
                quantum_register,
                control_qubit=control_qubit,
                control_register=control_register,
                t=weight * delta_t
            )
            circuit = circuit.compose(term)

    return circuit

from qiskit.visualization import circuit_drawer

qr = QuantumRegister(3, 'q')
hamiltonian = {
    "XZX": 2,
    "ZYI": 5,
    "IYZ": 7
}

circuit = hamiltonian_simulation(hamiltonian, qr, t=1/(2 * np.pi), trotter_number=1)
circuit.draw("mpl")

qr = QuantumRegister(3, 'q')
cr = QuantumRegister(1, 'c')

control_circuit = hamiltonian_simulation(
    hamiltonian,
    quantum_register=qr,
    control_qubit=cr[0],
    control_register=cr,
    t=1/(2 * np.pi),
    trotter_number=1
)

# Combine full circuit for visualization
full_circuit = QuantumCircuit(cr, qr)
full_circuit = full_circuit.compose(control_circuit)
full_circuit.draw("mpl")

# plt.show()
