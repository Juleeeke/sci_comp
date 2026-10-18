#!/usr/bin/env python3
"""Check the actual delivered PDFs, editable Word source and experimental records."""
from pathlib import Path
import json, re, csv, hashlib, zipfile, unicodedata
import pymupdf as fitz
from lxml import etree
ROOT=Path(__file__).resolve().parent
R=ROOT/'02_实验本体/results'
checks={}
def check(name, condition):
    checks[name]=bool(condition)
    if not condition:raise AssertionError(name)
def canonical(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKC',s).lower())
numeric=json.loads((R/'verification.json').read_text())
check('22_numerical_checks_pass',len(numeric)==22 and all(numeric.values()))
rows=list(csv.DictReader((R/'image_metrics_all_k.csv').open(encoding='utf-8-sig')))
check('512_image_metric_rows',len(rows)==512 and [int(x['k']) for x in rows]==list(range(1,513)))
original_hashes={'Lab_Instructions.pdf':'524167a5257aa42549d3e93d7c68de0845227a7daeb0649ba08bc73cc3e766e9','Original_Report_Template.docx':'807bcf1edd7f163ebdf6159b8766a0888cdfed878d3c2f906b6d58486fe600ba'}
for name,digest in original_hashes.items():check('original_'+name,hashlib.sha256((ROOT/'01_指导资料'/name).read_bytes()).hexdigest()==digest)
sources=json.loads((ROOT/'02_实验本体/data/sources.json').read_text())
for source in sources:
    p=ROOT/'02_实验本体/data'/Path(source['file']).name
    check('data_'+p.name,hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256'])
docx=ROOT/'03_最终实验报告/SVD_Report_English_Word.docx'
with zipfile.ZipFile(docx) as z:
    check('docx_zip_integrity',z.testzip() is None)
    xml=etree.fromstring(z.read('word/document.xml'))
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
    check('editable_office_equations',len(xml.xpath('//m:oMath',namespaces=ns))==14)
    equations=xml.xpath('//m:oMath',namespaces=ns)
    equation_text=lambda node:''.join(node.xpath('.//m:t/text()',namespaces=ns))
    check('word_error_difference_preserved','A−Ak' in equation_text(equations[2]).replace('-', '−'))
    check('word_quantizer_clipping_preserved','clip' in equation_text(equations[10]))
    check('retained_eight_row_template',len(xml.xpath('/w:document/w:body/w:tbl[1]/w:tr',namespaces=ns))==8)
    check('ten_figures_in_word',len([n for n in z.namelist() if n.startswith('word/media/')])==10)
    visible=''.join(xml.xpath('//w:t/text()|//m:t/text()',namespaces=ns))
    check('word_content_english',not re.search('[\u4e00-\u9fff]',visible))
    for label in ['Class','Name','Student ID','Lab date','Instructor','Grade']:
        check('historical_field_'+label,label+':' in visible)
content=json.loads((ROOT/'report_content.json').read_text())
pdf_info={}
for variant in ['Word','LaTeX']:
    p=ROOT/f'03_最终实验报告/SVD_Report_English_{variant}.pdf';doc=fitz.open(p)
    text='\n'.join(page.get_text() for page in doc)
    check(variant+'_16_pages',len(doc)==16)
    check(variant+'_english',not re.search('[\u4e00-\u9fff]',text))
    check(variant+'_no_replacement_glyph','\ufffd' not in text)
    check(variant+'_no_blank_pages',all(len(page.get_text().strip())>400 for page in doc))
    check(variant+'_no_personal_author',not doc.metadata.get('author'))
    canvas=[]
    for idx,pg in enumerate(doc):
        for block in pg.get_text('dict')['blocks']:
            if block['type']!=0:continue
            for line in block['lines']:
                for span in line['spans']:
                    x0,y0,x1,y1=span['bbox']
                    if span['text'].strip() and (x0<0 or y0<0 or x1>pg.rect.width+1 or y1>pg.rect.height+1):canvas.append((idx+1,span['text']))
    check(variant+'_text_within_page',not canvas)
    normalized=canonical(text)
    missing=[]
    for pg in content:
        for b in pg['blocks']:
            if b['kind']=='paragraph' and canonical(b['text']) not in normalized:missing.append(b['text'][:70])
    check(variant+'_all_report_paragraphs_present',not missing)
    pdf_info[variant]={'pages':len(doc),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'missing_paragraphs':missing,'producer':doc.metadata.get('producer')}
summary={'checks_passed':sum(checks.values()),'checks_total':len(checks),'checks':checks,'pdfs':pdf_info,'rendering':'All pages inspected in contact sheets; representative pages inspected at higher resolution.'}
(ROOT/'06_验证记录/delivery_verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False,indent=2))
