"""Independent numerical and source-data checks; exits nonzero on a failure."""
import hashlib, json, re
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.linalg import lstsq
import pymupdf

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
out=HERE/'results'
r=json.loads((out/'results.json').read_text()); c=r['cases'];checks=[]

def check(name,condition,detail=''):
    checks.append(dict(name=name,passed=bool(condition),detail=detail))

def exact_solve(A,b):
    m=[[F(v) for v in row]+[F(w)] for row,w in zip(A,b)]
    for k in range(len(m)):
        p=next(i for i in range(k,len(m)) if m[i][k])
        m[k],m[p]=m[p],m[k]
        v=m[k][k];m[k]=[a/v for a in m[k]]
        for i in range(len(m)):
            if i!=k:
                v=m[i][k];m[i]=[a-v*b for a,b in zip(m[i],m[k])]
    return [row[-1] for row in m]

check('All assigned tasks present',set(c)=={'1.1_literal','1.1_alternative','1.2','1.3','2.1','2.2','2.3','3.1'})
check('Original source hashes unchanged',all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha for name,sha in r['metadata']['source_sha256'].items()))
pdf='\n'.join(p.get_text() for p in pymupdf.open(ROOT/'2-2-DLSM-BSA--Application--lab.pdf'))
coords=np.loadtxt(HERE/'data/rae2822.csv',delimiter=',',skiprows=1)
pdf_coords=np.array([(float(a),float(b)) for a,b in re.findall(r'^([01]\.\d{6})\s+(-?\d\.\d{6})\s*$',pdf,re.M)])
check('All 129 coordinates match source PDF',pdf_coords.shape==coords.shape and np.array_equal(pdf_coords,coords),f'{len(pdf_coords)} source points')
pop=np.loadtxt(HERE/'data/population.csv',delimiter=',',skiprows=1)
pdf_pop=np.array([(float(a),float(b)) for a,b in re.findall(r'^(1[789]\d0|20[012]0)\s*\n([\d.]+)\s*$',pdf,re.M)])
check('All 24 population rows match source PDF',pdf_pop.shape==pop.shape and np.array_equal(pdf_pop,pop),f'{len(pdf_pop)} source rows')
for key,row in [('literal',[1,3,0]),('alternative',[1,1,2])]:
    info=c['1.1_'+key];A=np.array([[1,2,4],[2,1,1],row,[1,-1,-2]]); b=np.array([-1,4,2,1]);xx=exact_solve((A.T@A).tolist(),(A.T@b).tolist())
    x=np.array(info['coefficients']);res=b-A@x
    check(f'1.1 {key}: exact rational solution',np.allclose(x,[float(v) for v in xx],rtol=0,atol=1e-12),str(xx))
    check(f'1.1 {key}: normal equations and residual',np.array_equal(info['ATA'],A.T@A) and np.array_equal(info['ATb'],A.T@b) and np.allclose(info['residual'],res) and abs(info['rss']-res@res)<1e-12 and np.linalg.norm(A.T@res)<1e-12)
info=c['1.2'];x=np.array([25,27,31,33,35]);y=np.array([110,115,155,160,180]);B=np.column_stack([np.ones(5),x]);fr=exact_solve((B.T@B).astype(int).tolist(),(B.T@y).astype(int).tolist())
check('1.2: independent exact coefficients',np.allclose(info['coefficients'],[float(v) for v in fr],atol=1e-11,rtol=0),str(fr))
check('1.2: reference polynomial fit and RSS',np.allclose(info['coefficients'],np.polynomial.polynomial.polyfit(x,y,1)) and np.isclose(info['rss'],np.sum((y-B@info['coefficients'])**2)))
for name,deg in [('exponential',1),('variable_rate',2)]:
    info=c['1.3']['models'][name];u=(pop[:,0]-1790)/100;B=np.vander(u,deg+1,increasing=True);z=np.log(pop[:,1]);ref=lstsq(B,z,lapack_driver='gelsy')[0];p=np.exp(B@ref)
    check('1.3 '+name+': independent LAPACK QR reference',np.allclose(ref,info['coefficients'],rtol=0,atol=1e-12))
    check('1.3 '+name+': both objectives recomputed',np.isclose(np.sum((z-B@ref)**2),info['rss']) and np.isclose(np.sum((pop[:,1]-p)**2),info['population_rss']) and np.allclose(p,info['prediction']))
    par=info['parameters'];t=pop[:,0]-1790
    physical=par['x0']*np.exp(par['r_per_year']*t) if deg==1 else par['x0']*np.exp(par['r0_per_year']*t-par['r1_per_year_squared']*t*t/2)
    check('1.3 '+name+': parameter units and transformation',np.allclose(p,physical,rtol=1e-12))
