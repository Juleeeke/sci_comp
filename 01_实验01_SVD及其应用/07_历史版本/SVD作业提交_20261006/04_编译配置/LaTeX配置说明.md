# 编译方案与要求

检查环境：macOS arm64；系统 PATH 未找到 xelatex、latexmk 或 tectonic，已存在 Pandoc。随后发现应用自带 Tectonic 0.17.0，路径为 `/Applications/ChatGPT.app/Contents/Resources/tectonic/tectonic`。最终优先使用该编译器，无需全局安装 MacTeX 或上传在线平台。

## 本报告的要求

- XeTeX/XeLaTeX 兼容引擎（本次 Tectonic 0.17.0）。
- UTF-8 中文，ctexart 文档类；显式采用 Fandol 字体，避免依赖 macOS 专有字体。
- 宏包：ctex、geometry、amsmath、amssymb、booktabs、graphicx、float、xcolor、fancyhdr、fvextra、hyperref。
- 图片使用相对路径 `figures/`，需与 main.tex 一起保存。
- 首次运行 Tectonic 需要获取宏包/字体资源并写入用户缓存；缓存齐全后可重编译。
- 无 shell-escape、外部代码执行、BibTeX 或额外引用文件要求。

## 本地与在线选择

本任务需多张图片、实际 PDF 文件和可移植源码，因此用本地 Tectonic 完成工程编译及文件导出；源码也在内置 LaTeX 编辑器中打开。内置独立文档编译接口首次下载依赖时超时，且该接口不支持附属项目文件；实际多文件工程以本地命令行编译结果为准。

若换电脑没有编译器，可安装 Tectonic，或使用 TeX Live/MacTeX 的 XeLaTeX，连续编译两次生成目录。也可只上传 `03_LaTeX源码` 中的 main.tex 与 figures 到 Overleaf，主文件选 main.tex，编译器选 XeLaTeX。在线方案作为迁移说明，本次未上传作业。

官方资料：
- https://tectonic-typesetting.github.io/book/latest/installation/
- https://github.com/tectonic-typesetting/tectonic/releases/tag/tectonic%400.17.0

配置探测时曾下载官方便携发行包至临时目录，但无需安装，交付包不含二进制程序。
