"""Generate a standalone English LaTeX report, with all plots embedded as vectors."""
import json, math
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
OUT=HERE/'results'
R=json.loads((OUT/'results.json').read_text()); C=R['cases']
REPORT=HERE.parent/'report';REPORT.mkdir(exist_ok=True)


def n(v,d=8):return f'{v:.{d}g}'
def mat(a):
    return r'\begin{bmatrix}'+r'\\'.join(' & '.join(n(float(v)) for v in row) for row in np.atleast_2d(a))+r'\end{bmatrix}'
def col(a):return mat(np.array(a).reshape(-1,1))
def sci(v):
    if not v:return '$0$'
    a,b=f'{v:.3e}'.split('e');return rf'${a}\times10^{{{int(b)}}}$'

# series items: (label, x, y, color, dots); all axes supplied explicitly.
def plot(series,xlim,ylim,xticks,yticks,xlabel,ylabel,width=160,height=72):
    L,B,RR,T=18,12,width-4,height-14
    xp=lambda x:L+(x-xlim[0])/(xlim[1]-xlim[0])*(RR-L)
    yp=lambda y:B+(y-ylim[0])/(ylim[1]-ylim[0])*(T-B)
    lines=[rf'{{\setlength{{\unitlength}}{{1mm}}\begin{{picture}}({width},{height})',
           rf'\put({L},{height-3}){{\makebox({RR-L},3)[l]{{\scriptsize {ylabel}}}}}']
    for v,label in yticks:
        Y=yp(v)
        lines.extend([r'{\color{gridgray}\linethickness{.25pt}' + rf'\put({L},{Y:.3f}){{\line(1,0){{{RR-L}}}}}' + '}',
                      rf'\put(0,{Y-1.5:.3f}){{\makebox({L-2},3)[r]{{\scriptsize {label}}}}}'])
    for v,label in xticks:
        X=xp(v)
        lines.extend([rf'\put({X:.3f},{B-1}){{\line(0,1){{1}}}}',rf'\put({X-8:.3f},{B-5}){{\makebox(16,3){{\scriptsize {label}}}}}'])
    lines.extend([rf'\put({L},{B}){{\line(1,0){{{RR-L}}}}}',rf'\put({L},{B}){{\line(0,1){{{T-B}}}}}',
                  rf'\put({L},0){{\makebox({RR-L},4){{\scriptsize {xlabel}}}}}'])
    for label,x,y,color,dots in series:
        pts=list(zip(map(xp,x),map(yp,y)))
        lines.append(r'{\color{'+color+r'}\linethickness{.65pt}')
        if dots:
            for X,Y in pts:lines.append(rf'\put({X:.3f},{Y:.3f}){{\circle*{{.8}}}}')
        else:
            for (x1,y1),(x2,y2) in zip(pts,pts[1:]):
                lines.append(rf'\Line({x1:.3f},{y1:.3f})({x2:.3f},{y2:.3f})')
        lines.append('}')
    legend=r'\quad '.join(r'{\color{'+color+'}'+(r'\textbullet\ ' if dots else r'\rule[.5ex]{2.5mm}{.5pt}\ ')+label+'}' for label,_,_,color,dots in series if label)
    lines.append(rf'\put({L},{height-9}){{\makebox({RR-L},3)[l]{{\scriptsize {legend}}}}}')
    lines.append(r'\end{picture}}')
    return '\n'.join(lines)


def figure(body,caption):return '\n'+r'\begin{figure}[ht]\centering'+'\n'+body+'\n'+r'\caption{'+caption+r'}\end{figure}'+'\n'

v={}
for key in ['1.1_literal','1.1_alternative']:
    k='L' if key.endswith('literal') else 'A'; q=C[key]
    v[k+'_GRAM']=mat(q['ATA']);v[k+'_RHS']=col(q['ATb']);v[k+'_X']=col(q['coefficients']);v[k+'_R']=col(q['residual']);v[k+'_RSS']=n(q['rss'],10)
