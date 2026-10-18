"""Run all seven Lab 3 tasks. Input data come only from the supplied handout."""
from __future__ import annotations
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/lab3-matplotlib')
import csv, hashlib, io, json, platform, re, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import quad
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / 'results'
DATA = HERE / 'data'
for p in [OUT, DATA, OUT / 'figures']:
    p.mkdir(parents=True, exist_ok=True)


def gaussian_solve(A, b):
    """Gaussian elimination with partial pivoting, written for this lab."""
    A, b = np.array(A, dtype=float, copy=True), np.array(b, dtype=float, copy=True)
    n = len(b)
    for k in range(n):
        p = k + np.argmax(abs(A[k:, k]))
        if abs(A[p, k]) <= np.finfo(float).eps * np.linalg.norm(A, np.inf):
            raise ValueError('Singular matrix')
        A[[k, p]], b[[k, p]] = A[[p, k]], b[[p, k]]
        for i in range(k + 1, n):
            fac = A[i, k] / A[k, k]
            A[i, k:] -= fac * A[k, k:]
            b[i] -= fac * b[k]
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - A[i, i+1:] @ x[i+1:]) / A[i, i]
    return x


def householder_lstsq(A, b):
    """Full-column-rank least squares by explicit Householder reflectors."""
    R, q = np.array(A, dtype=float, copy=True), np.array(b, dtype=float, copy=True)
    m, n = R.shape
    if m < n:
        raise ValueError('Expected an overdetermined system')
    for k in range(n):
        v = R[k:, k].copy()
        alpha = -np.copysign(np.linalg.norm(v), v[0])
        v[0] -= alpha
        norm = np.linalg.norm(v)
        if norm == 0:
            raise ValueError('Rank deficient design')
        v /= norm
        R[k:, k:] -= 2 * np.outer(v, v @ R[k:, k:])
        q[k:] -= 2 * v * (v @ q[k:])
    return gaussian_solve(R[:n], q[:n])


def fit(A, y):
    qr = householder_lstsq(A, y)
    normal = gaussian_solve(A.T @ A, A.T @ y)
    ref, _, rank, s = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ qr
    return dict(coefficients=qr, normal_coefficients=normal, numpy_coefficients=ref,
                residual=r, rss=r @ r, rmse=np.sqrt(np.mean(r*r)),
                max_abs_residual=np.max(abs(r)), normal_orthogonality_inf=np.linalg.norm(A.T @ r, np.inf),
                rank=int(rank), singular_values=s, condition_A=np.linalg.cond(A),
                condition_ATA=np.linalg.cond(A.T @ A),
                qr_numpy_max_difference=np.max(abs(qr-ref)),
                normal_numpy_max_difference=np.max(abs(normal-ref)))


def basis(x):
    x = np.asarray(x)
    return np.column_stack((np.sqrt(x)-x, x*(1-x), x*x*(1-x), x**3*(1-x)))


def save_csv(name, columns, values):
    with (OUT / name).open('w', newline='') as f:
        w=csv.writer(f); w.writerow(columns); w.writerows(values)


def savefig(name):
    plt.tight_layout()
    for ext in ['pdf', 'png']:
        plt.savefig(OUT / 'figures' / f'{name}.{ext}', dpi=180, bbox_inches='tight')
    plt.close()


