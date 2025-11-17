"""Three-qubit repetition code implementation protecting against bit flips."""

from __future__ import annotations

from qiskit import QuantumCircuit

from .base import BaseCode


class RepetitionCode3(BaseCode):
    """Encode one logical qubit into three physical qubits via repetition."""

    def __init__(self) -> None:
        self.name = "3-qubit repetition code"
        self.n_physical = 3
        self.n_logical = 1

    def build_circuit(self, logical_state: str = "0") -> QuantumCircuit:
        """Construct the encoding circuit and measurements for the code."""

        circuit = QuantumCircuit(self.n_physical, self.n_physical)

        if logical_state == "1":
            circuit.x(0)  # Prepare |1> when requested.
        elif logical_state != "0":
            raise ValueError("Only logical states '0' and '1' are supported.")

        circuit.cx(0, 1)
        circuit.cx(0, 2)

        circuit.measure(0, 0)
        circuit.measure(1, 1)
        circuit.measure(2, 2)

        return circuit

    def logical_error_rate_from_counts(
        self, counts: dict[str, int], logical_state: str = "0"
    ) -> float:
        """Decode via majority vote and estimate the logical error rate.

        This simple decoder assumes the standard Qiskit bitstring ordering, but
        more care is needed when mixing registers or changing measurement order.
        """

        if logical_state not in {"0", "1"}:
            raise ValueError("Only logical states '0' and '1' are supported.")

        expected_logical = int(logical_state)
        total_shots = sum(counts.values())
        logical_errors = 0

        for bitstring, shots in counts.items():
            ones = bitstring.count("1")
            logical_out = 1 if ones >= 2 else 0
            if logical_out != expected_logical:
                logical_errors += shots

        if total_shots == 0:
            return 0.0

        return logical_errors / total_shots
