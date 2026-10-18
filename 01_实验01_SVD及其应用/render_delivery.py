#!/usr/bin/env python3
from pathlib import Path
import pymupdf as fitz
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parent
(root/'06_验证记录').mkdir(exist_ok=True)
for name in ['Word','LaTeX']:
    doc=fitz.open(root/f'03_最终实验报告/SVD_Report_English_{name}.pdf')
    cols=4;rows=(len(doc)+cols-1)//cols
    sheet=Image.new('RGB',(345*cols,490*rows),'#e4e7ed')
    for i,page in enumerate(doc):
        pix=page.get_pixmap(matrix=fitz.Matrix(.55,.55),alpha=False)
        im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        im.thumbnail((330,465));x=(i%cols)*345;y=(i//cols)*490
        sheet.paste(im,(x+(345-im.width)//2,y+8))
        ImageDraw.Draw(sheet).text((x+8,y+473),f'{name} page {i+1}',fill='black')
    sheet.save(root/f'06_验证记录/{name}_contact_sheet.jpg')
    for idx in range(len(doc)):
        doc[idx].get_pixmap(matrix=fitz.Matrix(1.3,1.3),alpha=False).save(str(root/f'06_验证记录/{name}_page_{idx+1}.png'))
    if name=='Word':
        doc[2].get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(190,260,450,330),alpha=False).save(str(root/'06_验证记录/formula_detail.png'))
print('Rendered final PDFs.')
