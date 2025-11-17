"""Nine-qubit Shor code combining phase- and bit-flip repetition protections."""

from __future__ import annotations

from qiskit import QuantumCircuit

from .base import BaseCode


class ShorCode9(BaseCode):
    """Encode one logical qubit into the 9-qubit Shor code."""

    def __init__(self) -> None:
        self.name = "9-qubit Shor code"
        self.n_physical = 9
        self.n_logical = 1

    def build_circuit(self, logical_state: str = "0") -> QuantumCircuit:
        """Build the encode/decode circuit for the Shor code."""

        circuit = QuantumCircuit(self.n_physical, self.n_physical)

        if logical_state == "1":
            circuit.x(0)
        elif logical_state != "0":
            raise ValueError("Only logical states '0' and '1' are supported.")

        circuit.cx(0, 3)
        circuit.cx(0, 6)

        for qubit in (0, 3, 6):
            circuit.h(qubit)

        for start in (0, 3, 6):
            circuit.cx(start, start + 1)
            circuit.cx(start, start + 2)

        for qubit in (0, 3, 6):
            circuit.h(qubit)

        for qubit in range(self.n_physical):
            circuit.measure(qubit, qubit)

        return circuit

    def logical_error_rate_from_counts(
        self, counts: dict[str, int], logical_state: str = "0"
    ) -> float:
        """Decode by majority vote within each triple and across triples."""

        if logical_state not in {"0", "1"}:
            raise ValueError("Only logical states '0' and '1' are supported.")

        expected_logical = int(logical_state)
        total_shots = sum(counts.values())
        logical_errors = 0

        for bitstring, shots in counts.items():
            bits = bitstring[::-1]
            block_values = []
            for start in (0, 3, 6):
                block = bits[start : start + 3]
                ones = block.count("1")
                block_values.append(1 if ones >= 2 else 0)
            logical_out = 1 if block_values.count(1) >= 2 else 0
            if logical_out != expected_logical:
                logical_errors += shots

        if total_shots == 0:
            return 0.0

        return logical_errors / total_shots
