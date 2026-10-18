#!/usr/bin/env python3
"""Verify exact final Word/PDF files, source preservation and requirement coverage."""
from pathlib import Path
import csv, hashlib, json, re, unicodedata, zipfile
from lxml import etree
import pymupdf as fitz
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parent
OUT = ROOT/'06_验证记录'
OUT.mkdir(exist_ok=True)
checks = {}
def check(name, condition):
    checks[name] = bool(condition)
    if not condition: raise AssertionError(name)
def canonical(text):
    return re.sub('[^a-z0-9]', '', unicodedata.normalize('NFKC', text).lower())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

numeric = json.loads((ROOT/'02_实验本体/results/verification.json').read_text())
check('39_numerical_assertions', len(numeric) == 39 and all(numeric.values()))
for name, ranks in [('image_metrics.csv', [5,10,20,50,100]), ('data_errors.csv', list(range(1,21)))]:
    rows = list(csv.DictReader((ROOT/'02_实验本体/results'/name).open()))
    check(name+'_requested_ranks', [int(row['k']) for row in rows] == ranks)
check('assignment_preserved', sha(ROOT/'01_指导资料/Assignment.pdf') ==
      'c71658550b4dc1b9f574b542e1104c939febc8660cac5bdff1a03458baae07c9')
check('template_preserved', sha(ROOT/'01_指导资料/Original_Report_Template.docx') ==
      sha(ROOT.parent/'01_实验01_SVD及其应用/01_指导资料/Original_Report_Template.docx'))
pages = json.loads((ROOT/'04_报告源码/report_content.json').read_text())
equations = sum(b['kind'] == 'equation' for pg in pages for b in pg['blocks'])
word = ROOT/'03_最终实验报告/SVD_Homework_English.docx'
with zipfile.ZipFile(word) as archive:
    check('docx_integrity', archive.testzip() is None)
    xml = etree.fromstring(archive.read('word/document.xml'))
    ns = dict(w='http://schemas.openxmlformats.org/wordprocessingml/2006/main',
              m='http://schemas.openxmlformats.org/officeDocument/2006/math')
    check('all_editable_office_equations', len(xml.xpath('//m:oMath', namespaces=ns)) == equations)
    check('eight_row_template', len(xml.xpath('/w:document/w:body/w:tbl[1]/w:tr', namespaces=ns)) == 8)
    check('four_figures_in_word', len([n for n in archive.namelist() if n.startswith('word/media/')]) == 4)
    visible = ''.join(xml.xpath('//w:t/text()|//m:t/text()', namespaces=ns))
    check('word_english', not re.search('[\u4e00-\u9fff]', visible))
    for label in ['Course', 'Class', 'Name', 'Student ID', 'Date', 'Instructor', 'Grade']:
        check('historical_field_'+label, label+':' in visible)
    core = etree.fromstring(archive.read('docProps/core.xml'))
    check('word_author_blank', not core.xpath('//*[local-name()="creator"]/text()'))
pdf = ROOT/'03_最终实验报告/SVD_Homework_English.pdf'
document = fitz.open(pdf)
text = '\n'.join(pg.get_text() for pg in document)
normalized = canonical(text)
check('pdf_25_pages', len(document) == 25)
check('pdf_english', not re.search('[\u4e00-\u9fff]', text))
check('pdf_no_replacement_glyph', '\ufffd' not in text)
check('pdf_no_formula_conversion_error', '¿' not in text)
check('pdf_author_blank', not document.metadata.get('author'))
check('pdf_all_pages_have_content', all(len(pg.get_text().strip()) > 800 for pg in document))
for number in range(1,16):
    check('problem_'+str(number), canonical('Problem '+str(number)+'.') in normalized)
check('optional_challenge', canonical('Optional challenge.') in normalized)
missing = []
for pg in pages:
    if canonical(pg['title']) not in normalized: missing.append(pg['title'])
    for b in pg['blocks']:
        if b['kind'] in ['paragraph','code'] and canonical(b['text']) not in normalized:
            missing.append(b['text'][:100])
        if b['kind'] == 'table':
            for row in b['rows']:
                for value in row:
                    if canonical(str(value)) not in normalized: missing.append(str(value))
check('all_prose_code_table_values_present', not missing)
outside = []
for idx, pg in enumerate(document):
    for block in pg.get_text('dict')['blocks']:
        if block['type'] != 0: continue
        for line in block['lines']:
            for span in line['spans']:
                x0,y0,x1,y1 = span['bbox']
                if span['text'].strip() and (x0<0 or y0<0 or x1>pg.rect.width+1 or y1>pg.rect.height+1):
                    outside.append([idx+1,span['text']])
check('pdf_no_text_outside_page', not outside)
check('one_page_essay', sum('Problem 15.' in pg.get_text() for pg in document) == 1 and
      canonical('answer.') in canonical(document[19].get_text()))
for start in range(0,len(document),12):
    count = min(12,len(document)-start)
    sheet = Image.new('RGB',(4*355,((count+3)//4)*490),'#e4e7ed')
    for j in range(count):
        pg = document[start+j]
        pix = pg.get_pixmap(matrix=fitz.Matrix(.56,.56),alpha=False)
        im = Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        im.thumbnail((340,463)); x=(j%4)*355; y=(j//4)*490
        sheet.paste(im,(x+(355-im.width)//2,y+5))
        ImageDraw.Draw(sheet).text((x+8,y+475),'Page '+str(start+j+1),fill='black')
    sheet.save(OUT/f'contact_sheet_{start+1:02d}.jpg')
for i in [0,2,4,7,8,11,14,17,18,19,20,23,24]:
    document[i].get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False).save(OUT/f'page_{i+1:02d}.png')
summary = dict(checks_passed=sum(checks.values()),checks_total=len(checks),checks=checks,
               pdf_pages=len(document),editable_equations=equations,missing_content=missing,
               pdf_producer=document.metadata.get('producer'),
               artifacts={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in [word,pdf]})
(OUT/'delivery_verification.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
