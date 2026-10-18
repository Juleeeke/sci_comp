"""Render final PDF pages and two-page review spreads for independent inspection."""
from pathlib import Path
import pymupdf as fitz
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
for mode,pdf in [('latex',ROOT/'03_最终实验报告/Report.pdf'),('word',ROOT/'06_验证记录/word_render/Report.pdf')]:
 if not pdf.exists():continue
 d=fitz.open(pdf);out=ROOT/'06_验证记录'/mode;out.mkdir(exist_ok=True)
 for i,page in enumerate(d):page.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False).save(str(out/f'page_{i+1}.png'))
 for i in range(0,len(d),2):
  ims=[Image.open(out/f'page_{j+1}.png') for j in range(i,min(i+2,len(d)))];sheet=Image.new('RGB',(sum(x.width for x in ims),max(x.height for x in ims)+24),'#eee');x=0
  for j,im in enumerate(ims):sheet.paste(im,(x,24));ImageDraw.Draw(sheet).text((x+5,5),f'{mode} page {i+j+1}',fill='black');x+=im.width
  sheet.save(out/f'spread_{i//2+1}.png')
 print(mode,len(d),'pages rendered')
