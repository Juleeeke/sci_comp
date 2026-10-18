# 第一节上机实验：SVD 及其应用

建议提交 `00_提交报告/第一节上机实验_SVD及其应用_实验报告.pdf`。若平台允许附件，同时提交完整文件夹压缩包，方便教师查看代码与数值结果。

封面仅保留标题，无需填写个人信息。

## 文件组织

- `00_提交报告`：LaTeX 编译的 PDF。
- `01_指导资料`：用户提供的指导 PDF 原件。
- `02_实验本体`：Python 源码、依赖清单、数据和重新运行的结果。
- `03_LaTeX源码`：`main.tex`、全部图片、`compile.sh` 和报告生成脚本。
- `04_编译配置`：本地配置说明、验证记录。

## 复现

在本文件夹根目录执行：

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r 02_实验本体/requirements.txt
python 02_实验本体/run_experiment.py
python 03_LaTeX源码/build_report.py
bash 03_LaTeX源码/compile.sh
```

`build_report.py` 会重建 main.tex 并复制结果图片；若已手动修改封面，请保留修改，直接运行 compile.sh 即可。仅修改排版或身份信息无需重跑实验。

## 范围

核心矩阵与图像压缩任务全部完成。Eigenfaces 和量化使用真实 ORL 数据；3D 部分与时序部分是明确标记的教学模拟，并非真实三维扫描或视频。原目录保持原样。

全部 512 个 k 的指标见 `02_实验本体/results/image_metrics_all_k.csv`。训练测试划分与逐样本预测均保存。`verification.json` 列出 22 项检查。
