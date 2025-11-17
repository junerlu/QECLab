"""Simple Qiskit Aer noise models used by the QEC lab experiments."""

from __future__ import annotations

from qiskit_aer.noise import NoiseModel, depolarizing_error, pauli_error, amplitude_damping_error

_SINGLE_QUBIT_GATES = ["id", "x", "y", "z", "h", "sx"]
_TWO_QUBIT_GATES = ["cx"]


def bit_flip_noise_model(p: float) -> NoiseModel:
    """Return a NoiseModel where each gate is followed by an X flip with prob p."""

    if not 0.0 <= p <= 1.0:
        raise ValueError("Probability p must be between 0 and 1.")

    noise_model = NoiseModel()
    single_qubit_error = pauli_error([("X", p), ("I", 1 - p)])
    two_qubit_error = single_qubit_error.tensor(single_qubit_error)

    for gate in _SINGLE_QUBIT_GATES:
        noise_model.add_all_qubit_quantum_error(single_qubit_error, gate)

    for gate in _TWO_QUBIT_GATES:
        noise_model.add_all_qubit_quantum_error(two_qubit_error, gate)

    return noise_model


def phase_flip_noise_model(p: float) -> NoiseModel:
    """Return a NoiseModel applying Z flips with probability p after each gate."""

    if not 0.0 <= p <= 1.0:
        raise ValueError("Probability p must be between 0 and 1.")

    noise_model = NoiseModel()
    single_qubit_error = pauli_error([("Z", p), ("I", 1 - p)])
    two_qubit_error = single_qubit_error.tensor(single_qubit_error)

    for gate in _SINGLE_QUBIT_GATES:
        noise_model.add_all_qubit_quantum_error(single_qubit_error, gate)

    for gate in _TWO_QUBIT_GATES:
        noise_model.add_all_qubit_quantum_error(two_qubit_error, gate)

    return noise_model


def depolarizing_noise_model(p: float) -> NoiseModel:
    """Return a simple depolarizing channel with strength p."""

    if not 0.0 <= p <= 1.0:
        raise ValueError("Probability p must be between 0 and 1.")

    noise_model = NoiseModel()
    single_qubit_error = depolarizing_error(p, 1)
    two_qubit_error = depolarizing_error(p, 2)

    for gate in _SINGLE_QUBIT_GATES:
        noise_model.add_all_qubit_quantum_error(single_qubit_error, gate)

    for gate in _TWO_QUBIT_GATES:
        noise_model.add_all_qubit_quantum_error(two_qubit_error, gate)

    return noise_model

def amplitude_damping_noise_model(gamma: float) -> NoiseModel:
    """Return a NoiseModel with amplitude-damping (T1-like) noise after each gate."""

    if not 0.0 <= gamma <= 1.0:
        raise ValueError("Damping parameter gamma must be between 0 and 1.")

    noise_model = NoiseModel()
    # Single-qubit amplitude-damping channel
    single_qubit_error = amplitude_damping_error(gamma)
    # For a 2-qubit gate, apply the same channel independently on both qubits
    two_qubit_error = single_qubit_error.tensor(single_qubit_error)

    for gate in _SINGLE_QUBIT_GATES:
        noise_model.add_all_qubit_quantum_error(single_qubit_error, gate)

    for gate in _TWO_QUBIT_GATES:
        noise_model.add_all_qubit_quantum_error(two_qubit_error, gate)

    return noise_model