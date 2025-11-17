"""Toy rotated surface code of distance 3 with parity-check readout."""

from __future__ import annotations

from qiskit import QuantumCircuit

from .base import BaseCode


class RotatedSurfaceCodeD3(BaseCode):
    """Demonstrate a distance-3 rotated surface code using passive decoding."""

    def __init__(self) -> None:
        self.name = "d=3 rotated surface code"
        self.n_physical = 17  # 9 data qubits + 8 ancilla qubits
        self.n_logical = 1

    def build_circuit(self, logical_state: str = "0") -> QuantumCircuit:
        """Construct a small rotated-surface-style circuit with parity checks."""

        if logical_state not in {"0", "1"}:
            raise ValueError("Only logical states '0' and '1' are supported.")

        circuit = QuantumCircuit(self.n_physical, self.n_physical)

        data = list(range(9))
        anc_x = list(range(9, 13))
        anc_z = list(range(13, 17))

        if logical_state == "1":
            circuit.x(data[0])

        for target in data[1:]:
            circuit.cx(data[0], target)

        x_stabilizers = [
            (0, 1, 3, 4),
            (1, 2, 4, 5),
            (3, 4, 6, 7),
            (4, 5, 7, 8),
        ]
        for anc, qubits in zip(anc_x, x_stabilizers):
            circuit.h(anc)
            for q in qubits:
                circuit.cx(q, anc)
            circuit.h(anc)

        z_stabilizers = [
            (0, 3, 1, 4),
            (1, 4, 2, 5),
            (3, 6, 4, 7),
            (4, 7, 5, 8),
        ]
        for anc, qubits in zip(anc_z, z_stabilizers):
            for q in qubits:
                circuit.cx(q, anc)

        for qubit in range(self.n_physical):
            circuit.measure(qubit, qubit)

        return circuit

    def logical_error_rate_from_counts(
        self, counts: dict[str, int], logical_state: str = "0"
    ) -> float:
        """Decode by combining row/column majorities to mimic surface-code logic."""

        if logical_state not in {"0", "1"}:
            raise ValueError("Only logical states '0' and '1' are supported.")

        expected_logical = int(logical_state)
        total_shots = sum(counts.values())
        logical_errors = 0

        for bitstring, shots in counts.items():
            bits = bitstring[::-1]
            data_bits = bits[:9]
            rows = [
                1 if data_bits[start : start + 3].count("1") >= 2 else 0
                for start in (0, 3, 6)
            ]
            cols = [
                1 if data_bits[start::3][:3].count("1") >= 2 else 0 for start in range(3)
            ]
            votes = rows + cols
            logical_out = 1 if votes.count(1) >= 3 else 0
            if logical_out != expected_logical:
                logical_errors += shots

        if total_shots == 0:
            return 0.0

        return logical_errors / total_shots
