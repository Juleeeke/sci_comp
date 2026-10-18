#!/usr/bin/env python3
"""Reproduce SVD Homework Problems 12/13 and verify numerical examples."""
from pathlib import Path
import csv, hashlib, json, platform, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import PIL

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
SEED = 20261009
checks = {}

def check(name, condition):
    checks[name] = bool(condition)
    if not condition:
        raise AssertionError(name)

def write_csv(name, rows):
    with (OUT / name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def save_plot(name):
    plt.savefig(OUT / name, dpi=180, bbox_inches='tight')
    plt.close()

# Problem 12: luminance of the archived NASA astronaut photograph.
rgb = np.asarray(Image.open(ROOT / 'data/astronaut.png'), dtype=float) / 255
A = rgb @ np.array([0.2126, 0.7152, 0.0722])
m, n = A.shape
np.save(ROOT / 'data/grayscale.npy', A)
Image.fromarray(np.rint(A * 255).astype('uint8')).save(
    ROOT / 'data/grayscale_preview.png')
U, s, Vt = np.linalg.svd(A, full_matrices=False)
image_rows = []
ranks = [5, 10, 20, 50, 100]
fig, axes = plt.subplots(2, 3, figsize=(10, 6.7))
axes.flat[0].imshow(A, cmap='gray', vmin=0, vmax=1)
axes.flat[0].set_title('Original (512 x 512)')
for ax, k in zip(list(axes.flat)[1:], ranks):
    Ak = (U[:, :k] * s[:k]) @ Vt[:k]
    error = np.linalg.norm(A - Ak, 'fro') / np.linalg.norm(A, 'fro')
    tail = np.linalg.norm(s[k:]) / np.linalg.norm(s)
    rho = k * (m + n + 1) / (m * n)
    check(f'image_tail_identity_k{k}', np.isclose(error, tail, rtol=1e-11))
    image_rows.append(dict(k=k, relative_error=float(error),
                           storage_fraction=float(rho),
                           retained_energy=float(1 - error**2),
                           factor_scalars=k * (m + n + 1)))
    np.save(OUT / f'image_rank_{k}.npy', Ak)
    ax.imshow(np.clip(Ak, 0, 1), cmap='gray', vmin=0, vmax=1)
    ax.set_title(f'k = {k}; E = {error:.4f}')
for ax in axes.flat:
    ax.axis('off')
fig.tight_layout()
save_plot('image_reconstructions.png')
plt.figure(figsize=(8, 3.6))
plt.semilogy(np.arange(1, len(s) + 1), s)
plt.xlabel('Singular value index'); plt.ylabel('Singular value (log scale)')
plt.title('Problem 12: grayscale singular value spectrum')
plt.grid(alpha=.25); save_plot('image_spectrum.png')
write_csv('image_metrics.csv', image_rows)
write_csv('image_singular_values.csv',
          [dict(index=i + 1, singular_value=float(v)) for i, v in enumerate(s)])
check('image_full_reconstruction', np.allclose((U * s) @ Vt, A, atol=1e-12))
check('image_error_monotone', np.all(np.diff([r['relative_error'] for r in image_rows]) < 0))

# Problem 13: rank-five signal with independent Gaussian noise.
rng = np.random.default_rng(SEED)
P = rng.standard_normal((100, 5))
Q = rng.standard_normal((80, 5))
N = rng.standard_normal((100, 80))
epsilon = 0.05
B = P @ Q.T
C = epsilon * N
M = B + C
Um, sm, Vtm = np.linalg.svd(M, full_matrices=False)
data_rows = []
for k in range(1, 21):
    Mk = (Um[:, :k] * sm[:k]) @ Vtm[:k]
    error = np.linalg.norm(M - Mk, 'fro') / np.linalg.norm(M, 'fro')
    tail = np.linalg.norm(sm[k:]) / np.linalg.norm(sm)
    check(f'data_tail_identity_k{k}', np.isclose(error, tail, rtol=1e-11))
    data_rows.append(dict(k=k, relative_error=float(error),
                          error_to_clean_B=float(np.linalg.norm(B - Mk, 'fro') /
                                                 np.linalg.norm(B, 'fro'))))
write_csv('data_errors.csv', data_rows)
write_csv('data_singular_values.csv',
          [dict(index=i + 1, singular_value=float(v)) for i, v in enumerate(sm)])
np.savez_compressed(OUT / 'data_matrix.npz', P=P, Q=Q, N=N, B=B,
                    C=C, A=M, U=Um, s=sm, Vt=Vtm)
plt.figure(figsize=(8, 3.6))
plt.semilogy(np.arange(1, 81), sm, 'o-', markersize=3)
plt.axvline(5.5, color='crimson', linestyle='--', label='Signal/noise boundary')
plt.xlabel('Singular value index'); plt.ylabel('Singular value (log scale)')
plt.title('Problem 13: five dominant modes and a noise tail')
plt.legend(); plt.grid(alpha=.25); save_plot('data_spectrum.png')
plt.figure(figsize=(8, 3.6))
plt.semilogy(range(1, 21), [r['relative_error'] for r in data_rows], 'o-')
plt.axvline(5, color='crimson', linestyle='--', label='k = 5')
plt.xlabel('Retained rank k'); plt.ylabel('Relative Frobenius error (log scale)')
plt.xticks(range(1, 21)); plt.legend(); plt.grid(alpha=.25)
plt.title('Problem 13: approximation error against the noisy matrix A')
save_plot('data_error.png')
check('clean_matrix_rank5', np.linalg.matrix_rank(B) == 5)
check('noisy_matrix_rank80', np.linalg.matrix_rank(M) == 80)
check('data_error_monotone', np.all(np.diff([r['relative_error'] for r in data_rows]) < 0))
check('noise_construction', np.allclose(M - B, epsilon * N))
check('weyl_noise_bound', abs(sm[4] - np.linalg.svd(B, compute_uv=False)[4]) <= np.linalg.norm(C, 2))

# Direct independent checks for Problems 3, 6, 7, 8 and the complex challenge.
A3 = np.array([[3., 0], [0, 2], [0, 0]])
check('problem3_singular_values', np.allclose(np.linalg.svd(A3, compute_uv=False), [3, 2]))
A6 = np.array([[1., 0], [0, 2], [0, 0]])
Ap = np.array([[1., 0, 0], [0, .5, 0]])
check('problem6_four_conditions', all([
    np.allclose(A6 @ Ap @ A6, A6), np.allclose(Ap @ A6 @ Ap, Ap),
    np.allclose((A6 @ Ap).T, A6 @ Ap), np.allclose((Ap @ A6).T, Ap @ A6)]))
A7 = np.array([[1., 0], [1, 1], [1, 2]])
b7 = np.array([1., 2, 2]); x7 = np.array([7 / 6, .5])
check('problem7_lstsq', np.allclose(np.linalg.lstsq(A7, b7, rcond=None)[0], x7))
check('problem7_residual_orthogonality', np.allclose(A7.T @ (b7 - A7 @ x7), 0))
A8 = np.array([[1., 1], [2, 2], [3, 3]])
b8 = np.array([1., 2, 4]); x8 = np.array([17 / 28, 17 / 28])
check('problem8_minimum_norm', np.allclose(np.linalg.pinv(A8) @ b8, x8))
Z = rng.standard_normal((7, 4)) + 1j * rng.standard_normal((7, 4))
Uz, sz, Vhz = np.linalg.svd(Z, full_matrices=False)
check('complex_svd_reconstruction', np.allclose((Uz * sz) @ Vhz, Z))
check('complex_adjoint_singular_values', np.allclose(sz, np.linalg.svd(Z.conj().T, compute_uv=False)))

summary = dict(seed=SEED, epsilon=epsilon, image_shape=[m, n],
               image_source='Archived NASA astronaut RGB image; weighted luminance',
               image_break_even=m * n / (m + n + 1), image_rows=image_rows,
               data_rows=data_rows, data_leading_singular_values=sm[:10].tolist(),
               clean_singular_values=np.linalg.svd(B, compute_uv=False)[:5].tolist(),
               noise_relative_frobenius=float(np.linalg.norm(C, 'fro') / np.linalg.norm(B, 'fro')),
               noise_spectral_norm=float(np.linalg.norm(C, 2)),
               noisy_rank=int(np.linalg.matrix_rank(M)), clean_rank=int(np.linalg.matrix_rank(B)),
               environment=dict(python=platform.python_version(), numpy=np.__version__,
                                matplotlib=matplotlib.__version__, pillow=PIL.__version__,
                                platform=platform.platform()),
               checks_passed=sum(checks.values()), checks_total=len(checks))
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2))
(OUT / 'verification.json').write_text(json.dumps(checks, indent=2))
(OUT / 'input_sha256.json').write_text(json.dumps({
    'astronaut.png': hashlib.sha256((ROOT / 'data/astronaut.png').read_bytes()).hexdigest()}, indent=2))
print(json.dumps(summary, indent=2))