def main():
    handout = ROOT / '01_指导资料/assignment_text.txt'
    source = handout.read_text()
    coords = np.array([(float(a),float(b)) for a,b in re.findall(r'^([01]\.\d{6})\s+(-?\d\.\d{6})\s*$',source,re.M)])
    pop = np.array([(float(a),float(b)) for a,b in re.findall(r'^(1[789]\d0|20[012]0)\s*\n([\d.]+)\s*$',source,re.M)])
    line = np.array([[25,110],[27,115],[31,155],[33,160],[35,180]],float)
    assert coords.shape == (129, 2) and pop.shape == (24,2) and line.shape == (5,2)
    for name, arr, header in [('rae2822.csv',coords,'x,y'),('population.csv',pop,'year,population_million'),('linear_points.csv',line,'x,y')]:
        np.savetxt(DATA / name, arr, delimiter=',', header=header, comments='', fmt='%.9g')
    result = dict(metadata=dict(generated_utc=datetime.now(timezone.utc).isoformat(), python=sys.version,
                               numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__,
                               platform=platform.platform(),source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'01_指导资料').glob('*.pdf'))}),cases={})
    cases=result['cases']
    b=np.array([-1.,4.,2.,1.])
    for key, row in [('literal',[1,3,0]),('alternative',[1,1,2])]:
        A=np.array([[1,2,4],[2,1,1],row,[1,-1,-2.]],float)
        cases['1.1_'+key]=dict(A=A,b=b,ATA=A.T@A,ATb=A.T@b,**fit(A,b))
    x,y=line.T
    cases['1.2']=dict(x=x,y=y,**fit(np.column_stack((np.ones(5),x)),y))
    c=cases['1.2']['coefficients']
    save_csv('linear_fit.csv',['x','y','fitted','residual'],zip(x,y,c[0]+c[1]*x,y-c[0]-c[1]*x))
    plt.figure(figsize=(7,3.6)); plt.scatter(x,y,label='Data'); grid=np.linspace(24,36,201)
    plt.plot(grid,c[0]+c[1]*grid,label='Least-squares line',color='tab:orange')
    plt.xlabel('x');plt.ylabel('y');plt.legend();plt.grid(alpha=.2);savefig('linear_fit')
    years,population=pop.T
    t=years-1790; u=t/100; z=np.log(population)
    pop_cases={}
    for name,degree in [('exponential',1),('variable_rate',2)]:
        D=np.vander(u,degree+1,increasing=True)
        info=fit(D,z); c=info['coefficients']; prediction=np.exp(D@c)
        params=dict(x0=np.exp(c[0]),r_per_year=c[1]/100) if degree==1 else dict(x0=np.exp(c[0]),r0_per_year=c[1]/100,r1_per_year_squared=-2*c[2]/10000)
        raw_design=np.vander(t,degree+1,increasing=True)
        info.update(parameters=params,prediction=prediction,population_rss=np.sum((population-prediction)**2),
                    population_rmse=np.sqrt(np.mean((population-prediction)**2)), population_max_abs_error=np.max(abs(population-prediction)),
                    unscaled_condition_A=np.linalg.cond(raw_design),unscaled_condition_ATA=np.linalg.cond(raw_design.T@raw_design))
        pop_cases[name]=info
    cases['1.3']=dict(year=years,t_years=t,u_centuries=u,population=population,models=pop_cases)
    save_csv('population_fits.csv',['year','observed_million','exponential_million','variable_rate_million','log_residual_exponential','log_residual_variable_rate'],
             zip(years,population,pop_cases['exponential']['prediction'],pop_cases['variable_rate']['prediction'],pop_cases['exponential']['residual'],pop_cases['variable_rate']['residual']))
    fig,axes=plt.subplots(1,2,figsize=(10,3.8));grid=np.linspace(0,2.3,400)
    for ax in axes:
        ax.scatter(years,population,color='black',s=13,label='Handout data')
        for name,degree in [('exponential',1),('variable_rate',2)]:
            ax.plot(1790+grid*100,np.exp(np.vander(grid,degree+1,increasing=True)@pop_cases[name]['coefficients']),label=name.replace('_',' '))
        ax.set_xlabel('Year');ax.grid(alpha=.2)
    axes[0].set_ylabel('Population (million)');axes[1].set_yscale('log');axes[1].set_ylabel('Population (million, log scale)');axes[0].legend(fontsize=8);savefig('population_models')
    plt.figure(figsize=(7,3.4))
    for name in pop_cases:plt.plot(years,pop_cases[name]['residual'],'o-',label=name.replace('_',' '))
    plt.axhline(0,color='gray',lw=.8);plt.xlabel('Year');plt.ylabel('log(observed) - log(fitted)');plt.legend();plt.grid(alpha=.2);savefig('population_log_residuals')
    G=np.array([[1,1/2],[1/2,1/3]]);h=np.array([1/3,1/4]);c=gaussian_solve(G,h)
    error,quaderr=quad(lambda v:(v*v-c[0]-c[1]*v)**2,0,1,epsabs=1e-13)
    cases['2.1']=dict(gram=G,rhs=h,coefficients=c,squared_error=error,quadrature_error_estimate=quaderr,
                     orthogonality=[quad(lambda v,k=k:(v*v-c[0]-c[1]*v)*v**k,0,1)[0] for k in range(2)])
    P=[lambda v:1.,lambda v:v,lambda v:(3*v*v-1)/2]
    gram=np.array([[quad(lambda v,i=i,j=j:P[i](v)*P[j](v),-1,1)[0] for j in range(3)] for i in range(3)])
    inner=np.array([quad(lambda v,j=j:v**3*P[j](v),-1,1)[0] for j in range(3)])
    a=inner/np.diag(gram)
    cases['2.2']=dict(gram=gram,inner_products=inner,legendre_coefficients=a,monomial_coefficients=[a[0]-a[2]/2,a[1],3*a[2]/2],
                     squared_error=quad(lambda v:(v**3-sum(a[j]*P[j](v) for j in range(3)))**2,-1,1)[0])
    gram=np.array([[0 if (i+j)%2 else 2/(i+j+1) for j in range(3)] for i in range(3)])
    h=np.array([quad(lambda v,k=k:np.sin(np.pi*v)*v**k,-1,1)[0] for k in range(3)])
    c=gaussian_solve(gram,h)
    cases['2.3']=dict(gram=gram,rhs=h,coefficients=c,squared_error=quad(lambda v:(np.sin(np.pi*v)-sum(c[k]*v**k for k in range(3)))**2,-1,1)[0],
                     taylor_squared_error=quad(lambda v:(np.sin(np.pi*v)-np.pi*v)**2,-1,1)[0])
    fig,axes=plt.subplots(1,3,figsize=(12,3.3))
    v=np.linspace(0,1,301);axes[0].plot(v,v*v,label='x squared');axes[0].plot(v,v-1/6,label='x - 1/6')
    v=np.linspace(-1,1,301);axes[1].plot(v,v**3,label='x cubed');axes[1].plot(v,.6*v,label='3x/5')
    axes[2].plot(v,np.sin(np.pi*v),label='sin(pi x)');axes[2].plot(v,3*v/np.pi,label='3x/pi');axes[2].plot(v,np.pi*v,'--',label='Taylor: pi x')
    for ax in axes:ax.set_xlabel('x');ax.legend(fontsize=8);ax.grid(alpha=.2)
    savefig('continuous_approximations')
    split=int(np.argmin(coords[:,0])); lower=coords[:split+1][::-1];upper=coords[split:]
    surfaces={}
    for name,points in [('upper',upper),('lower',lower)]:
        v,w=points.T;B=basis(v);info=fit(B,w)
        info.update(x=v,y=w,fitted=B@info['coefficients'],count=len(v))
        surfaces[name]=info
        save_csv(f'airfoil_{name}.csv',['x','observed_y','fitted_y','residual'],zip(v,w,info['fitted'],info['residual']))
    cases['3.1']=dict(total_input_points=len(coords),leading_edge_index=split,basis_count=4,surfaces=surfaces)
    fig,axes=plt.subplots(2,1,figsize=(8,5.6),gridspec_kw={'height_ratios':[2,1]})
    v=np.linspace(0,1,501)
    for name,info in surfaces.items():
        axes[0].plot(info['x'],info['y'],'o',ms=3,label=name+' data');axes[0].plot(v,basis(v)@info['coefficients'],label=name+' fit')
        axes[1].plot(info['x'],info['residual'],'.-',label=name)
    axes[0].set_aspect('equal',adjustable='box');axes[0].set_ylabel('y / chord');axes[0].legend(ncol=2,fontsize=8)
    axes[1].axhline(0,color='gray',lw=.8);axes[1].set_ylabel('Data - fit');axes[1].set_xlabel('x / chord');axes[1].legend(fontsize=8)
    for ax in axes:ax.grid(alpha=.2)
    savefig('airfoil_fit')
    def encode(v):
        if isinstance(v,np.ndarray):return v.tolist()
        if isinstance(v,np.generic):return v.item()
        raise TypeError(type(v).__name__)
    (OUT/'results.json').write_text(json.dumps(result,indent=2,default=encode)+'\n')
    print('Completed: 1.1 (two readings), 1.2, 1.3, 2.1, 2.2, 2.3, 3.1.')
    for name,info in cases.items():
        if 'coefficients' in info:print(name,info['coefficients'],'RSS/error',info.get('rss',info.get('squared_error')))
    for name,info in pop_cases.items(): print('Population',name,info['parameters'],'log RSS',info['rss'],'population RSS',info['population_rss'])
    for name,info in surfaces.items():print('Airfoil',name,info['coefficients'],'RSS',info['rss'])

if __name__=='__main__':main()
