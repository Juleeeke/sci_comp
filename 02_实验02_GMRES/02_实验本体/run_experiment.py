"""Reproduce Lab 2: sparse systems and finite-difference BVP.

Run: ../../.venv/bin/python run_experiment.py (from this directory).
All reported residuals are true, unpreconditioned Euclidean residuals.
"""

from __future__ import annotations

import json
import math
import platform
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.sparse import csr_matrix, diags, lil_matrix, tril, triu, save_npz
from scipy.sparse.linalg import LinearOperator, gmres as scipy_gmres, spilu, spsolve, spsolve_triangular


HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
OUT.mkdir(exist_ok=True)
DATA = HERE / 'data'
DATA.mkdir(exist_ok=True)
TOL = 1e-11
RESTART = 30
MAXITER = 10000
GS_MAXITER = 10000
REPEATS = 5


def matrix_11() -> csr_matrix:
    n = 300
    return diags([35 * np.ones(n - 1), 61.0001 * np.ones(n), 25 * np.ones(n - 1)], [-1, 0, 1], format="csr")


def matrix_12() -> csr_matrix:
    n = 100
    a = diags([np.ones(n - 1), np.arange(1, n + 1, dtype=float), np.ones(n - 1)], [-1, 0, 1], format="lil")
    a[0, n - 1] = n
    a[n - 1, 0] = n
    return a.tocsr()


def matrix_13() -> csr_matrix:
    """Explicit reading of the displayed matrix, including its unusual corners."""
    n = 100
    a = diags(
        [np.ones(n - 3), np.ones(n - 2), 2 * np.ones(n - 1),
         4 * np.ones(n), 2 * np.ones(n - 1), np.ones(n - 2)],
        [-3, -2, -1, 0, 1, 2], format="lil",
    )
    a[1, n - 1] = 2  # printed row 2, last column
    a[n - 1, 1] = 3  # printed last row, column 2
    return a.tocsr()


def forcing(x: np.ndarray) -> np.ndarray:
    p = (1 + x) ** 2
    return (1 - p) * np.exp(x) - np.pi**2 * np.cos(np.pi * x) + np.pi * p * np.sin(np.pi * x) - 1 - np.exp(-x) * np.cos(np.pi * x)


def exact_u(x: np.ndarray) -> np.ndarray:
    return np.exp(x) + np.cos(np.pi * x)


def bvp_matrix(n: int) -> tuple[csr_matrix, np.ndarray, np.ndarray]:
    h = 1 / n
    x = np.arange(1, n) * h
    p = (1 + x) ** 2
    lower = 2 + h * p
    diag = -(4 + 2 * h * h * np.exp(-x))
    upper = 2 - h * p
    a = diags([lower[1:], diag, upper[:-1]], [-1, 0, 1], format="csr")
    f = 2 * h * h * forcing(x)
    f[0] -= lower[0] * 2
    f[-1] -= upper[-1] * (math.e - 1)
    return a, f, x


def sample(history: list[dict], start: float, iteration: int, a: csr_matrix, b: np.ndarray, x: np.ndarray, truth: np.ndarray | None) -> float:
    residual = float(np.linalg.norm(b - a @ x))
    error = float(np.linalg.norm(x - truth)) if truth is not None else None
    history.append({"iteration": iteration, "time_s": time.perf_counter() - start, "residual": residual, "error": error})
    return residual


def gauss_seidel(a: csr_matrix, b: np.ndarray, truth: np.ndarray | None) -> dict:
    setup_start = time.perf_counter()
    low = tril(a, format="csr")
    up = triu(a, k=1, format="csr")
    setup_s = time.perf_counter() - setup_start
    x = np.zeros_like(b)
    start = time.perf_counter()
    hist: list[dict] = []
    r0 = sample(hist, start, 0, a, b, x, truth)
    threshold = TOL * r0
    status = "maxiter"
    for k in range(1, GS_MAXITER + 1):
        x = spsolve_triangular(low, b - up @ x, lower=True)
        residual = sample(hist, start, k, a, b, x, truth)
        if residual <= threshold:
            status = "converged"
            break
        if not np.isfinite(residual) or residual > 1e12 * r0:
            status = "diverged"
            break
    return {"x": x, "history": hist, "status": status, "iterations": k, "solve_s": time.perf_counter() - start, "setup_s": setup_s}