check('1.3: nested quadratic reduces log RSS',c['1.3']['models']['variable_rate']['rss']<c['1.3']['models']['exponential']['rss'])
# A separate 160-node Gauss-Legendre rule checks the continuous projections.
z,w=leggauss(160);v=(z+1)/2
check('2.1: coefficients and exact squared error',np.allclose(c['2.1']['coefficients'],[-1/6,1],rtol=0,atol=1e-14) and abs(c['2.1']['squared_error']-1/180)<1e-14 and abs(np.dot(w/2,(v*v-v+1/6)**2)-1/180)<1e-14)
check('2.1: projection residual orthogonal',np.max(abs(np.array(c['2.1']['orthogonality'])))<1e-14)
P=np.polynomial.legendre.legvander(z,2)
check('2.2: Legendre orthogonality and norms',np.allclose(P.T@(w[:,None]*P),np.diag([2,2/3,2/5]),rtol=0,atol=3e-14))
check('2.2: projection and exact squared error',np.allclose(c['2.2']['legendre_coefficients'],[0,.6,0],atol=1e-14) and abs(c['2.2']['squared_error']-8/175)<1e-14 and abs(np.dot(w,(z**3-.6*z)**2)-8/175)<1e-14)
check('2.2: residual orthogonal to full basis',np.max(abs(P.T@(w*(z**3-.6*z))))<1e-14)
check('2.3: symmetry and exact coefficients',np.allclose(c['2.3']['coefficients'],[0,3/np.pi,0],atol=1e-14))
check('2.3: exact minimum error and Taylor error',abs(c['2.3']['squared_error']-(1-6/np.pi**2))<1e-14 and abs(c['2.3']['taylor_squared_error']-(2*np.pi**2/3-3))<1e-14)
check('2.3: independent quadrature and orthogonality',abs(np.dot(w,(np.sin(np.pi*z)-3*z/np.pi)**2)-c['2.3']['squared_error'])<1e-13 and np.max(abs(np.vander(z,3,increasing=True).T@(w*(np.sin(np.pi*z)-3*z/np.pi))))<3e-14)
check('2.3: L2 error less than degree-two Taylor error',c['2.3']['squared_error']<c['2.3']['taylor_squared_error'])
for name,expected in [('lower',coords[:65][::-1]),('upper',coords[64:])]:
    info=c['3.1']['surfaces'][name];x=np.array(info['x']);y=np.array(info['y']);B=np.column_stack([np.sqrt(x)-x,x*(1-x),x*x*(1-x),x**3*(1-x)]);a=np.array(info['coefficients']);ref=lstsq(B,y,lapack_driver='gelsd')[0]
    check('3.1 '+name+': correct geometric split',len(x)==65 and np.array_equal(np.column_stack([x,y]),expected) and np.all(np.diff(x)>0))
    check('3.1 '+name+': SVD reference and full rank',np.allclose(a,ref,rtol=0,atol=1e-12) and np.linalg.matrix_rank(B)==4)
    check('3.1 '+name+': residual metrics and orthogonality',np.allclose(info['residual'],y-B@a) and np.isclose(info['rss'],np.sum((y-B@a)**2)) and np.max(abs(B.T@(y-B@a)))<1e-13)
    check('3.1 '+name+': closure enforced by basis',np.array_equal(B[[0,-1]],np.zeros((2,4))) and np.max(abs(np.array(info['fitted'])[[0,-1]]))==0)
    saved=np.loadtxt(out/f'airfoil_{name}.csv',delimiter=',',skiprows=1)
    check('3.1 '+name+': CSV agrees with results',np.allclose(saved,np.column_stack([x,y,B@a,y-B@a]),rtol=0,atol=1e-16))
fits=[c['1.1_literal'],c['1.1_alternative'],c['1.2'],*c['1.3']['models'].values(),*c['3.1']['surfaces'].values()]
check('All explicit QR solutions agree with NumPy',all(v['qr_numpy_max_difference']<1e-10 for v in fits))
check('All explicit normal-equation solutions agree with NumPy',all(v['normal_numpy_max_difference']<1e-9 for v in fits))
result=dict(passed=sum(v['passed'] for v in checks),total=len(checks),checks=checks)
(out/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(f"{result['passed']}/{result['total']} checks passed")
for v in checks:
    if not v['passed']:print('FAIL',v['name'],v['detail'])
raise SystemExit(0 if result['passed']==result['total'] else 1)
