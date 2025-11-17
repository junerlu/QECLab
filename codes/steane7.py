"""Seven-qubit Steane [[7,1,3]] code using Hamming-style decoding."""

from __future__ import annotations

from qiskit import QuantumCircuit

from .base import BaseCode


class SteaneCode7(BaseCode):
    """Encode one logical qubit into the 7-qubit Steane [[7,1,3]] code."""

    # 8 even-weight Hamming [7,4,3] codewords used in |0_L>
    _EVEN_CODEWORDS: tuple[str, ...] = (
        "0000000",
        "1010101",
        "0110011",
        "1100110",
        "0001111",
        "1011010",
        "0111100",
        "1101001",
    )

    _ODD_CODEWORDS: tuple[str, ...] = tuple(
        "".join("1" if b == "0" else "0" for b in cw) for cw in _EVEN_CODEWORDS
    )

    def __init__(self) -> None:
        self.name = "7-qubit Steane code"
        self.n_physical = 7
        self.n_logical = 1

    def build_circuit(self, logical_state: str = "0") -> QuantumCircuit:
        """Construct an encoding circuit and Z-basis measurements for Steane [[7,1,3]]."""

        if logical_state not in {"0", "1"}:
            raise ValueError("Only logical states '0' and '1' are supported.")

        circuit = QuantumCircuit(self.n_physical, self.n_physical)

        circuit.h(0)
        circuit.h(1)
        circuit.h(3)

        circuit.cx(0, 2)
        circuit.cx(3, 5)
        circuit.cx(1, 6)

        circuit.cx(0, 4)
        circuit.cx(3, 6)
        circuit.cx(1, 5)

        circuit.cx(0, 6)
        circuit.cx(1, 2)
        circuit.cx(3, 4)

        # If logical_state == "1", apply logical X (transversal X)
        if logical_state == "1":
            for q in range(self.n_physical):
                circuit.x(q)

        # Measure all 7 physical qubits in Z basis 
        circuit.measure(range(self.n_physical), range(self.n_physical))

        return circuit

    @staticmethod
    def _hamming_distance(a: str, b: str) -> int:
        """Compute Hamming distance between two equal-length bitstrings."""
        if len(a) != len(b):
            raise ValueError("Bitstrings must have the same length.")
        return sum(ch1 != ch2 for ch1, ch2 in zip(a, b))

    def _decode_logical_bit(self, bitstring: str) -> int:
        """Given a full measurement outcome bitstring, decode logical 0/1."""
        bits_str = bitstring[::-1]

        if len(bits_str) < self.n_physical:
            raise ValueError(
                f"Expected at least {self.n_physical} bits in measurement bitstring, "
                f"got '{bitstring}'."
            )
        data_bits = bits_str[: self.n_physical]
        best_logical = 0
        best_dist = self.n_physical + 1

        for cw in self._EVEN_CODEWORDS:
            d = self._hamming_distance(data_bits, cw)
            if d < best_dist:
                best_dist = d
                best_logical = 0

        for cw in self._ODD_CODEWORDS:
            d = self._hamming_distance(data_bits, cw)
            if d < best_dist:
                best_dist = d
                best_logical = 1

        return best_logical


    def logical_error_rate_from_counts(
        self, counts: dict[str, int], logical_state: str = "0"
    ) -> float:
        """Decode via Hamming-style lookup and estimate the logical error rate."""

        if logical_state not in {"0", "1"}:
            raise ValueError("Only logical states '0' and '1' are supported.")

        expected_logical = int(logical_state)
        total_shots = sum(counts.values())
        logical_errors = 0

        for bitstring, shots in counts.items():
            logical_out = self._decode_logical_bit(bitstring)
            if logical_out != expected_logical:
                logical_errors += shots

        if total_shots == 0:
            return 0.0

        return logical_errors / total_shots
