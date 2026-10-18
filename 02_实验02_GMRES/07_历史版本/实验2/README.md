# Lab 2: GMRES for Large Sparse Linear Systems

The original lab handout and lecture files in this directory are preserved. The completed experimental work is in `experiment/`; the English LaTeX report and PDF are in `report/`.

## Deliverables

- `report/main.pdf`: final six-page English report.
- `report/main.tex`: editable, self-contained LaTeX source. All numerical figures are embedded as standard LaTeX picture commands; no external graphics files are needed.
- `experiment/run_experiment.py`: all assigned matrix and boundary-value computations.
- `experiment/build_report.py`: regenerates the report source from the saved measurements.
- `experiment/results/results.json`: complete numerical results and selected per-iteration histories.
- `experiment/results/verification.json`: checks of the recorded results.

## Reproduce

From this directory, run:

```bash
../.venv/bin/python experiment/run_experiment.py
../.venv/bin/python experiment/verify_results.py
../.venv/bin/python experiment/build_report.py
bash report/compile.sh
```

The commands require NumPy and SciPy in `../.venv`. Timing values are machine-dependent and will change on another run. `report/main.tex` can also be opened and compiled directly in the Codex LaTeX editor. It is a single-file document.

## Source interpretation

The handout's boundary-value equation uses `t` in one second-derivative symbol, while the variable, exact solution, finite-difference equation, and lecture slide all use `x`. We used the `x` derivative. The displayed matrix for system 1.3 contains ellipses; the report and code state the explicit nonzero pattern used. The grid sizes follow the handout: 50, 100, and 200.
