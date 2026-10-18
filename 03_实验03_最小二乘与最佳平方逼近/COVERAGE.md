# Requirement coverage

| Supplied handout requirement | Report section and evidence |
|---|---|
| 1.1 normal equations solution residual and RSS | Section 2, literal row (1,3,0); separately labeled possible correction |
| 1.2 fitted line and RSS | Section 3, exact rational coefficients and all point residuals |
| 1.3 both growth models and graphical comparison | Section 4; 24 rows in population_fits.csv |
| 2.1 functional normal equations coefficients squared error | Section 5; all four subquestions |
| 2.2 Legendre form three coefficients final polynomial | Section 6; all three subquestions plus error check |
| 2.3 Gram system symmetry coefficients parity and Taylor comparison | Section 7; all five subquestions |
| 3.1 upper and lower airfoil fits and graphical comparison | Section 8; two sets of 65 points including shared leading edge |
| Python library comparison and numerical behavior | Section 9; explicit QR normal equations and NumPy references |

All 129 coordinates and 24 population observations are checked directly against the current PDF. The source equation x1+x2+2x2=2 is not silently corrected. Log space fitting and population space diagnostic errors are kept separate.