def restarted_gmres(a: csr_matrix, b: np.ndarray, truth: np.ndarray | None, use_ilu: bool) -> dict:
    setup_start = time.perf_counter()
    ilu = None
    if use_ilu:
        ilu = spilu(a.tocsc(), drop_tol=1e-4, fill_factor=10, permc_spec="NATURAL")
    setup_s = time.perf_counter() - setup_start if use_ilu else 0.0
    x = np.zeros_like(b)
    start = time.perf_counter()
    hist: list[dict] = []
    r0 = sample(hist, start, 0, a, b, x, truth)
    threshold = TOL * r0
    status = "maxiter"
    count = 0
    while count < MAXITER:
        r = b - a @ x
        beta = np.linalg.norm(r)
        if beta <= threshold:
            status = "converged"
            break
        v = np.zeros((len(b), RESTART + 1))
        z = np.zeros((len(b), RESTART))
        h = np.zeros((RESTART + 1, RESTART))
        v[:, 0] = r / beta
        base = x.copy()
        for j in range(RESTART):
            z[:, j] = ilu.solve(v[:, j]) if ilu is not None else v[:, j]
            w = a @ z[:, j]
            for i in range(j + 1):
                h[i, j] = np.dot(v[:, i], w)
                w -= h[i, j] * v[:, i]
            # Reorthogonalize to reduce loss of orthogonality.
            for i in range(j + 1):
                correction = np.dot(v[:, i], w)
                h[i, j] += correction
                w -= correction * v[:, i]
            h[j + 1, j] = np.linalg.norm(w)
            if h[j + 1, j] > 1e-14:
                v[:, j + 1] = w / h[j + 1, j]
            rhs = np.zeros(j + 2)
            rhs[0] = beta
            y = np.linalg.lstsq(h[:j + 2, :j + 1], rhs, rcond=None)[0]
            candidate = base + z[:, :j + 1] @ y
            count += 1
            residual = sample(hist, start, count, a, b, candidate, truth)
            x = candidate
            if residual <= threshold:
                status = "converged"
                break
            if h[j + 1, j] <= 1e-14 or count >= MAXITER:
                status = "breakdown" if h[j + 1, j] <= 1e-14 else "maxiter"
                break
        if status != "maxiter":
            break
    return {"x": x, "history": hist, "status": status, "iterations": count, "solve_s": time.perf_counter() - start, "setup_s": setup_s}


