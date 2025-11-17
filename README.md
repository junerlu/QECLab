# QEC Lab

QEC Lab is a lightweight playground for studying how canonical quantum error-correcting codes suppress noise when simulated with Qiskit and Aer. It bundles ready-to-run Monte Carlo sweeps, configurable noise models, and a notebook for visual inspection so you can compare physical and logical error rates without extra scaffolding.

## Highlights

- Reference codes: `RepetitionCode3`, `ShorCode9`, `RotatedSurfaceCodeD3`, and `SteaneCode7`, all implementing the shared `BaseCode` interface for encoders and decoders.
- Reusable noise models (`bit_flip`, `phase_flip`, `depolarizing`, `amplitude_damping`) built with `NoiseModel`, covering both single- and two-qubit gates.
- Experiment utilities (`run_physical_qubit`, `run_code_on_noise_grid`) that keep Monte Carlo sweeps tiny scripts instead of notebooks full of boilerplate.
- `notebooks/demo_repetition.ipynb` that walks through encoding, simulating noise, and plotting physical vs logical error rates.

## Repository layout

- `qec_lab/__init__.py` - convenience exports so `from qec_lab import RepetitionCode3` just works.
- `qec_lab/codes/` - implementations of the base class plus the 3-qubit repetition, 9-qubit Shor, distance-3 rotated surface, and 7-qubit Steane codes.
- `qec_lab/noise/models.py` - pure-Python builders that assemble Qiskit Aer `NoiseModel` instances.
- `qec_lab/experiments/sweep.py` - command-line helper that sweeps physical error probabilities and prints logical error estimates.
- `qec_lab/notebooks/demo_repetition.ipynb` - reproducible, well-commented notebook for visual learners.

## Project architecture

```text
qec_lab/
|-- __init__.py
|-- codes/
|   |-- __init__.py
|   |-- base.py
|   |-- repetition3.py
|   |-- shor9.py
|   |-- rotated_surface_d3.py
|   `-- steane7.py
|-- experiments/
|   `-- sweep.py
|-- noise/
|   |-- __init__.py
|   `-- models.py
|-- notebooks/
|   `-- demo_repetition.ipynb
`-- __pycache__/ (ignored during development)
```

The `codes` directory hosts encoder/decoder logic, `noise` declares Aer noise builders, `experiments` contains ready-to-run sweeps, and `notebooks` stores the interactive tutorial.

## QEC workflow

1. **Define a code** using `qec_lab.codes.BaseCode` (or one of the built-ins) so the logical state can be encoded, simulated, and decoded consistently.
2. **Select a noise model** from `qec_lab.noise.models` to attach bit-flip, phase-flip, depolarizing, or amplitude-damping channels to every gate with a tunable strength `p` or `gamma`.
3. **Run an experiment** via `qec_lab.experiments.sweep` (or the notebook helpers) to compile the circuit, launch Aer simulations across the chosen `ps`, and log physical vs logical error rates.
4. **Visualize and analyze** the resulting dictionaries in `notebooks/demo_repetition.ipynb` or your own scripts to compare baselines, spot suppression trends, and document findings.

## Requirements & installation

- Python 3.10 or newer
- `qiskit` and `qiskit-aer`
- `matplotlib` and `jupyter` (only required for plotting / notebooks)

Install everything into your virtualenv or Conda environment:

```bash
pip install qiskit qiskit-aer matplotlib jupyter
```

## Quick start

1. Install the dependencies shown above.
2. Run the sweep script to generate physical vs logical error data:

   ```bash
   python -m qec_lab.experiments.sweep
   ```

3. Launch the notebook for an interactive walkthrough:

   ```bash
   jupyter notebook qec_lab/notebooks/demo_repetition.ipynb
   ```

## Running experiments programmatically

You can import the helpers directly if you prefer scripts over notebooks:

```python
from qec_lab import RepetitionCode3, run_code_on_noise_grid

code = RepetitionCode3()
ps = [0.001, 0.005, 0.01, 0.02]
results = run_code_on_noise_grid(code, ps, noise_type="bit_flip", shots=4096)
print(results)
```

`run_physical_qubit` provides the corresponding baseline for a single qubit under the same noise model. Every helper prints progress so long sweeps can be monitored in a terminal.

## Extending

### Add a new QEC code

1. Create a file inside `qec_lab/codes/` and subclass `BaseCode`.
2. Implement `build_circuit` (return a circuit that encodes + measures) and `logical_error_rate_from_counts` (decode bitstrings produced by Aer).
3. Export the class from `qec_lab/codes/__init__.py` (and optionally from `qec_lab/__init__.py`) so it can be imported easily.
4. Re-run `experiments/sweep.py` or the notebook to compare the new code with the existing ones.

### Add a new noise model

1. Implement a builder in `qec_lab/noise/models.py` that returns a `NoiseModel`.
2. Register it in `_NOISE_BUILDERS` inside `experiments/sweep.py` so `noise_type="your_model"` becomes available to both scripts and notebooks.
3. Reference it from notebooks or your custom experiments just like the built-in options.

## Troubleshooting

- Make sure `qiskit-aer` is installed; missing simulators are the most common cause of runtime errors.
- The helpers only support logical states `"0"` and `"1"`; extend them if you need arbitrary stabilizer states.
- Simulations may take a while when you request millions of shots, so start with the defaults to sanity-check your setup.

## Future work

- Support higher-distance surface codes (d=5, 7, ...) to study threshold behavior systematically.
- Integrate more advanced decoders such as minimum-weight matching or neural-network-based decoders.
- Build a simple web front-end so users can pick noise models / codes via sliders and generate plots instantly.
- Add richer visualizations (syndrome timelines, logical error trajectories) for classroom demos and talks.
