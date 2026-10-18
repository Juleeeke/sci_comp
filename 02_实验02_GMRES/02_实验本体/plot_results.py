"""Plot measured residual/error histories without changing any timing data."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/scicomp-lab02-mpl')
import json, csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent/'results'
(P/'figures').mkdir(exist_ok=True)
d=json.loads((P/'results.json').read_text())
for case in d['cases']:
    tag=case['name'].replace(' ','_').replace('=','_')
    fig,axes=plt.subplots(1,2,figsize=(10,3.45))
    for name,m in case['methods'].items():
        h=m['history'];t=[q['time_s']*1000 for q in h]
        label=name+(' (diverged)' if m['status']=='diverged' else '')
        axes[0].semilogy(t,[max(q['residual'],1e-17) for q in h],label=label)
        axes[1].semilogy(t,[max(q['error'],1e-17) for q in h],label=label)
        with (P/(tag+'_'+name+'_history.csv')).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(h[0]));w.writeheader();w.writerows(h)
    for ax,title in zip(axes,['True residual norm','Error norm against exact solution']):
        ax.set_xlabel('Elapsed solve time (ms)');ax.set_title(title,fontsize=10);ax.grid(alpha=.25);ax.legend(fontsize=7)
    axes[0].set_ylabel('Euclidean norm');axes[1].set_ylabel('Euclidean norm')
    fig.suptitle('Experiment '+case['name'],fontsize=11);fig.tight_layout()
    fig.savefig(P/'figures'/(tag+'.png'),dpi=190);fig.savefig(P/'figures'/(tag+'.pdf'));plt.close(fig)
fig,ax=plt.subplots(figsize=(6.6,3.5));ns=np.array([50,100,200]);h=1/ns
for name in ['GMRES','ILU-GMRES']:
    for metric,style in [('bvp_error_max','o-'),('bvp_error_discrete_l2','s--')]:
        y=[next(c for c in d['cases'] if c.get('grid_n')==int(n))['methods'][name][metric] for n in ns]
        ax.loglog(h,y,style,label=name+' '+('max norm' if metric.endswith('max') else 'discrete L2'))
ax.loglog(h,.1*h*h,':',color='gray',label='Reference 0.1 h squared');ax.set_xlabel('Grid spacing h');ax.set_ylabel('Discretization error');ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout()
fig.savefig(P/'figures/convergence.png',dpi=190);fig.savefig(P/'figures/convergence.pdf');plt.close(fig)
print('Saved six time-history plots, convergence plot and all history CSV files.')
