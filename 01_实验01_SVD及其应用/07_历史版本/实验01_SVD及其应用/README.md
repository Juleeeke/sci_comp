# 实验 01：SVD 及其应用

优先阅读 `03_最终实验报告/实验01_SVD及其应用_实验报告.pdf`；需要编辑时打开同名 DOCX。姓名、学号、班级留空。

## 内容

- `01_指导资料`：用户两份 PDF 的原样副本，以及 Eigenfaces、3DMM 原论文。
- `02_实验本体/run_experiment.py`：全部实验，数据已随目录保存，运行无需联网。
- `02_实验本体/experiment.ipynb`：已执行的结果浏览笔记本；带重新计算入口。
- `02_实验本体/data`：astronaut 原图、ORL 原始压缩包与 400 张 PGM、来源与哈希。
- `02_实验本体/results`：完整指标 CSV、11 张图、精确矩阵/模型、编码文件、运行日志、验证记录。
- `02_实验本体/build_report.py`：根据真实结果生成 DOCX/Markdown。
- `03_最终实验报告`：DOCX、PDF、Markdown。

## 本机重新运行

在 `/Users/juleyau/code/sci_comp` 下：

```bash
.venv/bin/python 实验01_SVD及其应用/02_实验本体/run_experiment.py
.venv/bin/python 实验01_SVD及其应用/02_实验本体/build_report.py
```

主体运行会重新生成结果；数据下载、依赖安装和报告导出不计入主体耗时。
换电脑时，在课程根目录创建 Python 虚拟环境并安装 `02_实验本体/requirements.txt`。
`requirements-lock.txt` 保存本机确切版本，跨平台使用时可优先按 requirements.txt 安装。
Word 转 PDF 需 LibreOffice；本机的 `export_pdf.sh` 已设置中文字体路径并经过渲染核验。

## 关键约定

1. 给定 A 对应 `Q5 @ Sigma @ Q4`，Q4 在此作为 Vt。六位小数输入会有微小舍入差。
2. 所有理论图像指标使用未裁剪重建；裁剪只用于显示，裁剪误差另表。
3. 参数压缩比不是实际 PNG/JPEG 文件压缩比；字长和共享模型另计。
4. Eigenfaces 固定种子 20260917，每人训练 7 张、测试 3 张，k=80 预先固定；未用测试数据拟合基或量化器。
5. 3DMM 曲面、时序序列均为明确标注的合成演示；没有真实扫描/视频实验的泛化结论。
6. 系数化不保证隐私，能被用于身份分类，不能视为加密。

## 数据署名

ORL 数据：AT&T Laboratories Cambridge，官方来源与文件 SHA-256 见 `data/sources.json`。
Astronaut：NASA / scikit-image 官方示例图（公共领域），固定取 v0.25.2 仓库版本。

## 提交清单

`manifest_sha256.csv` 覆盖交付文件；排版检查缓存和 Python 缓存不纳入清单。
