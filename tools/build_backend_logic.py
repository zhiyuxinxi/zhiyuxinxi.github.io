"""Materialize only reviewed public JSON; keep exact bytes and provenance."""
import hashlib, json, pathlib, sys, zipfile

SOURCE = 'fe35cf7aa010d718c967679616bd1a44de71908c'
SHA = '9ca8da6cdef79d2a0c4e6d669b1ac7054b825f2ea4aad4f10cea87abe53de2ae'
NAMES = {'architecture-plan.json','architecture-plan.md','architecture-plan-validation.json','cloud-boundaries.json','cloud-boundaries.md'}

def build(path):
    raw=pathlib.Path(path).read_bytes()
    assert len(raw)==97837 and hashlib.sha256(raw).hexdigest()==SHA
    out=pathlib.Path(__file__).resolve().parents[1]/'handoff/backend-logic'
    out.mkdir(exist_ok=True)
    files={}
    with zipfile.ZipFile(path) as archive:
        assert set(archive.namelist())==NAMES
        for name in archive.namelist():
            body=archive.read(name)
            files[name]={'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}
            if name.endswith('.json'):
                json.loads(body)
                (out/name).write_bytes(body)
    (out/'manifest.json').write_text(json.dumps({'sourceCommit':SOURCE,'zipBytes':97837,'zipSha256':SHA,'sourceFiles':files,'publishedFiles':[n for n in files if n.endswith('.json')],'implementation':'Read-only documentation; no APP business implemented'},ensure_ascii=False,indent=2)+'\n')
    print('Verified public package; published 3 exact JSON source files plus manifest.')

if __name__=='__main__':build(sys.argv[1])
