from matplotlib import pyplot as plt
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag

# Define a sample circuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.t(0)
qc.cx(0, 1)
qc.tdg(1)
qc.t(0)
qc.cx(0, 1)
qc.measure(0, 0)
qc.measure(1, 1)

# Convert to DAG
dag = circuit_to_dag(qc)

# Compute general metrics
depth = qc.depth()
size = qc.size()
width = qc.width()

# Compute T-count and T-depth
t_count = 0
t_layers = {}

for node in dag.topological_op_nodes():
    if node.name in ['t', 'tdg']:
        t_count += 1
        qubit = node.qargs[0]._index
        prev_layer = t_layers.get(qubit, 0)
        t_layers[qubit] = prev_layer + 1

t_depth = max(t_layers.values()) if t_layers else 0

qc.draw()
# Print the results
print("Circuit depth   :", depth)
print("Circuit size    :", size)
print("Circuit width   :", width)
print("T-count         :", t_count)
print("T-depth         :", t_depth)
plt.show()
