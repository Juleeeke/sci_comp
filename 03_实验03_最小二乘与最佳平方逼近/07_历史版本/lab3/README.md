# Lab 3 — Least Squares and Best Square Approximation

## 提交文件

- `report/main.pdf`：全英文最终实验报告，封面仅保留标题。
- `report/main.tex`：可编辑、可单文件编译的 LaTeX 源码，图形以矢量命令内嵌。
- `Lab3_submission.zip`：完整提交包（原题、代码、输入数据、计算结果、图表、报告与校验文件）。

已完成全部七项实验：1.1、1.2、1.3、2.1、2.2、2.3、3.1。没有替换原题中的人口或翼型数据。

## 复现

在本 `lab3` 目录执行：

```bash
../.venv/bin/python experiment/run_experiment.py
../.venv/bin/python experiment/verify_results.py
../.venv/bin/python experiment/build_report.py
bash report/compile.sh
../.venv/bin/python experiment/verify_delivery.py
../.venv/bin/python experiment/package_submission.py
```

在其他电脑可创建环境并安装 `requirements.txt` 中的依赖，将上述 Python 路径替换成环境中的 `python`。运行代码不需要联网。`compile.sh` 优先调用 PATH 中的 Tectonic，再使用本机已有的应用内 Tectonic 和缓存；其他电脑可以使用本地 TeX 发行版编译 `report/main.tex`，也可在 Codex 内打开它编译。LaTeX 使用常见包 `amsmath`、`amssymb`、`booktabs`、`array`、`xcolor`、`pict2e`、`lmodern`、`hyperref`、`geometry`。

`run_experiment.py` 从保留的原题 Markdown 提取输入并保存为 CSV，再计算各题结果和独立图表。`verify_results.py` 使用原 PDF 数据、精确有理数、独立 LAPACK 例程和独立积分规则核验；38 项校验的逐项记录位于 `experiment/results/verification.json`。`build_report.py` 将 `report/template.tex.in` 的计算结果和图形占位符展开为独立的 `main.tex`；修改报告时应修改模板再重新生成。

## 文件结构

- `2-2-DLSM-BSA--Application--lab.pdf` / `.md`：保留的原始题目。
- `experiment/data/`：五个拟合点、24 行人口数据、129 行翼型坐标。
- `experiment/run_experiment.py`：自编高斯消元、Householder QR 和全部实验。
- `experiment/results/results.json`：完整系数、残差、RSS、条件数、参考解和环境版本。
- `experiment/results/*.csv`：逐点拟合值与残差。
- `experiment/results/figures/`：独立的 PDF / PNG 图表，翼型独立图使用等比例几何视图。
- `experiment/results/verification.json`：数值和源数据验证。
- `experiment/results/delivery_validation.json`：报告、图表和文件验证。
- `report/`：报告生成模板、最终 LaTeX、PDF 和编译脚本。
- `MANIFEST.sha256`：压缩包内文件的 SHA-256 清单。
- `package_verification.json`：压缩包完整性、文件内容和哈希核对回执（放在压缩包旁）。

## 原题解释与结果边界

1. 第 1.1 题 PDF 与 Markdown 的第三行都是 `x1 + x2 + 2*x2 = 2`，主结果按字面使用系数行 `(1, 3, 0)`。报告另列可能的 `(1, 1, 2)` 读法及其完整解，没有将其当作已确认的更正。
2. 人口模型以 `t = year - 1790`（年）、`u = t / 100`（世纪）拟合；`x0` 同其他参数一起估计。最小化的是对数空间 RSS，另列人口尺度 RSS、RMSE 和最大误差，不声称进行了预测验证。
3. 连续逼近最小化积分平方误差；2.1、2.2、2.3 的结果分别为 `x - 1/6`、`3x/5`、`3x/pi`。
4. 翼型按原始遍历次序在前缘分成上、下表面，各含 65 个点，共用原始第 65 行前缘点；不按 y 的正负划分。采用题给全部四个基函数、等权离散最小二乘。报告为观察误差放大了 y 轴并明确标注；独立图使用等比例几何视图。不作空气动力学验证声明。
