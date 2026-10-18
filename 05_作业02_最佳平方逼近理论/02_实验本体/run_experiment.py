"""Independent Gauss-Legendre quadrature checks of the six theoretical answers."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/scicomp-hw-bsa-mpl')
import json,platform
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss,legvander
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent/'results';P.mkdir(exist_ok=True);(P/'figures').mkdir(exist_ok=True)
z,w=leggauss(160);v=(z+1)/2;W=w/2
checks=[]
def ck(name,value):checks.append(dict(name=name,passed=bool(value)))
B=np.column_stack([np.ones(len(v)),v]);G=B.T@(W[:,None]*B);rhs=B.T@(W*v*v);c=np.linalg.solve(G,rhs)
e=np.dot(W,(v*v-B@c)**2)
ck('P2 coefficients',np.allclose(c,[-1/6,1],atol=2e-14,rtol=0));ck('P2 squared error',abs(e-1/180)<1e-14);ck('P2 orthogonality',np.max(abs(B.T@(W*(v*v-B@c))))<1e-14)
L=legvander(z,2);LG=L.T@(w[:,None]*L);a=np.linalg.solve(LG,L.T@(w*z**3));le=np.dot(w,(z**3-L@a)**2)
ck('P4 Legendre coefficients',np.allclose(a,[0,3/5,0],atol=1e-14,rtol=0));ck('P4 squared error',abs(le-8/175)<1e-14);ck('P4 Gram norms',np.allclose(LG,np.diag([2,2/3,2/5]),atol=3e-14,rtol=0))
psi=L/np.sqrt(np.diag(LG));alpha=psi.T@(w*z**3)
ck('P3 orthonormal Gram',np.allclose(psi.T@(w[:,None]*psi),np.eye(3),atol=3e-14,rtol=0));ck('P3 Parseval residual identity',abs(le-(np.dot(w,z**6)-np.dot(alpha,alpha)))<1e-14)
weight=1+v;WG=B.T@((W*weight)[:,None]*B);wc=np.linalg.solve(WG,B.T@(W*weight*v*v));we=np.dot(W*weight,(v*v-B@wc)**2)
ck('P5 positive definite Gram',np.min(np.linalg.eigvalsh(WG))>0);ck('P5 weighted example coefficients',np.allclose(wc,[-5/26,68/65],atol=3e-14,rtol=0));ck('P5 weighted orthogonality',np.max(abs(B.T@(W*weight*(v*v-B@wc))))<1e-14)
M=np.vander(z,3,increasing=True);MG=M.T@(w[:,None]*M);s=np.sin(np.pi*z);mc=np.linalg.solve(MG,M.T@(w*s));se=np.dot(w,(s-M@mc)**2);te=np.dot(w,(s-np.pi*z)**2)
ck('P6 coefficients',np.allclose(mc,[0,3/np.pi,0],atol=2e-14,rtol=0));ck('P6 minimum error',abs(se-(1-6/np.pi**2))<1e-14);ck('P6 Taylor error',abs(te-(2*np.pi**2/3-3))<1e-13);ck('P6 projection orthogonality',np.max(abs(M.T@(w*(s-M@mc))))<2e-14);ck('P6 beats Taylor',se<te)
r=dict(environment=dict(python=platform.python_version(),numpy=np.__version__,matplotlib=matplotlib.__version__,quadrature_nodes=160),P2=dict(gram=G.tolist(),rhs=rhs.tolist(),coefficients=c.tolist(),error=e),P4=dict(coefficients=a.tolist(),error=le),P5=dict(gram=WG.tolist(),coefficients=wc.tolist(),weighted_error=we),P6=dict(gram=MG.tolist(),rhs=(M.T@(w*s)).tolist(),coefficients=mc.tolist(),error=se,taylor_error=te),verification=dict(passed=sum(c['passed'] for c in checks),total=len(checks),checks=checks))
(P/'results.json').write_text(json.dumps(r,indent=2));(P/'verification.json').write_text(json.dumps(r['verification'],indent=2))
np.savetxt(P/'quadrature_nodes_weights.csv',np.column_stack([z,w]),delimiter=',',header='node,weight',comments='')
fig,axes=plt.subplots(1,3,figsize=(11,3.3));x=np.linspace(0,1,401);axes[0].plot(x,x*x,label='x squared');axes[0].plot(x,x-1/6,label='Unweighted projection');axes[0].plot(x,-5/26+68*x/65,'--',label='Weight 1 + x')
x=np.linspace(-1,1,401);axes[1].plot(x,x**3,label='x cubed');axes[1].plot(x,3*x/5,label='Legendre projection');axes[2].plot(x,np.sin(np.pi*x),label='sin(pi x)');axes[2].plot(x,3*x/np.pi,label='Best quadratic');axes[2].plot(x,np.pi*x,'--',label='Taylor degree two')
for ax in axes:ax.set_xlabel('x');ax.grid(alpha=.2);ax.legend(fontsize=7)
fig.tight_layout();fig.savefig(P/'figures/projections.png',dpi=190);fig.savefig(P/'figures/projections.pdf');plt.close(fig)
print(f"{r['verification']['passed']}/{len(checks)} independent quadrature checks passed")
assert all(c['passed'] for c in checks)
