"""Check the final PDF, report equations, figures and reproducible source files."""
import json,re,subprocess,sys,tempfile
from pathlib import Path
import numpy as np
import pymupdf
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'results'
r=json.loads((OUT/'results.json').read_text());c=r['cases'];checks=[]
def check(name,condition,detail=''):checks.append(dict(name=name,passed=bool(condition),detail=detail))
pdf=ROOT/'report/main.pdf';tex=ROOT/'report/main.tex';d=pymupdf.open(pdf);text='\n'.join(p.get_text() for p in d);source=tex.read_text()
check('Final English PDF has 10 pages',len(d)==10)
check('No empty or orphan body pages',all(len(p.get_text())>600 for p in list(d)[1:]))
check('English report has no CJK characters',not re.search(r'[\u3400-\u9fff]',text))
check('All seven experiment labels are present',all('Experiment '+t in text for t in ['1.1','1.2','1.3','2.1','2.2','2.3','3.1']))
check('All seven figures are present',len(re.findall(r'Figure \d+:',text))==7)
check('Title-only cover',d[0].get_text().strip()=='Lab 3\nApplications of Least Squares\nand Best Square Approximation')
check('Standalone LaTeX has no external figure or source dependency',not re.search(r'\\(?:includegraphics|input|include)\b',source) and '@@' not in source and r'\Line(' in source)
check('PDF is newer than generated LaTeX',pdf.stat().st_mtime>=tex.stat().st_mtime)
log=(ROOT/'report/main.log').read_text()
check('Compilation has no errors or layout overflow',not re.search(r'Overfull|Underfull|^!|^error:',log,re.M))
for i,page in enumerate(d):
    # Render all final pages, then discard temporary raster outputs.
    pix=page.get_pixmap(matrix=pymupdf.Matrix(.5,.5))
    if pix.width<200 or pix.height<200:raise RuntimeError('Unexpected render dimensions')
check('All final PDF pages render successfully',True)
check('Report literal exact coefficient vector',np.allclose(np.array([1354,203,-449])/890,c['1.1_literal']['coefficients'],atol=1e-14))
check('Report literal exact residual vector',np.allclose(np.array([-854,1098,-183,-1159])/890,c['1.1_literal']['residual'],atol=1e-14))
line=np.loadtxt(HERE/'data/linear_points.csv',delimiter=',',skiprows=1);B=np.column_stack([np.ones(5),line[:,0]])
check('Report line normal equations match original points',np.array_equal(B.T@B,[[5,151],[151,4629]]) and np.array_equal(B.T@line[:,1],[720,22240]))
check('Report line rational coefficients and RSS',np.allclose(c['1.2']['coefficients'],[-3170/43,310/43]) and np.isclose(c['1.2']['rss'],4050/43))
check('Numerical verification passed in full',json.loads((OUT/'verification.json').read_text())['passed']==38)
check('All source programs parse',all(compile(p.read_text(),str(p),'exec') for p in HERE.glob('*.py')))
names=['linear_fit','population_models','population_log_residuals','continuous_approximations','airfoil_fit']
for name in names:
    q=pymupdf.open(OUT/'figures'/f'{name}.pdf');check(name+': standalone PDF and PNG readable',len(q)==1 and Image.open(OUT/'figures'/f'{name}.png').width>600)
check('Input data CSV files retained',all((HERE/'data'/n).is_file() for n in ['linear_points.csv','population.csv','rae2822.csv']))
check('Pointwise fit CSV files retained',all((OUT/n).is_file() for n in ['linear_fit.csv','population_fits.csv','airfoil_upper.csv','airfoil_lower.csv']))
check('Original PDF and Markdown retained',all((ROOT/f'2-2-DLSM-BSA--Application--lab.{ext}').is_file() for ext in ['pdf','md']))
check('Reproduction instructions and dependency versions retained',(ROOT/'README.md').is_file() and (ROOT/'requirements.txt').is_file() and (ROOT/'report/compile.sh').is_file())
# Regenerate the report source and require exact byte agreement.
before=tex.read_bytes();before_stat=tex.stat();subprocess.run([sys.executable,str(HERE/'build_report.py')],check=True,capture_output=True)
check('Report regeneration reproduces exact LaTeX bytes',before==tex.read_bytes())
# Preserve source mtime to keep the PDF freshness check meaningful on reruns.
import os
if before==tex.read_bytes():
    os.utime(tex,ns=(before_stat.st_atime_ns,before_stat.st_mtime_ns))
result=dict(passed=sum(v['passed'] for v in checks),total=len(checks),checks=checks)
(OUT/'delivery_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(f"{result['passed']}/{result['total']} delivery checks passed")
for v in checks:
    if not v['passed']:print('FAIL:',v['name'])
raise SystemExit(0 if result['passed']==result['total'] else 1)
