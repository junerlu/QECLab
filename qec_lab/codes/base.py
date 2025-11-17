"""Abstract base class for quantum error-correcting codes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from qiskit import QuantumCircuit


class BaseCode(ABC):
    """Define the minimal interface required from any QEC code."""

    name: str
    n_physical: int
    n_logical: int = 1

    @abstractmethod
    def build_circuit(self, logical_state: str = "0") -> QuantumCircuit:
        """Build and return a full quantum circuit for this code.

        The circuit should:
        - Initialize the chosen logical state on one or more qubits.
        - Encode it into the physical qubits of the code.
        - Perform additional steps before measurement when required.
        - Measure relevant qubits at the end.

        The `NoiseModel` is applied externally when running the circuit on
        an Aer simulator.
        """

    @abstractmethod
    def logical_error_rate_from_counts(
        self, counts: dict[str, int], logical_state: str = "0"
    ) -> float:
        """Estimate the logical error rate from a Qiskit counts dictionary.

        Implementations should map measured bitstrings to logical outcomes,
        compare them with the expected logical state, and compute the fraction
        of shots that correspond to logical errors.
        """
