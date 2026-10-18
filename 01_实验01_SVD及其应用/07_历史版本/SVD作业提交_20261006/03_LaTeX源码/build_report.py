from pathlib import Path
import json,csv,shutil
R=Path(__file__).resolve().parent; O=R.parent/'02_实验本体/results'
def load(n):return json.loads((O/n).read_text())
m=load('matrix_summary.json'); im=load('image_summary.json'); f=load('eigenfaces_summary.json'); q=load('edge_quantization_summary.json'); t=load('temporal_summary.json'); run=load('run_summary.json')
for p in O.glob('*.png'):shutil.copy2(p,R/'figures'/p.name)
parts=[]
def add(s):parts.append(s)
def mat(a):return r'\begin{pmatrix}'+r'\\'.join(' & '.join(f'{v:.6f}' for v in row) for row in a)+r'\end{pmatrix}'
def tab(headers,rows,fmt=None):
 add(r'\begin{center}\small\begin{tabular}{'+(fmt or 'r'*len(headers))+r'}\toprule{}'+' & '.join(headers)+r'\\\midrule'+'\n'+ '\n'.join(' & '.join(map(str,row))+r'\\' for row in rows)+r'\bottomrule\end{tabular}\end{center}')
def fig(n,caption,width='.90'):
 add(r'\begin{figure}[H]\centering\includegraphics[width='+width+r'\linewidth]{figures/'+n+r'}\caption{'+caption+r'}\end{figure}')
