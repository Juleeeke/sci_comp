"""Build a standalone English LaTeX report from results.json."""

from __future__ import annotations

import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
CASES = {case["name"]: case for case in DATA["cases"]}
REPORT = HERE.parent / "report"
REPORT.mkdir(exist_ok=True)


def sci(value: float, digits: int = 2) -> str:
    if value == 0:
        return "$0$"
    mantissa, exponent = f"{value:.{digits}e}".split("e")
    return rf"${mantissa}\times10^{{{int(exponent)}}}$"


def ms(value: float) -> str:
    return f"{value * 1000:.3f}"


def method_tex(method: str) -> str:
    return method.replace("-", "--")


def linear_table() -> str:
    rows = []
    for case in ["1.1", "1.2", "1.3"]:
        for method, item in CASES[case]["methods"].items():
            rows.append(
                f"{case} & {method_tex(method)} & {item['iterations']} & "
                f"{sci(item['residual'])} & {sci(item['error_l2'])} & "
                f"{ms(item['median_total_s'])} & {item['status']} \\\\"
            )
        if case != "1.3":
            rows.append(r"\midrule")
    return "\n".join(rows)


def plot_points(history: list[dict], key: str, maximum: int = 90) -> list[tuple[float, float]]:
    count = len(history)
    if count <= maximum:
        indices = list(range(count))
    else:
        indices = sorted(set(round(i * (count - 1) / (maximum - 1)) for i in range(maximum)))
    return [(history[i]["time_s"] * 1000, max(history[i][key], 1e-17)) for i in indices]


