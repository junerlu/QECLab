"""Active 3-qubit repetition-code demo with explicit syndrome decoding."""

from __future__ import annotations

from typing import Dict

from qiskit import ClassicalRegister, QuantumCircuit, transpile
from qiskit_aer import AerSimulator


_SYNDROME_TO_DATA = {
    0b01: 0,  # only ancilla-0 fired -> flip qubit 0
    0b10: 2,  # only ancilla-1 fired -> flip qubit 2
    0b11: 1,  # both fired -> middle qubit
}


def build_repetition3_active_correction_circuit(
    logical_state: str = "0", error_qubit: int | None = 1
) -> QuantumCircuit:
    """Return a circuit that encodes, errors, extracts syndromes, and corrects."""

    if logical_state not in {"0", "1"}:
        raise ValueError("Only logical states '0' and '1' are supported.")
    if error_qubit not in {None, 0, 1, 2}:
        raise ValueError("error_qubit must be None or one of 0, 1, 2.")

    data_reg = ClassicalRegister(3, "data")
    syndrome_reg = ClassicalRegister(2, "syndrome")
    circuit = QuantumCircuit(5, name="repetition3_active")
    circuit.add_register(data_reg)
    circuit.add_register(syndrome_reg)

    if logical_state == "1":
        circuit.x(0)

    circuit.cx(0, 1)
    circuit.cx(0, 2)

    if error_qubit is not None:
        circuit.x(error_qubit)

    circuit.cx(0, 3)
    circuit.cx(1, 3)
    circuit.cx(1, 4)
    circuit.cx(2, 4)

    circuit.measure(3, syndrome_reg[0])
    circuit.measure(4, syndrome_reg[1])
    circuit.barrier()

    for syndrome_value, target_qubit in _SYNDROME_TO_DATA.items():
        with circuit.if_test((syndrome_reg, syndrome_value)):
            circuit.x(target_qubit)

    circuit.barrier()

    circuit.measure(0, data_reg[0])
    circuit.measure(1, data_reg[1])
    circuit.measure(2, data_reg[2])

    return circuit


def run_active_correction_demo(
    logical_state: str = "0", error_qubit: int | None = 1, shots: int = 1024
) -> Dict[str, int]:
    """Execute the active-correction circuit and aggregate counts over the data register."""

    circuit = build_repetition3_active_correction_circuit(
        logical_state=logical_state, error_qubit=error_qubit
    )
    simulator = AerSimulator()
    compiled = transpile(circuit, simulator)
    result = simulator.run(compiled, shots=shots).result()
    raw_counts = result.get_counts()

    data_counts: Dict[str, int] = {}
    for bitstring, count in raw_counts.items():
        data_bits = bitstring[-3:]
        data_counts[data_bits] = data_counts.get(data_bits, 0) + count

    ideal = "000" if logical_state == "0" else "111"
    success = data_counts.get(ideal, 0) / shots
    print(
        f"[Active demo] logical={logical_state}, error_qubit={error_qubit}, "
        f"success={success:.3f}"
    )
    print("Data-register counts:", data_counts)

    return data_counts
