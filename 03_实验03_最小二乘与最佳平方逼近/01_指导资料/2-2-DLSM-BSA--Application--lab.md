Lab 3: Applications of Least Squares and Best Square Approximation

【Class Hours】 2 class hours
【Objectives and Requirements】
Through this lab, students will become further familiar with using AI on a personal computer to write, debug, run, and analyze results of Python code; become familiar with the least squares method for solving overdetermined linear systems and for fitting discrete data (both linear and nonlinear models), and with the best square approximation of continuous functions using orthogonal bases (including Legendre polynomials), so as to understand the applicability and numerical behaviour of these algorithms; and try to use these methods to fit real data (the U.S. population growth data and the RAE2822 airfoil geometry).

【Notes】
1. Pay attention to the difference between the computational expressions of Python code and their mathematical written form.
2. Observe the differences between the results produced by AI-assisted programming and those given by the Python–NumPy library functions.

【Lab Content】
**Experiment 1.1:** For the overdetermined linear system $\mathrm{Ax}=\mathrm{b}$ :

$$
\left\{\begin{array}{r}
x_1+2 x_2+4 x_3=-1, \\
2 x_1+x_2+x_3=4, \\
x_1+x_2+2 x_2=2, \\
x_1-x_2-2 x_3=1 .
\end{array}\right.
$$

Form the normal equations $\mathrm{A}^{\mathrm{T}} \mathrm{A} x=\mathrm{A}^{\mathrm{T}} \mathrm{b}$, solve for the least squares solution $x$, and report the residual $\mathrm{r}=\mathrm{b}-\mathrm{A} x$ and the residual sum of squares $\|\mathrm{r}\|_2^2$.

**Experiment 1.2:** For the following data points, obtain the fitted function by linear least squares approximation, and give the residual sum of squares (RSS).

| $i$ | $x$ | $y$ |
| :---- | :---- | :---- |
| 1     | 25    | 110   |
| 2     | 27    | 115   |
| 3     | 31    | 155   |
| 4     | 33    | 160   |
| 5     | 35    | 180   |

**Experiment 1.3:** Linear least squares approximation of the U.S. population growth model. Fit the following U.S. population data with the two models below, and compare them graphically.

$$
x(t)=x_0 e^{r t}, \qquad y=r t+a, \quad y=\ln x, \quad a=\ln x_0
$$

$$
x(t)=x_0 e^{\left(r_0 t-r_1 t^2 / 2\right)}
$$

| Year | Population / million |
| :--- | -------------------: |
| 1790 |                  3.9 |
| 1800 |                  5.3 |
| 1810 |                  7.2 |
| 1820 |                  9.6 |
| 1830 |                 12.9 |
| 1840 |                 17.1 |
| 1850 |                 23.2 |
| 1860 |                 31.4 |
| 1870 |                 38.6 |
| 1880 |                 50.2 |
| 1890 |                 62.9 |
| 1900 |                 76.0 |
| 1910 |                 92.0 |
| 1920 |                106.5 |
| 1930 |                123.2 |
| 1940 |                131.7 |
| 1950 |                150.7 |
| 1960 |                179.3 |
| 1970 |                204.0 |
| 1980 |                226.5 |
| 1990 |                251.4 |
| 2000 |                281.4 |
| 2010 |                308.7 |
| 2020 |                331.5 |

**Experiment 2.1:** Best square approximation by a linear polynomial. Find the best square approximation of

$$
f(x)=x^2
$$

on $[0,1]$ by a linear polynomial

$$
p(x)=c_0+c_1 x .
$$

1. Set up the least-squares error functional

   $$
   E\left(c_0, c_1\right)=\int_0^1\left(x^2-c_0-c_1 x\right)^2 d x .
   $$

2. Derive the normal equations.
3. Solve for $c_0$ and $c_1$.
4. Compute the squared error

   $$
   \left\|x^2-p(x)\right\|_2^2 .
   $$

**Experiment 2.2:** Legendre polynomial approximation. On $[-1,1]$, the first three Legendre polynomials are

$$
P_0(x)=1, \quad P_1(x)=x, \quad P_2(x)=\frac{1}{2}\left(3 x^2-1\right) .
$$

They satisfy

$$
\int_{-1}^1 P_i(x) P_j(x) d x=0 \quad \text { if } i \neq j
$$

and

$$
\int_{-1}^1 P_j(x)^2 d x=\frac{2}{2 j+1} .
$$

Let

$$
f(x)=x^3 .
$$

Find the best square approximation to $f$ from

$$
\operatorname{span}\left\{P_0, P_1, P_2\right\} .
$$

1. Write the approximation in the form

   $$
   p_2(x)=a_0 P_0(x)+a_1 P_1(x)+a_2 P_2(x) .
   $$

2. Use the formula

   $$
   a_j=\frac{\left\langle f, P_j\right\rangle}{\left\langle P_j, P_j\right\rangle}
   $$

   to compute $a_0, a_1, a_2$.
3. Write the final polynomial in both Legendre form and monomial form.

**Experiment 2.3:** Function fitting with a quadratic polynomial. Let

$$
f(x)=\sin (\pi x), \quad-1 \leq x \leq 1 .
$$

Find the best square approximation of $f$ from

$$
P_2=\operatorname{span}\left\{1, x, x^2\right\} .
$$

1. Set up the Gram matrix system using the monomial basis $\left\{1, x, x^2\right\}$.
2. Use symmetry to simplify the system as much as possible.
3. Determine the coefficients of the best quadratic approximation.
4. Explain why some coefficients must vanish due to symmetry.
5. Compare the result with the Taylor polynomial of $\sin (\pi x)$ at $x=0$.

**Experiment 3.1:** Approximation of the RAE2822 airfoil. Split the profile into the upper and lower surface curves, and represent the RAE2822 airfoil with the NACA-type basis functions

$$
y=\sum_{i=1}^N \alpha_i g_i(x), \quad x \in[0,1],
$$

$$
\left\{\begin{array}{ll}
g_1(x)=\sqrt{x}-x, & \\
g_i(x)=x^{i-1}(1-x), & i=2,3,4 .
\end{array}\right. \quad x \in[0,1]
$$

Use the least squares method to determine the coefficients $\alpha_i$ for the upper and lower curves separately, and compare the fitted curves with the given data.

![RAE2822 airfoil](image/参考题库/1792043437217.png)

The airfoil coordinates $(x, y)$ are given below.

```text
1.000000  0.000000
0.999398  0.000035
0.997592  0.000137
0.994588  0.000296
0.990393  0.000497
0.985016  0.000719
0.978470  0.000935
0.970772  0.001112
0.961940  0.001212
0.951995  0.001197
0.940961  0.001033
0.928864  0.000694
0.915735  0.000157
0.901604 -0.000600
0.886505 -0.001592
0.870476 -0.002829
0.853553 -0.004314
0.835779 -0.006048
0.817197 -0.008027
0.797850 -0.010244
0.777785 -0.012690
0.757051 -0.015357
0.735698 -0.018232
0.713778 -0.021289
0.691342 -0.024495
0.668445 -0.027814
0.645142 -0.031207
0.621490 -0.034631
0.597545 -0.038043
0.573365 -0.041397
0.549009 -0.044642
0.524534 -0.047719
0.500000 -0.050563
0.475466 -0.053099
0.450991 -0.055257
0.426635 -0.056979
0.402455 -0.058224
0.378510 -0.058974
0.354858 -0.059236
0.331555 -0.059046
0.308658 -0.058459
0.286222 -0.057547
0.264302 -0.056376
0.242949 -0.054994
0.222215 -0.053427
0.202150 -0.051694
0.182803 -0.049805
0.164221 -0.047773
0.146447 -0.045610
0.129524 -0.043326
0.113495 -0.040929
0.098396 -0.038431
0.084265 -0.035843
0.071136 -0.033170
0.059039 -0.030416
0.048005 -0.027586
0.038060 -0.024685
0.029228 -0.021722
0.021530 -0.018707
0.014984 -0.015649
0.009607 -0.012559
0.005412 -0.009443
0.002408 -0.006308
0.000602 -0.003160
0.000000  0.000000
0.000602  0.003165
0.002408  0.006306
0.005412  0.009416
0.009607  0.012480
0.014984  0.015489
0.021530  0.018441
0.029228  0.021348
0.038060  0.024219
0.048005  0.027062
0.059039  0.029874
0.071136  0.032644
0.084265  0.035360
0.098396  0.038011
0.113495  0.040585
0.129524  0.043071
0.146447  0.045457
0.164221  0.047729
0.182803  0.049874
0.202150  0.051885
0.222215  0.053753
0.242949  0.055470
0.264302  0.057026
0.286222  0.058414
0.308658  0.059629
0.331555  0.060660
0.354858  0.061497
0.378510  0.062133
0.402455  0.062562
0.426635  0.062779
0.450991  0.062774
0.475466  0.062530
0.500000  0.062029
0.524534  0.061254
0.549009  0.060194
0.573365  0.058845
0.597545  0.057218
0.621490  0.055344
0.645142  0.053258
0.668445  0.050993
0.691342  0.048575
0.713778  0.046029
0.735698  0.043377
0.757051  0.040641
0.777785  0.037847
0.797850  0.035017
0.817197  0.032176
0.835779  0.029347
0.853553  0.026554
0.870476  0.023817
0.886505  0.021153
0.901604  0.018580
0.915735  0.016113
0.928864  0.013769
0.940961  0.011562
0.951995  0.009508
0.961940  0.007622
0.970772  0.005915
0.978470  0.004401
0.985016  0.003092
0.990393  0.002001
0.994588  0.001137
0.997592  0.000510
0.999398  0.000128
1.000000  0.000000
```
