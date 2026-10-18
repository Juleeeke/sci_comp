"""Reproduce this complete assignment from its canonical directory."""
from pathlib import Path
import subprocess,sys,os
R=Path(__file__).resolve().parent
P=sys.executable
for script in ['02_实验本体/run_experiment.py','02_实验本体/verify_results.py','02_实验本体/plot_results.py','make_content.py']:
 if (R/script).exists():subprocess.run([P,str(R/script)],cwd=R,check=True)
D=os.environ.get('ARTIFACT_PYTHON',P)
subprocess.run([D,str(R/'build_report.py'),'--tex'],cwd=R,check=True)
subprocess.run(['bash',str(R/'04_LaTeX源码/compile.sh')],cwd=R,check=True)
subprocess.run([D,str(R/'build_report.py'),'--word'],cwd=R,check=True)
subprocess.run([P,str(R/'verify_delivery.py')],cwd=R,check=True)
