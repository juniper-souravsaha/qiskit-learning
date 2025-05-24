import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def alice_prepares_qubits(key_bits, bases):
    """Prepare quantum state according to BB84 protocol for Alice."""
    n = len(key_bits)
    qc = QuantumCircuit(n, n)
    for i in range(n):
        if key_bits[i] == 1:
            qc.x(i)
        if bases[i] == 1:
            qc.h(i)
    return qc


def eve_intercepts(qc, eve_bases):
    """Eve intercepts and measures qubits in her random bases."""
    n = len(eve_bases)
    for i in range(n):
        if eve_bases[i] == 1:
            qc.h(i)
        qc.measure(i, i)
        # Eve re-prepares the qubit after measurement (ideal case)
        qc.reset(i)
        if random.randint(0, 1):
            qc.x(i)
        if eve_bases[i] == 1:
            qc.h(i)
    return qc


def bob_measures_qubits(qc, bob_bases):
    """Bob measures qubits in his chosen bases."""
    n = len(bob_bases)
    for i in range(n):
        if bob_bases[i] == 1:
            qc.h(i)
        qc.measure(i, i)
    return qc


def sift_keys(alice_bases, bob_bases, alice_key, bob_key):
    """Compare Alice's and Bob's bases to derive the sifted key."""
    sifted_alice = []
    sifted_bob = []
    for a_b, b_b, a_k, b_k in zip(alice_bases, bob_bases, alice_key, bob_key):
        if a_b == b_b:
            sifted_alice.append(a_k)
            sifted_bob.append(b_k)
    return sifted_alice, sifted_bob


def error_estimation(sifted_alice_key, sifted_bob_key, sample_size=10):
    """Estimate QBER from a sample of the sifted key."""
    if len(sifted_alice_key) < sample_size:
        sample_size = len(sifted_alice_key)
    indices = random.sample(range(sample_size), sample_size)
    errors = sum(sifted_alice_key[i] != sifted_bob_key[i] for i in indices)
    return errors / sample_size if sample_size > 0 else 0


def run_bb84_protocol_with_eve(key_size=100, eve_present=True, threshold=0.2):
    alice_key = [random.randint(0, 1) for _ in range(key_size)]
    alice_bases = [random.randint(0, 1) for _ in range(key_size)]
    bob_bases = [random.randint(0, 1) for _ in range(key_size)]

    qc = alice_prepares_qubits(alice_key, alice_bases)
    print("Alice's key:", alice_key)
    print("Alice's bases:", alice_bases)
    print("Bob's bases:", bob_bases)
    print("Eve's presence:", eve_present)
    if eve_present:
        eve_bases = [random.randint(0, 1) for _ in range(key_size)]
        qc = eve_intercepts(qc, eve_bases)

    qc = bob_measures_qubits(qc, bob_bases)
    print("Bob's measure done.")
    simulator = AerSimulator()
    transpiled = transpile(qc, simulator)
    result = simulator.run(transpiled, shots=10).result()
    counts = result.get_counts()
    print("Counts:", counts)
    # Get the most frequent outcome (realistically only 1 shot used)
    outcome = max(counts, key=counts.get)
    bob_key = list(map(int, reversed(outcome.zfill(key_size))))

    # Sift the keys
    sifted_alice, sifted_bob = sift_keys(alice_bases, bob_bases, alice_key, bob_key)
    error_rate = error_estimation(sifted_alice, sifted_bob)
    print("Sifted keys:")
    print("Alice's sifted key:", sifted_alice)
    print("Bob's sifted key:", sifted_bob)
    print(f"Error rate: {error_rate:.2%}")
    if error_rate > threshold:
        print("Possible eavesdropping detected. Aborting key exchange.")
        return None

    print("Key exchange successful.")
    print(f"Alice's sifted key: {sifted_alice}")
    print(f"Bob's sifted key:   {sifted_bob}")
    return sifted_alice, sifted_bob


# Run the BB84 protocol
if __name__ == "__main__":
    final_key = run_bb84_protocol_with_eve(key_size=20, eve_present=True)