def picture_plot(series: list[tuple[str, list[tuple[float, float]]]], ylabel: str,
                 xlabel: str = "Elapsed solve time (ms)", xlog: bool = False,
                 width: int = 80, height: int = 63) -> str:
    """Use only standard LaTeX picture primitives; no external plot files."""
    all_x = [x for _, points in series for x, _ in points]
    all_y = [y for _, points in series for _, y in points]
    x_min = min(all_x) if xlog else 0.0
    x_max = max(all_x)
    if x_max == x_min:
        x_max = x_min * 1.01 if xlog else 1.0
    ymin_exp = math.floor(math.log10(min(all_y)))
    ymax_exp = math.ceil(math.log10(max(all_y)))
    if ymax_exp <= ymin_exp:
        ymax_exp = ymin_exp + 1
    left, bottom, right, top = 13.0, 14.0, width - 3.0, height - 14.0

    def xp(x: float) -> float:
        fraction = (math.log(x / x_min) / math.log(x_max / x_min)) if xlog else (x - x_min) / (x_max - x_min)
        return left + fraction * (right - left)

    def yp(y: float) -> float:
        return bottom + (math.log10(y) - ymin_exp) / (ymax_exp - ymin_exp) * (top - bottom)

    lines = [r"{\setlength{\unitlength}{1mm}\begin{picture}(" + f"{width},{height}" + r")",
             rf"\put({left:.2f},{bottom:.2f}){{\line(1,0){{{right-left:.2f}}}}}",
             rf"\put({left:.2f},{bottom:.2f}){{\line(0,1){{{top-bottom:.2f}}}}}",
             rf"\put({left:.2f},0){{\makebox({right-left:.2f},4){{\scriptsize {xlabel}}}}}",
             rf"\put({left:.2f},{height-3}){{\makebox({right-left:.2f},3){{\scriptsize {ylabel}}}}}"]
    legend = []
    names = {"Gauss-Seidel": "GS", "GMRES": "GMRES", "ILU-GMRES": "ILU--GMRES", "Second order": "$h^2$"}
    marks = {"Gauss-Seidel": r"$\circ$", "GMRES": r"$\times$", "ILU-GMRES": r"$\bullet$", "Second order": r"$\diamond$"}
    for name, _ in series:
        legend.append(names[name] + " " + marks[name])
    legend_tex = r"\quad ".join(legend)
    lines.append(rf"\put({left:.2f},{height-8:.2f}){{\makebox({right-left:.2f},3)[l]{{\scriptsize {legend_tex}}}}}")
    for exponent in sorted(set([ymin_exp, (ymin_exp + ymax_exp) // 2, ymax_exp])):
        yy = yp(10 ** exponent)
        lines.append(rf"\put({left-2:.2f},{yy:.2f}){{\line(1,0){{2}}}}")
        lines.append(rf"\put(0,{yy-1.2:.2f}){{\makebox({left-2:.2f},2.4)[r]{{\scriptsize $10^{{{exponent}}}$}}}}")
    xticks = [x_min, math.sqrt(x_min * x_max), x_max] if xlog else [0, x_max / 2, x_max]
    for val in xticks:
        xx = xp(val)
        label = f"{val:.3f}" if xlog else f"{val:.1f}"
        lines.append(rf"\put({xx:.2f},{bottom-1:.2f}){{\line(0,1){{1}}}}")
        lines.append(rf"\put({xx-4:.2f},{bottom-5:.2f}){{\makebox(8,3){{\scriptsize {label}}}}}")
    for name, points in series:
        thickness = {"Gauss-Seidel": "0.30pt", "GMRES": "0.50pt", "ILU-GMRES": "0.85pt", "Second order": "0.25pt"}[name]
        lines.append(r"\linethickness{" + thickness + "}")
        xy = [(xp(x), yp(y)) for x, y in points]
        for (x1, y1), (x2, y2) in zip(xy, xy[1:]):
            lines.append(rf"\qbezier({x1:.2f},{y1:.2f})({(x1+x2)/2:.2f},{(y1+y2)/2:.2f})({x2:.2f},{y2:.2f})")
        step = max(1, len(xy) // 7)
        for x, y in xy[::step]:
            if name == "GMRES":
                lines.append(rf"\put({x-.48:.2f},{y-.48:.2f}){{\framebox(.96,.96){{}}}}")
            elif name == "ILU-GMRES":
                lines.append(rf"\put({x:.2f},{y:.2f}){{\makebox(0,0){{\scriptsize $\bullet$}}}}")
            elif name == "Gauss-Seidel":
                lines.append(rf"\put({x:.2f},{y:.2f}){{\makebox(0,0){{\scriptsize $\circ$}}}}")
    lines.append(r"\end{picture}}")
    return "\n".join(lines)


def plot_axis(case: str, key: str, ylabel: str) -> str:
    series = [(method, plot_points(item["history"], key)) for method, item in CASES[case]["methods"].items()]
    return picture_plot(series, ylabel)


def linear_figures() -> str:
    all_figures = []
    for case in ["1.1", "1.2", "1.3"]:
        all_figures.append(
            r"\begin{figure}[p]\centering" + "\n"
            + r"\begin{minipage}{0.49\textwidth}\centering" + "\n"
            + plot_axis(case, "residual", r"$\|b-Ax_m\|_2$") + "\n"
            + r"\end{minipage}\hfill" + "\n"
            + r"\begin{minipage}{0.49\textwidth}\centering" + "\n"
            + plot_axis(case, "error", r"$\|x^*-x_m\|_2$") + "\n"
            + r"\end{minipage}" + "\n"
            + r"\caption{Experiment " + case + r": residual and solution error against solver time. "
            + r"Only plotted points are thinned; all recorded iterations remain in the JSON data. "
            + (r"The Gauss--Seidel curve stops at the divergence safeguard." if case == "1.2" else r"All three methods use the same relative-residual target.")
            + r"}\end{figure}"
        )
    return "\n\n".join(all_figures)


def bvp_table() -> str:
    rows = []
    for n in [50, 100, 200]:
        case = CASES[f"2.1 N={n}"]
        for method, item in case["methods"].items():
            rows.append(
                f"{n} & {method_tex(method)} & {item['iterations']} & "
                f"{sci(item['residual'])} & {sci(item['bvp_error_max'])} & "
                f"{sci(item['bvp_error_discrete_l2'])} & {ms(item['median_total_s'])} \\\\"
            )
        if n != 200:
            rows.append(r"\midrule")
    return "\n".join(rows)


def orders_table() -> str:
    rows = []
    for method in ["GMRES", "ILU-GMRES"]:
        items = [CASES[f"2.1 N={n}"]["methods"][method] for n in [50, 100, 200]]
        vals = []
        for key in ["bvp_error_max", "bvp_error_discrete_l2"]:
            vals += [math.log(items[i][key] / items[i + 1][key], 2) for i in [0, 1]]
        rows.append(f"{method_tex(method)} & {vals[0]:.3f} & {vals[1]:.3f} & {vals[2]:.3f} & {vals[3]:.3f} \\\\")
    return "\n".join(rows)


def bvp_figure() -> str:
    c = CASES["2.1 N=200"]
    series = [(method, plot_points(item["history"], "residual", 130)) for method, item in c["methods"].items()]
    return (r"\begin{figure}[t]\centering" + "\n" +
            picture_plot(series, "True residual norm", width=130, height=72) + "\n" +
            r"\caption{True residual history for the finest boundary-value grid ($N=200$). The GMRES curve is decimated for display only.}\end{figure}")


def bvp_order_figure() -> str:
    series = []
    for method in ["GMRES", "ILU-GMRES"]:
        points = [(1 / n, CASES[f"2.1 N={n}"]["methods"][method]["bvp_error_max"]) for n in [200, 100, 50]]
        series.append((method, points))
    series.append(("Second order", [(0.005, 3.10625e-5), (0.02, 4.97e-4)]))
    return (r"\begin{figure}[t]\centering" + "\n" +
            picture_plot(series, "Maximum nodal error", "Mesh width $h$", xlog=True, width=130, height=72) + "\n" +
            r"\caption{Observed maximum nodal error versus mesh width. The $h^2$ line is a slope-two reference, not a fitted model.}\end{figure}")


TEMPLATE = r"""\documentclass[a4paper,11pt]{article}
\usepackage[margin=22mm]{geometry}
\usepackage{amsmath,booktabs,graphicx}
\usepackage[colorlinks=true,linkcolor=blue!40!black,urlcolor=blue!40!black]{hyperref}
\hypersetup{pdftitle={Lab 2: GMRES for Large Sparse Linear Systems},pdfauthor={Scientific Computing Lab}}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\begin{document}
\begin{titlepage}
\centering\vspace*{33mm}
{\Large Scientific Computing Laboratory\par}\vspace{12mm}
{\Huge\bfseries Lab 2\par}\vspace{5mm}
{\LARGE GMRES for Large Sparse Linear Systems\par}\vspace{14mm}
{\Large Experimental Report\par}
\vfill
{\large 8 October 2026\par}
\end{titlepage}

\begin{abstract}
This report reproduces all four tasks in the Lab 2 handout. Three prescribed sparse systems are solved with Gauss--Seidel, restarted GMRES, and ILU-preconditioned GMRES. A finite-difference boundary-value problem is solved on three grids with the two GMRES variants. We report true residuals, errors against known solutions, elapsed times, and solver-library cross-checks. At a common relative-residual target of $10^{-11}$, Gauss--Seidel diverges for system 1.2, whereas both GMRES variants converge. In the tridiagonal problems, the specified incomplete factorization is effectively exact and preconditioned GMRES finishes in one Krylov step. The boundary-value errors decrease at approximately second order as the grid is refined.
\end{abstract}

\section{Tasks and interpretation of the source}
The handout prescribes three linear systems with $b=A\mathbf{1}$, hence the exact algebraic solution is $x^*=\mathbf{1}$. System 1.1 is a $300\times300$ tridiagonal matrix with diagonal $61.0001$, subdiagonal $35$, and superdiagonal $25$. System 1.2 has size $100$, diagonal $(1,2,\ldots,100)$, unit first off-diagonals, and two corner entries $a_{1,100}=a_{100,1}=100$.

The ellipses in the printed system 1.3 do not define every entry formally. For reproducibility, we use the directly displayed pattern: size $100$; diagonal $4$; first lower and upper diagonals $2$; second lower and upper diagonals $1$; third lower diagonal $1$; and the exceptional entries $a_{2,100}=2$, $a_{100,2}=3$. All unspecified entries are zero. This construction reproduces the displayed first, second, fourth, and last rows and has 593 nonzeros. The result is conditional on this explicit reading of the figure.

For the boundary-value problem, the handout prints $d^2u/dt^2$ although its independent variable, supplied difference equation, and lecture slide all use $x$. We therefore solve
\begin{equation}
u''(x)-(1+x)^2u'(x)-e^{-x}u(x)=f(x),\quad 0<x<1,\qquad u(0)=2,\quad u(1)=e-1,
\end{equation}
where
\begin{equation}
f(x)=[1-(1+x)^2]e^x-\pi^2\cos(\pi x)+\pi(1+x)^2\sin(\pi x)-1-e^{-x}\cos(\pi x).
\end{equation}
The known exact solution is $u(x)=e^x+\cos(\pi x)$. The handout requests $N=50,100,200$; the slide's smaller grid examples are illustrative and are not substituted for these assigned grids.

\section{Algorithms and experimental protocol}
Gauss--Seidel uses $A=L+U$ with $L$ including the diagonal and iterates $Lx^{(k+1)}=b-Ux^{(k)}$. GMRES builds a Krylov basis by modified Gram--Schmidt with a second orthogonalization pass. At each inner step it solves the small least-squares problem and records the actual residual of the reconstructed iterate. Restart length is 30. Right preconditioning uses an incomplete LU factorization $M\approx A$, with $z_j=M^{-1}v_j$ and Arnoldi applied to $Az_j$. The reported ILU implementation is SciPy SuperLU's threshold ILU (drop tolerance $10^{-4}$, fill factor 10, natural ordering), rather than a separately coded ILU(0). SciPy's reference \texttt{gmres} applies its \texttt{M} argument as a left preconditioner; we use it to check the final solution and true residual, not to require identical intermediate iterates.

All solvers start from zero. Convergence requires $\|b-Ax_m\|_2\leq10^{-11}\|b\|_2$, evaluated using the \emph{original}, unpreconditioned system. The iteration cap is 10,000. Gauss--Seidel is also stopped and labeled divergent if its residual exceeds $10^{12}$ times its initial value or becomes non-finite. This safeguard does not count as convergence. We report $\|b-Ax_m\|_2$ and, for systems 1.1--1.3, $\|x^*-x_m\|_2$.

Each method/problem combination is run five times. The table gives the median wall time, including matrix splitting or ILU setup and per-iteration true-residual/error sampling. The plotted history is the median-time run, and its horizontal axis measures solve time after setup. Timings are short, machine-dependent Python measurements; the iteration and error comparisons are more stable than sub-millisecond timing ratios. NumPy @@NUMPY@@, SciPy @@SCIPY@@, Python @@PYTHON@@, @@MACHINE@@ are used.

\section{Three prescribed sparse systems}
\begin{table}[ht]\centering\small
\caption{Solver results for the three algebraic systems. Time is the median of five runs and includes setup. The error column uses the known solution $\mathbf{1}$.}
\begin{tabular}{llrrrrl}\toprule
Case & Method & Iter. & $\|b-Ax\|_2$ & $\|x-\mathbf{1}\|_2$ & Time (ms) & Outcome\\\midrule
%%LINEAR_TABLE%%
\bottomrule\end{tabular}\end{table}

The tridiagonal system 1.1 converges under all three methods. The preconditioner preserves its tridiagonal elimination pattern, so the factorization is effectively exact and one Krylov step suffices. For system 1.2, Gauss--Seidel exhibits rapid growth instead of convergence. Its first row is far from diagonally dominant because of the $100$ corner coefficient; this explains why the standard sufficient convergence condition does not apply, while the measured divergence establishes the outcome for this particular ordering. Both GMRES variants converge. For system 1.3, all three converge, with ILU--GMRES requiring the fewest Krylov steps. These observations concern the specified matrices and solver settings, not a universal ranking.

%%LINEAR_FIGURES%%

\section{Finite-difference boundary-value problem}
For $x_i=ih$, $h=1/N$, centered differences give
\begin{align}
\frac{u_{i+1}-2u_i+u_{i-1}}{h^2}
-(1+x_i)^2\frac{u_{i+1}-u_{i-1}}{2h}
-e^{-x_i}u_i&=f(x_i),\\
[2+h(1+x_i)^2]u_{i-1}-[4+2h^2e^{-x_i}]u_i
+[2-h(1+x_i)^2]u_{i+1}&=2h^2f(x_i).
\end{align}
Boundary terms $u_0=2$ and $u_N=e-1$ are moved into the right-hand side of the $(N-1)\times(N-1)$ system. For the interior solution $u_h$, we compute
\begin{equation}
E_\infty=\max_{1\leq i\leq N-1}|u_i-u(x_i)|,\qquad
E_{2,h}=\left[h\sum_{i=1}^{N-1}(u_i-u(x_i))^2\right]^{1/2}.
\end{equation}
\begin{table}[ht]\centering\small
\caption{Boundary-value results. Each grid uses $N-1$ interior unknowns; time is median total time including setup.}
\begin{tabular}{rlrrrrr}\toprule
$N$ & Method & Iter. & $\|F-AU\|_2$ & $E_\infty$ & $E_{2,h}$ & Time (ms)\\\midrule
%%BVP_TABLE%%
\bottomrule\end{tabular}\end{table}

%%BVP_FIGURE%%

The measured convergence order between grids $N$ and $2N$ is $p=\log_2(E_N/E_{2N})$.
\begin{table}[ht]\centering\small
\caption{Observed grid-convergence orders.}
\begin{tabular}{lrrrr}\toprule
Method & $E_\infty$: 50--100 & $E_\infty$: 100--200 & $E_{2,h}$: 50--100 & $E_{2,h}$: 100--200\\\midrule
%%ORDERS_TABLE%%
\bottomrule\end{tabular}\end{table}

%%ORDER_FIGURE%%

Both error measures approach the expected second-order behavior of centered finite differences. The unpreconditioned GMRES iteration count rises sharply on finer grids. With this tridiagonal operator and the chosen ILU settings, the factorization reproduces the direct solve to roundoff; ILU--GMRES therefore uses one Krylov step at every grid size. The remaining error is primarily the discretization error, not a failure of the linear solver. A looser linear-solver tolerance distorted the finest-grid error, so the reported run uses $10^{-11}$ throughout.

\section{Independent checks and limitations}
The code checks selected displayed matrix entries, the boundary values, and the nonzero count. A sparse direct solve provides an independent algebraic reference for every case. Independently called \texttt{scipy.sparse.linalg.gmres} returns success for every custom GMRES run, and their solutions agree to within @@MAXDIFF@@ in Euclidean norm; the largest difference occurs in the ill-conditioned finest-grid solve. Direct-solve residuals are at most @@MAXDIRECT@@. The two boundary-value error measures and their orders are computed against the analytic solution, not against the direct numerical solve.

The handout asks students to compare AI-assisted code with library functions. Here the custom Arnoldi/GMRES implementation is cross-checked with SciPy's GMRES and a sparse direct solve; neither library result is treated as an exact continuum solution. Timing includes instrumentation and is not a low-level performance benchmark. The 1.3 matrix interpretation, ILU parameters, stopping rule, and divergence rule are fully stated so that the results can be reproduced or revised if the instructor supplies a more explicit matrix.

\section{Conclusion}
All assigned systems and grid sizes were completed. GMRES handled the case where Gauss--Seidel diverged. ILU preconditioning greatly reduced Krylov iterations for these matrices, reaching one step when the factorization was effectively exact. The finite-difference solution showed approximately second-order convergence under grid refinement. True residual checks, known-solution errors, sparse direct solves, and SciPy GMRES cross-checks support the numerical results.

\appendix
\section{Reproduction}
From the \texttt{experiment} directory, run \texttt{../../.venv/bin/python run\_experiment.py}, followed by \texttt{../../.venv/bin/python build\_report.py}. The first command writes \texttt{results/results.json}; the second regenerates this standalone \texttt{main.tex}, with all plotted data embedded. Compile the source in the Codex LaTeX editor. The provided handout and lecture slides remain in the parent experiment directory.
\end{document}
"""


def main() -> None:
    diffs = [m.get("scipy_solution_difference_l2", 0) for c in DATA["cases"] for m in c["methods"].values()]
    direct = [c["direct_residual"] for c in DATA["cases"]]
    replacements = {
        "%%LINEAR_TABLE%%": linear_table(),
        "%%LINEAR_FIGURES%%": linear_figures(),
        "%%BVP_TABLE%%": bvp_table(),
        "%%ORDERS_TABLE%%": orders_table(),
        "%%BVP_FIGURE%%": bvp_figure(),
        "%%ORDER_FIGURE%%": bvp_order_figure(),
        "@@NUMPY@@": DATA["environment"]["numpy"],
        "@@SCIPY@@": DATA["environment"]["scipy"],
        "@@PYTHON@@": DATA["environment"]["python"],
        "@@MACHINE@@": DATA["environment"]["machine"],
        "@@MAXDIFF@@": sci(max(diffs), 3),
        "@@MAXDIRECT@@": sci(max(direct), 3),
    }
    report = TEMPLATE
    for marker, value in replacements.items():
        report = report.replace(marker, value)
    assert "%%" not in report and "@@" not in report
    target = REPORT / "main.tex"
    target.write_text(report, encoding="utf-8")
    print("Saved", target, "bytes", target.stat().st_size)


if __name__ == "__main__":
    main()
