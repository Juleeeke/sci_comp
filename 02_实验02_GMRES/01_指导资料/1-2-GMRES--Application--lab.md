Lab 2: Applying the GMRES Method to Large Sparse Linear Systems

【Class Hours】 2 class hours
【Objectives and Requirements】
Through this lab, students will become further familiar with using AI on a personal computer to write, debug, run, and analyze results of Python code; become familiar with the GMRES method and the incomplete LU (ILU) preconditioning technique for solving large sparse linear systems, and compare them with the Gauss–Seidel iteration, so as to understand the applicability and efficiency of these algorithms; and try to use these methods to solve a two-point boundary value problem.

【Notes】
\begin{itemize}
\item[1、] Pay attention to the difference between the computational expressions of Python code and their mathematical written form.
\item[2、] Observe the differences between the results produced by AI-assisted programming and those given by the Python–NumPy library functions.
\end{itemize}

【Lab Content】
Experiment 1.1: For the linear system $\mathrm{Ax}=\mathrm{b}$ :

$$
A=\left[\begin{array}{ccccc}
61.0001 & 25 & & & \\
35 & 61.0001 & 25 & & \\
& 35 & \ddots & \ddots & \\
& & \ddots & \ddots & 25 \\
& & & 35 & 61.0001
\end{array}\right]_{300 \times 300} \quad b=A\left[\begin{array}{c}
1 \\
1 \\
1 \\
\vdots \\
1
\end{array}\right]
$$

Solve it by the Gauss–Seidel method, the GMRES method, and the ILU-GMRES method, respectively; plot the curves of the residual $\mathrm{r}_{\mathrm{m}}=b-A x_m$ and the error $\left|x-x_{\mathrm{m}}\right|_2$ of the iterative results versus time, and compare the accuracy and efficiency of the three methods.

Experiment 1.2: For the linear system $\mathrm{Ax}=\mathrm{b}$ :

$$
A=\left(\begin{array}{ccccccc}
1 & 1 & 0 & \cdots & 0 & 0 & n \\
1 & 2 & 1 & \cdots & 0 & 0 & 0 \\
0 & 1 & 3 & \cdots & 0 & 0 & 0 \\
\vdots & \vdots & \vdots & \ddots & \ddots & \vdots & \vdots \\
0 & 0 & 0 & \ddots & \ddots & 1 & 0 \\
0 & 0 & 0 & \cdots & 1 & n-1 & 1 \\
n & 0 & 0 & \cdots & 0 & 1 & n
\end{array}\right)_{n \times n} \quad \mathbf{b}=\mathbf{A}\left[\begin{array}{c}
\mathbf{1} \\
\mathbf{1} \\
\mathbf{1} \\
\vdots
\end{array}\right], n=100
$$

Solve it by the Gauss–Seidel method, the GMRES method, and the ILU-GMRES method, respectively; plot the curves of the residual $\mathrm{r}_{\mathrm{m}}=b-A x_m$ and the error $\left|x-x_{\mathrm{m}}\right|_2$ of the iterative results versus time, and compare the accuracy and efficiency of the three methods.

Experiment 1.3: For the linear system $\mathrm{Ax}=\mathrm{b}$ :

$$
A=\left(\begin{array}{ccccccc}
4 & 2 & 1 & & & & \\
2 & 4 & 2 & 1 & & & 2 \\
1 & 2 & 4 & \ddots & \ddots & & \\
1 & 1 & \ddots & \ddots & \ddots & \ddots & \\
& 1 & \ddots & \ddots & \ddots & 2 & 1 \\
& & \ddots & \ddots & 2 & 4 & 2 \\
& 3 & & 1 & 1 & 2 & 4
\end{array}\right)_{n \times n}, b=A\left(\begin{array}{c}
1 \\
1 \\
\vdots \\
\vdots \\
1 \\
1
\end{array}\right), \quad n=100
$$

Solve it by the Gauss–Seidel method, the GMRES method, and the ILU-GMRES method, respectively; plot the curves of the residual $\mathrm{r}_{\mathrm{m}}=b-A x_m$ and the error $\left|x-x_{\mathrm{m}}\right|_2$ of the iterative results versus time, and compare the accuracy and efficiency of the three methods.

Experiment 2.1: Finite Difference Solution of a Two-Point Boundary Value Problem

$$
\left\{\begin{array}{l}
\frac{d^2 u}{d t^2}-(1+x)^2 \frac{d u}{d x}-e^{-x} u=f(x), 0<x<1, \\
f(x)=\left[1-(1+x)^2\right] e^x-\pi^2 \cos (\pi x)+\pi(1+x)^2 \sin (\pi x)-1-e^{-x} \cos (\pi x) \\
u(0)=2, \quad u(1)=e-1
\end{array}\right.
$$

(The exact solution is $u(x)=e^x+\cos (\pi x)$ .)
Perform a uniform grid partition of $[0,1]$ .

$$
x_0=0<x_1<\cdots<x_i<\cdots<x_{N-1}<x_N=1 \quad, \quad x_i=i \cdot h, 0 \leq i \leq N, h=\frac{1}{N}
$$

This yields the linear system $\mathrm{A} U=F$ :

$$
\left\{\begin{array}{c}
{\left[2+h\left(1+x_i\right)^2\right] u_{i-1}-\left[4+2 h^2 e^{-x_i}\right] u_i+\left[2-h\left(1+x_i\right)^2\right] u_{i+1}=2 h^2 f\left(x_i\right), 1 \leq i \leq N-1,} \\
u_0=2, \quad u_N=e-1 .
\end{array}\right.
$$

Please solve it by the GMRES method and the ILU-GMRES method, respectively.

Then $\left\{\mathrm{u}_{\mathrm{i}}\right\}_{i=0}^N$ corresponding to $\mathrm{N}=50,100,200$ can be obtained, and the errors can be computed as

$$
\left\|u_h-u\right\|_l=\max _{\mathbb{K} \leq N-1}\left|u_i-u\left(x_i\right)\right|, \quad \mid u_h-u \|_b=\sqrt{\sum_{i=1}^{N-1} h\left(u_i-u\left(x_i\right)\right)^2}
$$

Please solve it by the GMRES method and the ILU-GMRES method, respectively, and compare the accuracy and efficiency of the two methods.
