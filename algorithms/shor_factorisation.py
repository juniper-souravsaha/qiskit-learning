import numpy as np
from math import gcd
from fractions import Fraction
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from qiskit_aer import AerSimulator

def is_coprime(a, N):
    return gcd(a, N) == 1


def modular_inverse(a, N):
    for i in range(1, N):
        if (a * i) % N == 1:
            return i
    return None


def get_random_coprime(N):
    for a in range(2, N):
        if gcd(a, N) == 1:
            return a
    raise ValueError("No coprime found")


def c_amod15(a, power):
    """Controlled multiplication by a mod 15"""
    if a not in [2,4,7,8,11,13]:
        raise ValueError("'a' must be 2,4,7,8,11 or 13")
    U = QuantumCircuit(4)
    for _iteration in range(power):
        if a in [2,13]:
            U.swap(2,3)
            U.swap(1,2)
            U.swap(0,1)
        if a in [7,8]:
            U.swap(0,1)
            U.swap(1,2)
            U.swap(2,3)
        if a in [4, 11]:
            U.swap(1,3)
            U.swap(0,2)
        if a in [7,11,13]:
            for q in range(4):
                U.x(q)
    U = U.to_gate()
    U.name = f"{a}^{power} mod 15"
    c_U = U.control()
    return c_U


def qpe_period_finding_circuit(a, N, n_count=8):
    qc = QuantumCircuit(n_count + 4, n_count)
    qc.h(range(n_count))
    qc.x(n_count)
    for q in range(n_count):
        qc.append(c_amod15(a, 2**q),
             [q] + [i+n_count for i in range(4)])
    qc.append(QFT(n_count, inverse=True).to_gate(label="IQFT"), range(n_count))
    qc.measure(range(n_count), range(n_count))
    return qc


def get_period_from_result(counts, N, n_count=8):
    measured_bin = max(counts, key=counts.get)
    measured_decimal = int(measured_bin, 2)
    phase = measured_decimal / (2 ** n_count)
    frac = Fraction(phase).limit_denominator(N)
    r = frac.denominator
    return r, phase, frac


def try_shor(N, a=None, n_count=8, plot=True):
    if not a:
        a = get_random_coprime(N)
    print(f"\nTrying to factor N = {N} using a = {a}")
    assert gcd(a, N) == 1, "a must be coprime to N"

    qc = qpe_period_finding_circuit(a, N, n_count)
    # qc.draw(fold=-1)  # -1 means 'do not fold'
    backend = AerSimulator()
    tqc = transpile(qc, backend)
    # qobj = assemble(tqc, shots=1)
    result = backend.run(tqc).result()
    counts = result.get_counts()

    if plot:
        plot_histogram(counts)
        plt.title(f"Measured Phase (N={N}, a={a})")
        plt.show()

    r, phase, frac = get_period_from_result(counts, N, n_count)
    print(f"Measured phase: {phase:.5f}, approximated as {frac}")
    print(f"Estimated period r = {r}")

    if r % 2 == 0 and pow(a, r // 2, N) != N - 1:
        guess1 = gcd(pow(a, r // 2) - 1, N)
        guess2 = gcd(pow(a, r // 2) + 1, N)
        if guess1 not in [1, N] and guess2 not in [1, N]:
            print(f"Found factors: {guess1}, {guess2}")
            return guess1, guess2
        else:
            print("Non-trivial factors not found. Try another a.")
    else:
        print("Invalid period. Try again with different a.")
    return None, None


# Examples, this works only for N=15, a=2,4,7,8,11,13. c_amod15 is not
# implemented for other values of a.
try_shor(15, a=4, plot=False)
try_shor(15, a=8, plot=False)
try_shor(15, a=2, plot=False)
