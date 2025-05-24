from qiskit import QuantumCircuit

def bell_pair_beta(a=0, b=0, q0=0, q1=1):
    """
    Create a Bell state |β(a, b)> = (|0⟩|b⟩ + (-1)^a |1⟩|¬b⟩) / √2

    Parameters:
    - a: int (0 or 1) – determines phase
    - b: int (0 or 1) – determines target bit flip
    - q0: int – control qubit
    - q1: int – target qubit

    Returns:
    - QuantumCircuit producing the desired Bell state
    """
    qc = QuantumCircuit(max(q0, q1) + 1)

    qc.h(q0)        # Hadamard on control
    qc.cx(q0, q1)   # Entangle

    if b == 1:
        qc.x(q1)    # Flip target bit

    if a == 1:
        qc.z(q0)    # Phase flip

    return qc


# bell_pair_beta(a=0, b=0, q0=1, q1=2).draw("mpl")  # |β(0,0)> = (|00⟩ + |11⟩)/√2
# bell_pair_beta(1, 0).draw("mpl")  # |β(1,0)> = (|00⟩ - |11⟩)/√2
# bell_pair_beta(0, 1).draw("mpl")  # |β(0,1)> = (|01⟩ + |10⟩)/√2
# bell_pair_beta(1, 1).draw("mpl")  # |β(1,1)> = (|01⟩ - |10⟩)/√2

def bell_pair(q0=0, q1=1, state_type="phi_plus"):
    """
    Create a Bell pair circuit between two qubits.

    Parameters:
    - q0: int - first qubit index (control)
    - q1: int - second qubit index (target)
    - state_type: str - type of Bell state ("phi_plus", "phi_minus", "psi_plus", "psi_minus")

    Returns:
    - QuantumCircuit with 2 qubits in the desired Bell state
    """
    qc = QuantumCircuit(max(q0, q1) + 1)
    
    qc.h(q0)        # Step 1: Hadamard on q0
    qc.cx(q0, q1)   # Step 2: CNOT from q0 to q1

    if state_type == "phi_minus":
        qc.z(q0)    # Apply Z to flip phase of |11⟩
    elif state_type == "psi_plus":
        qc.x(q1)    # Apply X to get |01⟩ + |10⟩
    elif state_type == "psi_minus":
        qc.x(q1)
        qc.z(q0)    # Combine X and Z for phase flip

    return qc

# bell_pair(q0=1, q1=2, state_type="psi_minus").draw() 

