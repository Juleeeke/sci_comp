# SVD Homework: English Submission

This submission completes all 15 problems and the optional complex-SVD challenge in the attached assignment. The first page retains the supplied eight-row course template, translated into English. Course, class, name, student ID, date, instructor and grade are blank. The Word file contains native editable Office equations. The PDF is exported from that exact Word file.

## Deliverables

- `03_最终实验报告/SVD_Homework_English.docx`: editable template-based report.
- `03_最终实验报告/SVD_Homework_English.pdf`: matching submission PDF.
- `01_指导资料/`: unchanged original assignment and original template.
- `02_实验本体/`: complete Python source, archived photograph, generated matrices, raw reconstructions, numerical tables, spectra, plots and assertions.
- `04_报告源码/`: report content, DOCX builder and cached Office equations.
- `06_验证记录/delivery_verification.json`: exact final-file validation and hashes.

The report includes all theoretical proofs, exact least-squares examples, five grayscale reconstruction ranks, all twenty noisy-matrix approximation ranks, four figures, the one-page essay and complete numerical source code in Appendix A. The numerical experiments passed 39 assertions. The noisy data are a controlled generated experiment; their approximate signal rank is five while the noisy matrix has numerical rank eighty.

## Numerical reproduction

Run from this folder:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python 02_实验本体/run_experiments.py
```

On Windows activate `.venv\Scripts\activate` instead. The input image is archived, so execution needs no network access after installation. `grayscale.npy` preserves the unrounded luminance input. Display clipping is separate from reported raw Frobenius errors. The random seed is 20261009 and the noise multiplier is 0.05. Floating-point digits can vary slightly with numerical-library versions.

## Report rebuild

```sh
python -m pip install -r 04_报告源码/requirements-build.txt
python 04_报告源码/build_report.py
soffice --headless --convert-to pdf --outdir 00_Deliverables 03_最终实验报告/SVD_Homework_English.docx
python verify_delivery.py
```

Word can also export its editable document to PDF. The provided PDF was exported using bundled LibreOfficeDev. Changing fonts or exporters can alter pagination, so inspect the new PDF. Cached equations permit rebuilding the unchanged report without Microsoft Word. If LaTeX formula definitions in `content.py` are changed, conversion currently also uses Microsoft Word's locally installed `mathml2omml.xsl`; that stylesheet is not redistributed. Alternatively edit the native equations directly in Word and export the document again.

The source-preservation checks in `verify_delivery.py` refer to the original user's local paths; adjust or skip only those path comparisons on another computer. Numerical checks and report-content checks are self-contained. Final-page-count checks reflect this delivered version.