def reference(a: csr_matrix, b: np.ndarray, ilu: bool) -> dict:
    pre = None
    if ilu:
        fac = spilu(a.tocsc(), drop_tol=1e-4, fill_factor=10, permc_spec="NATURAL")
        pre = LinearOperator(a.shape, matvec=fac.solve)
    x, info = scipy_gmres(a, b, M=pre, rtol=TOL, atol=0, restart=RESTART, maxiter=MAXITER // RESTART)
    return {"info": int(info), "true_residual": float(np.linalg.norm(b - a @ x)), "x": x}


def summary(result: dict, a: csr_matrix, b: np.ndarray, truth: np.ndarray | None) -> dict:
    x = result["x"]
    out = {key: result[key] for key in ["status", "iterations", "setup_s", "solve_s"]}
    out["total_s"] = result["setup_s"] + result["solve_s"]
    out["residual"] = float(np.linalg.norm(b - a @ x))
    out["relative_residual"] = out["residual"] / float(np.linalg.norm(b))
    if truth is not None:
        out["error_l2"] = float(np.linalg.norm(x - truth))
    return out


def run_case(case: str, a: csr_matrix, b: np.ndarray, truth: np.ndarray | None, methods: tuple[str, ...], grid_n: int | None = None) -> dict:
    tag = case.replace(' ', '_').replace('=', '_')
    save_npz(DATA / (tag + '_A.npz'), a)
    np.savez(DATA / (tag + '_vectors.npz'), b=b, truth=truth)
    data = {"name": case, "shape": list(a.shape), "nnz": int(a.nnz), "norm_b": float(np.linalg.norm(b)), "methods": {}}
    if grid_n is not None:
        data["grid_n"] = grid_n
    direct = spsolve(a, b)
    data["direct_residual"] = float(np.linalg.norm(b - a @ direct))
    if truth is not None:
        data["direct_error_l2"] = float(np.linalg.norm(direct - truth))
    for method in methods:
        func = gauss_seidel if method == "Gauss-Seidel" else (lambda aa, bb, tt: restarted_gmres(aa, bb, tt, method == "ILU-GMRES"))
        runs = [func(a, b, truth) for _ in range(REPEATS)]
        order = np.argsort([r["setup_s"] + r["solve_s"] for r in runs])
        selected = runs[int(order[len(order) // 2])]
        item = summary(selected, a, b, truth)
        item["median_total_s"] = float(np.median([r["setup_s"] + r["solve_s"] for r in runs]))
        item["min_total_s"] = float(min(r["setup_s"] + r["solve_s"] for r in runs))
        item["max_total_s"] = float(max(r["setup_s"] + r["solve_s"] for r in runs))
        item["history"] = selected["history"]
        np.savetxt(OUT / (tag + '_' + method + '_solution.csv'), selected['x'], delimiter=',', header='x', comments='')
        if method != "Gauss-Seidel":
            ref = reference(a, b, method == "ILU-GMRES")
            item["scipy_info"] = ref["info"]
            item["scipy_residual"] = ref["true_residual"]
            item["scipy_solution_difference_l2"] = float(np.linalg.norm(selected["x"] - ref["x"]))
        if grid_n is not None:
            h = 1 / grid_n
            err = selected["x"] - truth
            item["bvp_error_max"] = float(np.max(np.abs(err)))
            item["bvp_error_discrete_l2"] = float(np.sqrt(h * np.dot(err, err)))
        data["methods"][method] = item
        print(case, method, item["status"], item["iterations"], f"res={item['residual']:.3e}", f"t={item['median_total_s']:.4f}s", flush=True)
    return data


def main() -> None:
    assert matrix_11().nnz == 898
    a12 = matrix_12()
    assert a12[0, 99] == 100 and a12[99, 0] == 100 and a12[99, 99] == 100
    a13 = matrix_13()
    assert a13[1, 99] == 2 and a13[99, 1] == 3 and a13[3, 0] == 1 and a13[99, 96] == 1
    assert abs(exact_u(np.array([0.0]))[0] - 2) < 1e-14
    assert abs(exact_u(np.array([1.0]))[0] - (math.e - 1)) < 1e-14
    cases = []
    for label, a in [("1.1", matrix_11()), ("1.2", matrix_12()), ("1.3", matrix_13())]:
        truth = np.ones(a.shape[0])
        cases.append(run_case(label, a, a @ truth, truth, ("Gauss-Seidel", "GMRES", "ILU-GMRES")))
    for n in [50, 100, 200]:
        a, b, x = bvp_matrix(n)
        cases.append(run_case(f"2.1 N={n}", a, b, exact_u(x), ("GMRES", "ILU-GMRES"), n))
    result = {
        "settings": {"rtol": TOL, "restart": RESTART, "maxiter": MAXITER, "gs_maxiter": GS_MAXITER, "repeats": REPEATS, "ilu_drop_tol": 1e-4, "ilu_fill_factor": 10, "ilu_ordering": "NATURAL", "initial_guess": "zeros", "timing": "median of five runs; includes residual/error sampling and setup"},
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "machine": platform.machine(), "platform": platform.platform()},
        "cases": cases,
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("Saved", OUT / "results.json")


if __name__ == "__main__":
    main()
