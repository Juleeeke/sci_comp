"""Build the complete ZIP and verify CRCs, entry bytes and SHA-256 hashes."""
import hashlib,json,zipfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
archive=ROOT/'Lab3_submission.zip';receipt=ROOT/'package_verification.json'
for name in ['verification.json','delivery_validation.json']:
    v=json.loads((ROOT/'experiment/results'/name).read_text())
    if v['passed']!=v['total']:raise RuntimeError(f'Checks failed: {name}')
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p not in [archive,receipt,ROOT/'MANIFEST.sha256'] and not any(v.startswith('.') or v=='__pycache__' for v in p.relative_to(ROOT).parts) and p.suffix not in ['.log','.aux','.out','.xdv','.pyc'])
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=''.join(f'{sha(p.read_bytes())}  {p.relative_to(ROOT).as_posix()}\n' for p in files)
(ROOT/'MANIFEST.sha256').write_text(manifest);files.append(ROOT/'MANIFEST.sha256')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,'lab3/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as z:
    if z.testzip() is not None:raise RuntimeError('CRC failure')
    if len(z.namelist())!=len(set(z.namelist())):raise RuntimeError('Duplicate entry')
    for p in files:
        if z.read('lab3/'+p.relative_to(ROOT).as_posix())!=p.read_bytes():raise RuntimeError('Archive bytes differ')
    for line in manifest.splitlines():
        expected,name=line.split('  ',1)
        if sha(z.read('lab3/'+name))!=expected:raise RuntimeError('Manifest mismatch')
info=dict(verified_utc=datetime.now(timezone.utc).isoformat(),archive=archive.name,bytes=archive.stat().st_size,
          sha256=sha(archive.read_bytes()),entry_count=len(files),crc_passed=True,all_entry_bytes_match=True,all_manifest_hashes_match=True)
receipt.write_text(json.dumps(info,indent=2)+'\n')
print(json.dumps(info,indent=2))