q=C['1.2'];a,b=q['coefficients'];x=np.array(q['x']);y=np.array(q['y']);g=np.linspace(24,36,161)
v['LINE_RSS']=n(q['rss'],11);v['LINE_TABLE']='\n'.join(f'{xx:g} & {yy:g} & {a+b*xx:.6f} & {yy-a-b*xx:.6f} '+r'\\' for xx,yy in zip(x,y))
v['LINE_PLOT']=figure(plot([('Data',x,y,'black',True),('Least-squares fit',g,a+b*g,'bluefit',False)],(24,36),(95,190),[(z,str(z)) for z in [24,27,30,33,36]],[(z,str(z)) for z in [100,120,140,160,180]],'$x$','$y$'), 'The line minimizes the sum of squared vertical residuals for the five supplied points.')
pop=C['1.3'];models=pop['models'];pe=models['exponential'];pv=models['variable_rate']
v['POP_ROWS']='\n'.join(f'{int(year)} & {p:g} & {pe["prediction"][i]:.3f} & {pv["prediction"][i]:.3f} '+r'\\' for i,(year,p) in enumerate(zip(pop['year'],pop['population'])))
v['POP_METRICS']='\n'.join(f'{label} & {q["rss"]:.8f} & {q["population_rss"]:.4f} & {q["population_rmse"]:.4f} & {q["population_max_abs_error"]:.4f} '+r'\\' for label,q in [('Constant rate',pe),('Variable rate',pv)])
v['POP_EXP']=rf'{pe["parameters"]["x0"]:.10f}\exp({pe["parameters"]["r_per_year"]:.11f}t)'
v['POP_VAR']=rf'{pv["parameters"]["x0"]:.10f}\exp({pv["parameters"]["r0_per_year"]:.11f}t-{pv["parameters"]["r1_per_year_squared"]/2:.12f}t^2)'
v['R1']=n(pv['parameters']['r1_per_year_squared'],11)
v['LOG_REDUCTION']=f'{100*(1-pv["rss"]/pe["rss"]):.2f}'
years=np.array(pop['year']);g=np.linspace(1790,2020,241);u=(g-1790)/100
curves=[('Observed',years,np.array(pop['population']),'black',True)]
for label,degree,q,color in [('Constant rate',1,pe,'orangefit'),('Variable rate',2,pv,'bluefit')]:
    curves.append((label,g,np.exp(np.vander(u,degree+1,increasing=True)@q['coefficients']),color,False))
