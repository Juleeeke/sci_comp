# GMRES for Large Sparse Linear Systems

The independent assignment package contains the completed English report in three forms:

- `03_最终实验报告/Report.docx` is editable Word with native Office equations and the retained template cover table.
- `03_最终实验报告/Report.pdf` is compiled from `04_LaTeX源码/main.tex`, not exported from Word.
- `04_LaTeX源码/` contains standalone TeX, required figures and `compile.sh`.

`01_指导资料/` preserves the exact current assignment PDF, original Word template, extracted text and SHA-256 provenance. Class 230116, name yule yang and student ID 23376268 are filled from the user supplied screenshot. The current report date is 2026.10.17; instructor and grade remain empty. `COVERAGE.md` maps every assigned task to the report. `02_实验本体/` contains runnable code, data where applicable, actual full precision results, CSV files, plots and numerical verification. `06_验证记录/` contains the final audit and review record. Rendering intermediates are excluded from the delivery archive.

## Reproduce

Use Python 3.12 or 3.13 in a virtual environment. Install `requirements.txt`. From this directory:

```bash
python 02_实验本体/run_experiment.py
python 02_实验本体/verify_results.py
python 02_实验本体/plot_results.py
python make_content.py
python build_report.py --tex
bash 04_LaTeX源码/compile.sh
python build_report.py --word
python verify_delivery.py
```

LaTeX compilation runs before Word generation. An installed Tectonic or pdfLaTeX can compile the source; the script also supports the bundled macOS Tectonic and its existing local cache. The equation cache `equations.json` contains native editable OMML for every report equation. It makes routine Word rebuilding independent of a Microsoft Word installation. To convert newly added equations after changing the content, the builder uses the vendored MIT licensed latex2mathml and the Microsoft Office MathML stylesheet if available; otherwise provide a compatible MathML to OMML transform and regenerate the cache.

The audit can also inspect Word rendering when `06_验证记录/word_render/Report.pdf` is present. On delivery, the recorded audit documents the actual full rendering check. A later rerun without rendering data performs the structural Word and compiled PDF checks and records that the Word render was not rerun. Native Word pagination can vary with installed fonts; the delivered copy was rendered and checked using bundled LibreOffice. The PDF preserves the verified LaTeX layout.

Run `python render_validation.py` after generating the optional Word render to regenerate page review images. Use the document skill renderer in Codex, or export Word to `06_验证记录/word_render/Report.pdf` using a trusted office renderer. After changes rerun the numerical and artifact checks, visually review the outputs, and update checksums before packaging.

## 一键复现与填写规则

运行 `python reproduce.py` 可重跑本次作业。若科学计算和文档构建使用不同 Python，通过环境变量 `ARTIFACT_PYTHON` 指定文档 Python。班级、姓名、学号来自用户截图；本次日期为 2026.10.17，后续作业日期按实际情况填写。`student_profile.json` 保存本次封面值，教师及成绩留空。
