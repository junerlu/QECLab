"""Helpers to sweep physical noise strengths and estimate logical error rates."""

from __future__ import annotations

from typing import Dict, List

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from qec_lab.codes import BaseCode, RepetitionCode3
from qec_lab.noise import (
    bit_flip_noise_model,
    depolarizing_noise_model,
    amplitude_damping_noise_model,
)

_NOISE_BUILDERS = {
    "bit_flip": bit_flip_noise_model,
    "depolarizing": depolarizing_noise_model,
    "amplitude_damping": amplitude_damping_noise_model,
}


def run_physical_qubit(
    p: float, logical_state: str = "0", shots: int = 4096, noise_type: str = "bit_flip"
) -> float:
    """Estimate the physical error rate for a single qubit under a noise model."""

    if logical_state not in {"0", "1"}:
        raise ValueError("Only logical states '0' and '1' are supported.")
    if noise_type not in _NOISE_BUILDERS:
        raise ValueError(f"Unknown noise_type '{noise_type}'.")

    circuit = QuantumCircuit(1, 1)
    if logical_state == "1":
        circuit.x(0)

    circuit.measure(0, 0)

    noise_model = _NOISE_BUILDERS[noise_type](p)
    simulator = AerSimulator(noise_model=noise_model)
    compiled = transpile(circuit, simulator)
    counts = simulator.run(compiled, shots=shots).result().get_counts()

    expected = logical_state
    total_shots = sum(counts.values())
    wrong_shots = sum(shot for bitstring, shot in counts.items() if bitstring != expected)

    if total_shots == 0:
        return 0.0

    return wrong_shots / total_shots


def run_code_on_noise_grid(
    code: BaseCode,
    ps: List[float],
    noise_type: str = "bit_flip",
    logical_state: str = "0",
    shots: int = 4096,
) -> Dict[float, float]:
    """Run Monte Carlo sweeps to map physical p values to logical error rates."""

    if noise_type not in _NOISE_BUILDERS:
        raise ValueError(f"Unknown noise_type '{noise_type}'.")

    results: Dict[float, float] = {}
    noise_builder = _NOISE_BUILDERS[noise_type]

    for p in ps:
        noise_model = noise_builder(p)
        circuit = code.build_circuit(logical_state=logical_state)
        simulator = AerSimulator(noise_model=noise_model)
        compiled = transpile(circuit, simulator)
        counts = simulator.run(compiled, shots=shots).result().get_counts()
        logical_error = code.logical_error_rate_from_counts(
            counts, logical_state=logical_state
        )
        results[p] = logical_error
        print(
            f"[{code.name} | noise={noise_type}] p={p:.4f}, logical error={logical_error:.4f}"
        )

    return results


if __name__ == "__main__":
    ps = [0.001, 0.005, 0.01, 0.02, 0.05]

    print("Running physical qubit baseline...")
    physical_results = {p: run_physical_qubit(p) for p in ps}

    repetition_code = RepetitionCode3()
    print("Running 3-qubit repetition code sweep...")
    repetition_results = run_code_on_noise_grid(
        repetition_code, ps, noise_type="bit_flip"
    )

    print("\nBaseline physical errors:")
    print(physical_results)
    print("Repetition code logical errors:")
    print(repetition_results)
