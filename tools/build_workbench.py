"""Refresh the existing review-shell catalog from canonical route and tree manifests."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
p=root/'workbench-data.js';raw=p.read_text();data=json.loads(raw.split('=',1)[1].rstrip(';\n'))
data['routes']=json.loads((root/'handoff/routes.json').read_text())
data.update(json.loads((root/'handoff/workbench-map.json').read_text()))
p.write_text('window.WorkbenchData='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
print('Workbench manifest synchronized:',len(data['routes']),'nodes')
