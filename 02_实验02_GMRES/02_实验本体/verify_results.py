"""Validate the recorded numerical experiment without rerunning timings."""

from __future__ import annotations

import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
cases = {case["name"]: case for case in data["cases"]}
checks: dict[str, bool] = {}
checks["all_assigned_cases_present"] = set(cases) == {"1.1", "1.2", "1.3", "2.1 N=50", "2.1 N=100", "2.1 N=200"}
checks["all_direct_residuals_small"] = all(case["direct_residual"] < 1e-10 for case in cases.values())
checks["gauss_seidel_diverges_only_in_1_2"] = (
    cases["1.2"]["methods"]["Gauss-Seidel"]["status"] == "diverged"
    and all(cases[name]["methods"]["Gauss-Seidel"]["status"] == "converged" for name in ["1.1", "1.3"])
)
checks["all_gmres_runs_converged"] = all(
    item["status"] == "converged" and item["relative_residual"] <= data["settings"]["rtol"] * 1.001
    for case in cases.values() for name, item in case["methods"].items() if "GMRES" in name
)
checks["scipy_gmres_cross_checks_passed"] = all(
    item["scipy_info"] == 0 and item["scipy_solution_difference_l2"] < 1e-7
    for case in cases.values() for name, item in case["methods"].items() if "GMRES" in name
)
checks["histories_match_final_metrics"] = all(
    abs(item["history"][-1]["residual"] - item["residual"]) <= max(1e-12, 1e-10 * item["residual"])
    and all(b["time_s"] >= a["time_s"] for a, b in zip(item["history"], item["history"][1:]))
    for case in cases.values() for item in case["methods"].values()
)
for method in ["GMRES", "ILU-GMRES"]:
    for metric in ["bvp_error_max", "bvp_error_discrete_l2"]:
        values = [cases[f"2.1 N={n}"]["methods"][method][metric] for n in [50, 100, 200]]
        orders = [math.log(values[i] / values[i + 1], 2) for i in [0, 1]]
        checks[f"second_order_{method}_{metric}"] = all(1.9 < order < 2.1 for order in orders)
output = {"checks": checks, "passed": sum(checks.values()), "total": len(checks), "all_passed": all(checks.values())}
(HERE / "results" / "verification.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
print(json.dumps(output, indent=2))
if not output["all_passed"]:
    raise SystemExit(1)