add(r'''\documentclass[UTF8,a4paper,11pt,fontset=fandol]{ctexart}
\usepackage[margin=22mm]{geometry}
\usepackage{amsmath,amssymb,booktabs,graphicx,float,xcolor,fancyhdr,fvextra,hyperref}
\hypersetup{colorlinks=true,linkcolor=blue!45!black,urlcolor=blue!45!black,pdftitle={SVD及其应用实验报告}}
\setlength{\parindent}{2em}
\setlength{\parskip}{4pt}
\linespread{1.18}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{科学计算实验}\fancyhead[R]{SVD 及其应用}\fancyfoot[C]{\thepage}
\setlength{\headheight}{15pt}
\DefineVerbatimEnvironment{code}{Verbatim}{fontsize=\small,breaklines=true,frame=single}
\begin{document}
\hypersetup{pageanchor=false}\begin{titlepage}
\centering\vspace*{22mm}
{\Large 科学计算课程\par}\vspace{12mm}
{\Huge\bfseries 第一节上机实验\par}\vspace{7mm}
{\LARGE SVD 及其应用\par}\vspace{18mm}
{\large 实验报告\par}\vspace{16mm}
\vfill
\end{titlepage}\hypersetup{pageanchor=true}
\tableofcontents\newpage
\section{实验目标、数据与完成范围}
按课程附件完成以下内容：给定矩阵的 SVD 与能量分析；灰度图重建、RGB 对比网格、全部 $k$ 的指标计算、三类曲线以及三个关键发现；共享基在人脸识别、低带宽上传、三维表示和时序编码中的提高实验。

图像采用 scikit-image 的 astronaut.png（NASA 图源），大小为 $512\times512\times3$；读入为 float64，并除以 255 归一化。人脸使用 AT\&T（ORL）公开数据，共 40 人、400 张 $112\times92$ 灰度图。原始图像与人脸数据保存在实验目录，重新运行无需下载。

\textbf{完成边界：}核心部分全部实现。Eigenfaces 与量化使用真实公开静态人脸；三维部分使用合成曲面，时序部分使用模拟轨迹，均属于教学机制验证，不代表真实三维扫描、真实视频或边缘设备部署结果。未虚构课堂分组讨论记录。
\section{给定矩阵的 SVD}
\subsection{矩阵组装与输入核对}
将附件矩阵逐行录入后发现，印出的 $A$ 对应 $Q_5\Sigma Q_4$，因此此处 $Q_4$ 扮演 $V^T$ 的角色。采用该乘法与印刷矩阵的最大元素差为 $3.276\times10^{-5}$；若使用 $Q_4^T$，差异达 41.700658。前者差异与输入仅保留六位小数相符。本报告统一分析组装矩阵，不擅自对输入重新正交化。

附件将 $Q$ 称为“正定矩阵”，但它们非对称且近似正交。实测 $\|Q_5^TQ_5-I\|_F=2.284\times10^{-6}$，$\|Q_4^TQ_4-I\|_F=2.176\times10^{-6}$。
''')
add(r'\[A='+mat(m['A'])+r'.\]')
add(r'''\subsection{数学原理与算法}
对 $A\in\mathbb R^{m\times n}$，约化 SVD 写为
\[
 A=U\Sigma V^T=\sum_{i=1}^{r}\sigma_i u_i v_i^T,\qquad
 A_k=\sum_{i=1}^{k}\sigma_i u_i v_i^T.
\]
其中 $\sigma_i$ 降序排列，$u_i,v_i$ 为左右奇异向量，并满足
\[
 Av_i=\sigma_i u_i,\quad A^Tu_i=\sigma_i v_i,\quad
 A^TAv_i=\sigma_i^2v_i,\quad AA^Tu_i=\sigma_i^2u_i.
\]
非方阵 $A$ 不宜直接称有左右“特征向量”；这里的特征关系属于 $A^TA$ 和 $AA^T$。截断近似在 Frobenius 范数意义下最优，且
\[
 E(k)=\frac{\sum_{i=1}^k\sigma_i^2}{\sum_{i=1}^r\sigma_i^2},\qquad
 \frac{\|A-A_k\|_F}{\|A\|_F}=\sqrt{1-E(k)}.
\]
教学实现使用 \texttt{eigh} 求 $A^TA$ 特征对，再计算 $u_i=Av_i/\sigma_i$；以 \texttt{numpy.linalg.svd} 交叉核验。构造 $A^TA$ 会使条件数平方，因此后续计算直接使用 SVD。两种方法的奇异值最大绝对差为 $5.487\times10^{-11}$。
\subsection{秩、奇异值及能量结果}
''')
tab([r'$k$',r'$\sigma_k$',r'$E(k)$',r'相对误差'],[[i+1,f'{s:.9f}',f'{m["energy"][i]["energy"]:.12f}',f'{m["energy"][i]["relative_error"]:.3e}'] for i,s in enumerate(m['singular_values'])])
add(r'''四个奇异值均为正，故 $\operatorname{rank}(A)=4$，为满列秩；$\kappa_2(A)\approx100000.071$。保留前两项已有约 $99.999901\%$ 能量，但精确秩仍为 4。$AA^T$ 有一个额外零特征值，$A^TA$ 的四个特征值均为正。附录给出左右奇异向量及四个秩一矩阵，求和重构误差约为 $5.975\times10^{-14}$。
\section{SVD 图像压缩}
\subsection{灰度图的三行核心代码}
\par\noindent\begin{minipage}{\linewidth}\begin{code}
A = img @ np.array([0.2126, 0.7152, 0.0722])
U, s, Vt = np.linalg.svd(A, full_matrices=False)
A_k = (U[:, :20] * s[:20]) @ Vt[:20, :]
\end{code}
\end{minipage}\par
输入 \texttt{img} 已转换为 $[0,1]$ 浮点数，输出形状为 $(512,512)$。显示时执行 \texttt{np.clip(A\_k,0,1)}。\par\texttt{full\_matrices=False} 返回约化形状，不等于只计算前 $k$ 项。
''')
fig('01_grayscale_rank20.png','灰度原图与 $k=20$ 的截断重建。')
add(r'''\subsection{RGB 三通道与可视化网格}
分别对 R、G、B 分解，以相同 $k$ 截断后堆叠为彩色图。按附件选择
\[k\in\{1,2,3,5,8,12,20,35,50,80,120\}.\]
原图与 11 个重建组成 $3\times4$ 网格。图中可见小 $k$ 仅保留大致颜色和轮廓，随着 $k$ 增加，边缘与纹理逐步恢复。
''')
fig('02_rgb_rank_grid.png','原图与各截断阶数的 RGB 重建；PSNR 使用裁剪前的理论误差。','1.0')
add(r'''\subsection{不显式重建的指标计算}
设图像高、宽、通道数为 $H,W,C$，定义
\[
 T=\sum_c\sum_i\sigma_{c,i}^2,\qquad R_k=\sum_c\sum_{i>k}\sigma_{c,i}^2.
\]
由酉不变性，所有通道误差平方和就是 $R_k$，故
\[
 E(k)=1-\frac{R_k}{T},\quad e_{\mathrm{rel}}=\sqrt{\frac{R_k}{T}},\quad
 \mathrm{MSE}=\frac{R_k}{HWC},\quad\mathrm{PSNR}=10\log_{10}\frac{1}{\mathrm{MSE}}.
\]
\[
 P(k)=Ck(H+W+1),\qquad \mathrm{CR}(k)=\frac{HWC}{P(k)}=\frac{HW}{k(H+W+1)}.
\]
每通道分别保存 $Hk$ 个左向量元素、$k$ 个奇异值和 $kW$ 个右向量元素。满秩时尾和为 0，PSNR 记为 $+\infty$。从末尾累加奇异值平方，可避免总量减前缀导致的消减误差。
\par\noindent\begin{minipage}{\linewidth}\begin{code}
e = np.stack([s**2 for _, s, _ in svd_ch])
tail = np.concatenate([np.cumsum(e[:, ::-1], axis=1)[:, ::-1],
                       np.zeros((C, 1))], axis=1)
def stats(k):
    err2 = tail[:, k].sum()
    mse = err2 / (H * W * C)
    return (H * W / (k * (H + W + 1)),
            np.sqrt(err2 / e.sum()),
            np.inf if mse == 0 else 10 * np.log10(1 / mse))
\end{code}
\end{minipage}\par
实际程序另记录参数量、MSE 与能量。完整指标表包含 $k=1,\ldots,512$ 的全部 512 行，保存为 \path{image_metrics_all_k.csv}。下表为代表性阶数：
''')
tab(['$k$',r'能量（\%）','相对误差','PSNR（dB）','参数压缩比'],[[v['k'],f'{v["energy"]*100:.5f}',f'{v["relative_error"]:.6f}',r'$+\infty$' if isinstance(v['psnr_db'],str) else f'{v["psnr_db"]:.3f}',f'{v["compression_ratio"]:.3f}'] for v in im['selected']])
add(r'''在 $k=1,4,20,80,120,256,512$ 上，程序将尾和结果与显式重建 MSE 交叉核验，全部通过。图像显示裁剪后的误差另存；裁剪改变矩阵，不能直接套用未裁剪的尾和等式。
\subsection{奇异值、质量与压缩比曲线}
''')
fig('03_singular_values.png','三通道奇异值衰减，纵轴为对数尺度。','.79')
fig('04_error_psnr.png','相对误差与 PSNR 随 $k$ 的变化；无穷值不绘作有限点。','.79')
fig('05_compression_ratio.png','参数压缩比及盈亏平衡点 $k^*=255.750$。','.79')
add(r'''\section{三个关键发现}
\subsection{能量占比不能替代视觉质量}
$k=1$ 时能量占比为 $78.5057\%$，PSNR 仅 11.856 dB；$k=4$ 时能量已有 $90.5566\%$，PSNR 仍为 15.428 dB。即使 $k=20$ 能量达到 $97.9497\%$，PSNR 也只有 22.061 dB。大面积背景、平均亮度贡献较大，能量较高不能保证纹理细节完整。
\subsection{盈亏平衡点：区分参数与字节}
由 $\mathrm{CR}>1$ 得
\[
 k<k^*=\frac{HW}{H+W+1}=\frac{262144}{1025}=255.750244.
\]
本图 $k\le255$ 时参数更少，$k\ge256$ 时参数更多。因此超过 $k^*$ 后，增加阶数虽然提高重建质量，但会“越压越大”。附件中约 353 对应 $620\times820$ 图像，不能沿用到本图。

以上假设每个标量占相同字节。原始 uint8 像素占 786432 B，$k=20$ 的 float32 因子占 246000 B，实际原始负载压缩比仅 $3.197$ 倍，而参数比为 $12.788$ 倍。float32 相对 uint8 的字节盈亏平衡点是 $255.750244/4\approx63.938$，从 $k=64$ 起因子已更大。PNG 文件大小为 791555 B，还包含编码与文件开销；本实验未与 JPEG 作率失真比较。
\subsection{细节失真观察}
''')
fig('06_detail_crop.png','相同局部区域对照：原图、$k=1$、$k=4$、$k=20$。','1.0')
add(r'''宇航服徽章、接缝和器件边缘较早模糊，大块颜色区域更容易保留。这表明本图细节需要更多奇异分量共同表达。小奇异值不普遍等同于高空间频率，观察到的趋势不是对所有图像成立的严格定理。
\section{提高实验：共享基表示}
\subsection{Eigenfaces 人脸识别}
将每张图展开为 $D=10304$ 维向量。固定随机种子 20260917，每人随机选 7 张训练、3 张测试，共 280/120 张。均值和基只用训练集计算，测试照片不参与拟合。两组包含相同身份、不同照片，属于已知身份的闭集识别。

令训练矩阵中心化为 $X_c$，对其 SVD 得到行基 $B_k$。投影与重建为
\[
 z=(x-\mu)B_k^T,\qquad \hat x=\mu+zB_k.
\]
识别在系数空间采用欧氏距离最近邻。主评估预先固定 $k=80$，其余 $k$ 用于敏感性分析，不以测试结果选择新参数。训练中心化矩阵数值秩为 279。
''')
fig('08_mean_eigenfaces.png','均值脸及前 11 个特征脸，各基图独立归一化显示。')
with (O/'eigenfaces_metrics.csv').open(encoding='utf-8-sig') as fp: face=list(csv.DictReader(fp))
# derive report directly from saved numerical metrics
add('% Eigenfaces metrics: see CSV for all columns.')
rows=f['metrics']
# names are read from the current outputs, not assumed from older report tables
tab(['$k$','正确 / 120',r'准确率（\%）','测试 PSNR（dB）'], [[v['k'],str(v['correct']),f"{100*v['accuracy']:.2f}",f"{v['test_psnr_db']:.3f}"] for v in rows if v['k'] in [1,5,20,32,80,200,279]])
add(r'''主结果为 118/120 正确，准确率 $98.33\%$；$k=200$ 和 279 时降为 $96.67\%$，虽然重建误差继续下降。这说明重建保真与识别判别力不是同一目标。单次划分结果不能解释为跨身份泛化保证。
''')
fig('07_eigenfaces_accuracy.png','识别准确率随保留主成分数量的变化。','.85')
fig('09_face_reconstructions.png','保留测试照片在不同阶数下的重建。')
add(r'''共享基与均值也占存储。$N$ 张图的参数压缩比为
\[
 \frac{ND}{D+kD+Nk}.
\]
本训练库 $N=280,k=80$ 时为 $3.366$ 倍。即使保留训练集全部非零方向，测试图像仍可能具有子空间外分量，故测试重建不一定无误差。
\subsection{边缘上传：每维 int8 量化}
采用 $k=32$ 的训练基，以训练系数每维 $0.1\%$ 和 $99.9\%$ 分位数定义 $\mathrm{lo},\mathrm{hi}$，并令 $s=(\mathrm{hi}-\mathrm{lo})/255$。编码和解码为
\[
 q=\operatorname{round}\!\left(\operatorname{clip}\!\left(\frac{z-\mathrm{lo}}{s},0,255\right)\right)-128,
 \qquad \hat z=(q+128)s+\mathrm{lo}.
\]
量化器仅由训练集标定。均值、共享基、lo、scale 均作为模型保存；两端应校验基 ID、版本和量化参数。本实验按固定除以 255 归一化，不需要每帧传输额外亮度参数。
''')
tab(['指标','本次结果'],[['浮点 / int8 重建 PSNR','21.442089 / 21.441348 dB'],['PSNR 损失 / 最大像素差','0.000742 dB / 0.021111'],['超范围系数比例',r'$0.2344\%$'],['量化后识别准确率',r'$96.67\%$'],['uint8 原帧 / 系数负载','10304 B / 32 B'],['共享模型原始负载','1360384 B'],['120 帧含模型压缩比','0.9064'],['摊销模型的盈亏平衡','133 帧']],fmt='ll')
add(r'''每帧负载虽缩小 322 倍，但短序列并不能抵消模型分发开销；相对原始像素节省需满足\[1360384+32N<10304N.\]以上未计网络包头、加密与重传。

平均 PSNR 损失很小，最大像素差却为 0.021111，不能复述附件中其他案例的 0.0015 为本次结果。系数化也不等于加密：系数仍能用于身份识别，持有基即可近似重建；未证明去标识化或隐私保护效果。
\subsection{三维共享基：合成曲面的教学演示}
3DMM 将对应顶点坐标和纹理分别表示为均值与基的线性组合：
\[
 S=\bar S+\sum_i\alpha_i b_i,\qquad T=\bar T+\sum_i\beta_i c_i.
\]
本次未获取真实三维扫描；构造 $40\times32$ 网格、1280 个顶点、3840 维坐标，以六种线性形变生成 200 个样本，160 个训练、40 个测试。只演示形状 PCA，不包含纹理 PCA 或从照片反演三维。
''')
fig('11_synthetic_3dmm.png','合成曲面与低秩重建，非真实三维人脸扫描。','1.0')
d=load('synthetic_3dmm_summary.json')
tab(['$k$','测试曲面 RMSE'],[[v['k'],f'{v["test_rmse"]:.6e}'] for v in d['metrics']])
add(r'''$k=6$ 时达到浮点精度，是因为数据生成机制本来只有六个线性自由度，不能据此声称真实人脸只需六个参数。
\subsection{时序共享基：模拟轨迹与差分编码}
ORL 没有连续采集时间戳，不能将文件顺序当视频。以一个测试样本的系数为中心，叠加振幅为训练系数标准差 0.12 倍的平滑正弦变化，生成 300 帧、32 维模拟轨迹。该构造主动满足平滑性，结果仅限于此条件。
''')
fig('10_synthetic_temporal_coefficients.png','模拟系数轨迹的前四维，非真实视频。','.85')
add(r'''每 60 帧记录绝对系数，其余保存相邻差；差分可能超出 int8，使用 int16，再用 zlib level=9 压缩。解压和累加后逐元素恢复量化系数，这不意味着对原图无损。
''')
tab(['表示方式','字节数'],[['直接 int8 系数',9600],['int16 差分',19200],['直接 int8 + zlib',1979],['int16 差分 + zlib',1387]],fmt='lr')
add(r'''公平比较双方均使用 zlib，额外压缩为 $1979/1387=1.427$ 倍，未达到附件案例的 $2\sim3$ 倍。仅做差分而不熵编码，反而使负载翻倍。包含一次模型分发时，300 帧相对原始像素压缩比为 2.270 倍。

此处周期绝对系数帧仅重置预测状态，没有重算基。真实应用可监测重建残差或分布漂移来触发新基，并同步基版本；本实验未验证真实场景切换、漂移阈值或与视频编码器的竞争性能。
\section{结论与复现说明}
给定矩阵满列秩为 4，奇异值跨五个数量级，少量分量能保留主要能量。图像实验表明，增加阶数能提升重建质量，但同时增加存储；能量、视觉质量、参数量和文件字节必须区分。

共享基使图像压缩与识别使用同一低维表示。模型摊销、量化截断和时序编码都有实际代价，必须结合样本数量与数据类型评价。真实 ORL 实验与三维、时序教学模拟分别报告，不将模拟收益扩展为真实部署结论。

本次使用智能体辅助阅读材料、核对矩阵、整理程序、执行计算及生成报告。Python 程序与原始数据随提交目录附上，运行命令为：
\par\noindent\begin{minipage}{\linewidth}\begin{code}
python -m pip install -r 02_实验本体/requirements.txt
python 02_实验本体/run_experiment.py
python 03_LaTeX源码/build_report.py
bash 03_LaTeX源码/compile.sh
\end{code}
\end{minipage}\par
''')
tab(['项目','本次运行环境'],[['Python',run['python']],['NumPy / SciPy',run['numpy']+' / '+run['scipy']],['Matplotlib / Pillow',run['matplotlib']+' / '+run['pillow']],['随机种子',20260917],['自动检查',f'{run["checks_passed"]}/{run["checks_total"]} 通过']],fmt='ll')
add(r'''完整指标、训练测试划分、逐张预测和校验项分别见实验结果目录中的 CSV 与 JSON；运行日志为 \path{run.log}。本报告由 LaTeX 编译，编译要求与复现步骤见文件夹说明。姓名、学号与班级未提供，封面留空。
\section*{参考资料}\addcontentsline{toc}{section}{参考资料}
\begin{enumerate}
\item 课程附件：《第一节上机实验——SVD 及其应用》，本次提交包保留原件。
\item AT\&T Laboratories Cambridge, The Database of Faces.\\\url{https://www.cl.cam.ac.uk/research/dtg/attarchive/facedatabase.html}
\item scikit-image, astronaut image.\\\url{https://scikit-image.org/docs/stable/api/skimage.data.html}
\item NumPy, numpy.linalg.svd.\\\url{https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html}
\item Turk M, Pentland A. Eigenfaces for Recognition. Journal of Cognitive Neuroscience, 1991, 3(1):71--86. DOI: 10.1162/jocn.1991.3.1.71.
\item Blanz V, Vetter T. A Morphable Model for the Synthesis of 3D Faces. SIGGRAPH, 1999:187--194. DOI: 10.1145/311535.311556.
\end{enumerate}
\newpage\appendix
\section{左右奇异向量与秩一展开}
以下数值保留六位小数，完整精度数组见 \path{matrix_decomposition.npz}。$U$ 的第 $i$ 列为左奇异向量；$V^T$ 的第 $i$ 行转置为右奇异向量。左右向量成对变号不改变分解。
''')
add(r'\[U='+mat(m['U'])+r',\qquad\]\[V^T='+mat(m['Vt'])+r'.\]')
add(r'令 $R_i=\sigma_i u_iv_i^T$，则 $A=R_1+R_2+R_3+R_4$，$A_k$ 为前 $k$ 项之和。')
for i in range(1,5):
 with (O/f'rank_one_{i}.csv').open() as fp:a=[[float(v) for v in row] for row in csv.reader(fp)]
 add(r'\[R_'+str(i)+'='+mat(a)+r'.\]')
add(r'''六位小数表格会引入舍入误差，不能用表格精度要求复现机器精度残差。直接对指导书印刷 $A$ 分解所得奇异值约为 $100.000000439$、$10.000000130$、$0.100000094$、$0.001000092$；其与组装矩阵有微小输入差异，两种版本均保存在结果数组中。
\end{document}''')
(R/'main.tex').write_text('\n\n'.join(parts))
print('Generated',R/'main.tex')