v['POP_PLOT']=figure(plot(curves,(1790,2020),(0,550),[(z,str(z)) for z in [1790,1840,1890,1940,1990,2020]],[(z,str(z)) for z in [0,100,200,300,400,500]],'Year','Population (million)',height=78),'Comparison over the supplied years only. The constant-rate fit overestimates the most recent observations.')
v['POP_RESIDUAL_PLOT']=figure(plot([(label,years,q['residual'],color,False) for label,q,color in [('Constant rate',pe,'orangefit'),('Variable rate',pv,'bluefit')]],(1790,2020),(-.6,.4),[(z,str(z)) for z in [1790,1840,1890,1940,1990,2020]],[(z,str(z)) for z in [-.6,-.4,-.2,0,.2,.4]],'Year',r'$\ln P_{\mathrm{obs}}-\ln P_{\mathrm{fit}}$',height=67),'Log-space residuals. The extra quadratic term removes most of the broad curvature, but a small structured discrepancy remains.')
g=np.linspace(0,1,161)
v['SQUARE_PLOT']=figure(plot([('$x^2$',g,g*g,'black',False),('$x-1/6$',g,g-1/6,'bluefit',False)],(0,1),(-.2,1.05),[(z,str(z)) for z in [0,.25,.5,.75,1]],[(z,str(z)) for z in [0,.25,.5,.75,1]],'$x$','Function and projection',height=58),'The continuous best line need not interpolate the endpoint values.')
g=np.linspace(-1,1,201)
v['SINE_PLOT']=figure(plot([(r'$\sin(\pi x)$',g,np.sin(np.pi*g),'black',False),(r'$3x/\pi$',g,3*g/np.pi,'bluefit',False),(r'$\pi x$',g,np.pi*g,'orangefit',False)],(-1,1),(-3.3,3.3),[(z,str(z)) for z in [-1,-.5,0,.5,1]],[(z,str(z)) for z in [-3,-2,-1,0,1,2,3]],'$x$','Function, best approximation and Taylor polynomial',height=76),'The Taylor polynomial is accurate locally near zero. The projection minimizes the integrated squared error over the whole interval.')
v['TAYLOR_ERROR']=n(C['2.3']['taylor_squared_error'],10);v['SINE_ERROR']=n(C['2.3']['squared_error'],10)
sur=C['3.1']['surfaces'];v['AIR_COEFFS']='\n'.join(f'{i+1} & {sur["upper"]["coefficients"][i]:.10f} & {sur["lower"]["coefficients"][i]:.10f} '+r'\\' for i in range(4))
v['AIR_METRICS']='\n'.join(f'{name.capitalize()} & {q["count"]} & {sci(q["rss"])} & {sci(q["rmse"])} & {sci(q["max_abs_residual"])} '+r'\\' for name,q in sur.items())
from run_experiment import basis
g=np.linspace(0,1,241);series=[]
for name,color in [('upper','bluefit'),('lower','orangefit')]:
    q=sur[name];series.extend([(name.capitalize()+' data',q['x'],q['y'],color,True),(name.capitalize()+' fit',g,basis(g)@q['coefficients'],color,False)])
v['AIR_PLOT']=figure(plot(series,(0,1),(-.071,.071),[(z,str(z)) for z in [0,.2,.4,.6,.8,1]],[(z,str(z)) for z in [-.06,-.03,0,.03,.06]],'$x$/chord','$y$/chord (vertical scale enlarged)',height=58),'All supplied coordinates and the two fitted curves. The vertical axis is enlarged to show fit quality; this panel is not an equal-scale geometry drawing.')
v['AIR_RES_PLOT']=figure(plot([(name.capitalize(),q['x'],q['residual'],color,False) for (name,q),color in zip(sur.items(),['bluefit','orangefit'])],(0,1),(-.0013,.0013),[(z,str(z)) for z in [0,.2,.4,.6,.8,1]],[(z,str(z)) for z in [-.001,0,.001]],'$x$/chord','Residual: data minus fitted ordinate',height=48),'Signed residuals reveal the larger mismatch on the lower surface. Units are fractions of chord length.')
labels=[('1.1 literal',C['1.1_literal']),('1.1 alternative',C['1.1_alternative']),('1.2 line',C['1.2']),('1.3 constant rate',pe),('1.3 variable rate',pv),('3.1 upper',sur['upper']),('3.1 lower',sur['lower'])]
v['CHECK_TABLE']='\n'.join(f'{name} & {q["condition_A"]:.4g} & {q["condition_ATA"]:.4g} & {sci(q["qr_numpy_max_difference"])} & {sci(q["normal_numpy_max_difference"])} '+r'\\' for name,q in labels)
v['COND_RAW']=f'{pv["unscaled_condition_A"]:.4g}';v['COND_SCALED']=f'{pv["condition_A"]:.4g}'
verification=json.loads((OUT/'verification.json').read_text());v['CHECK_COUNT']=str(verification['total']);v['NUMPY']=R['metadata']['numpy'];v['SCIPY']=R['metadata']['scipy'];v['MATPLOTLIB']=R['metadata']['matplotlib']
s=(REPORT/'template.tex.in').read_text()
for key,value in v.items():s=s.replace('@@'+key+'@@',value)
assert '@@' not in s,'Unexpanded template placeholder'
(REPORT/'main.tex').write_text(s)
print('Generated standalone report/main.tex')
