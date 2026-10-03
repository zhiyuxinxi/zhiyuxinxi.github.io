"""Public candidate review evidence; no private research or real user data.

Run: python candidate_review_bundle.py <candidate> <accepted-reference> <output>
Records the disposition of 29 specific premium static findings and tests actual
keyboard dispatch. The original strict audit remains a failure; this companion
does not modify its parser, suppress findings, or certify accessibility/aesthetics.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import html, json, os, re, subprocess, sys
from playwright.sync_api import sync_playwright

ROOT, BASELINE, OUT = [Path(x).resolve() for x in sys.argv[1:4]]
OUT.mkdir(parents=True, exist_ok=True)
(OUT/'before').mkdir(exist_ok=True)
(OUT/'controls').mkdir(exist_ok=True)
# ID, declaration file, line, ordinal on line, delegated action, runtime status.
# Source locations are checked below: drift fails rather than silently waiving it.
DECLARATIONS = [
 (1,'components.js',51,0,'tab',True),(2,'components.js',55,0,'factor',True),
 (3,'experience-v2.js',22,0,'nav',False),(4,'experience-v2.js',34,0,'nav',False),
 (5,'experience-v2.js',69,0,'nav',False),(6,'experience-v2.js',75,0,'nav',False),
 (7,'experience-v2.js',104,0,'nav',True),(8,'experience-v3.js',39,0,'nav',True),
 (9,'experience-v3.js',117,0,'nav',True),(10,'experience-v3.js',124,0,'nav',True),
 (11,'experience-v3.js',124,1,'nav',True),(12,'experience-v3.js',124,2,'nav',True),
 (13,'experience-v3.js',126,0,'nav',True),(14,'experience-v3.js',149,0,'avatar',True),
 (15,'experience-v3.js',150,0,'avatar',True),(16,'views.js',9,0,'mode',False),
 (17,'views.js',13,0,'category',False),(18,'views.js',14,0,'nav',False),
 (19,'views.js',16,0,'answer',True),(20,'views.js',20,0,'record-filter',False),
 (21,'views.js',20,1,'nav',False),(22,'views.js',22,0,'theme',False),
 (23,'views.js',22,1,'avatar',False),(24,'views.js',23,0,'nav',True),
 (25,'views.js',31,0,'plan',True),(26,'views.js',33,0,'nav',True),
 (27,'views.js',37,0,'font-size',True),(28,'experience-v2.js',47,0,None,False),
 (29,'experience-v3.js',79,0,None,True)
]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
def serve(root):
 s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)))
 Thread(target=s.serve_forever,daemon=True).start()
 return s,f'http://127.0.0.1:{s.server_port}'
server,base=serve(ROOT);refserver,ref=serve(BASELINE)
findings=[];checks=[];errors=[]
for id,file,line,ordinal,action,current in DECLARATIONS:
 source=(ROOT/'prototype'/file).read_text().splitlines()[line-1]
 tags=re.findall(r'<'+('button' if action else 'textarea')+r'\b[^>]*>',source)
 if action:
  tags=[tag for tag in tags if ('data-action="'+action+'"') in tag]
  ordinal=sum(f['source']==f'prototype/{file}:{line}' and f['action']==action for f in findings)
 tag=tags[ordinal]
 assert (('data-action="'+action+'"') in tag if action else 'class="textarea"' in tag), (id, tag)
 findings.append({'id':id,'source':f'prototype/{file}:{line}','action':action,'declaration':tag,
  'runtime':'current' if current else 'superseded template',
  'rule':'affordance.actionless-button' if action else 'form.textarea-resize-missing',
  'disposition':'pending runtime evidence' if current else 'Not a current reachable declaration; later Views.map assignment replaces this template. Its absence of an inline handler/style is not evidence of a current usability defect.',
  'owner':'app.js document click delegate → dispatch' if action else 'product.css shared textarea resize + V3.updateCounts auto-grow'})
assert "document.addEventListener('click'" in (ROOT/'prototype/app.js').read_text()

def check(ok,message):
 if not ok: raise AssertionError(message)
def goto(p,route,scenario='default'):
 p.goto(f'{base}/prototype/index.html?reset=1&scenario={scenario}#{route}')
 p.wait_for_function('window.App&&window.Ambient');p.wait_for_timeout(100)
def activate(p,selector,expect):
 control=p.locator(selector).first;control.scroll_into_view_if_needed();control.focus();p.keyboard.press('Enter')
 p.wait_for_function(expect,timeout=5000)
def run(id,p,fn):
 try:
  fn();p.screenshot(path=str(OUT/'controls'/f'{id:02}.png'))
  checks.append({'finding':id,'status':'PASS','activation':'native keyboard Enter (textarea: fill, focus, End and scroll)'})
 except Exception as e:
  checks.append({'finding':id,'status':'FAIL','error':str(e)})

with sync_playwright() as w:
 launch={'headless':True,'args':['--no-sandbox']}
 if os.environ.get('CHROMIUM_PATH'):launch['executable_path']=os.environ['CHROMIUM_PATH']
 b=w.chromium.launch(**launch);p=b.new_page(viewport={'width':390,'height':844},locale='zh-CN')
 p.on('pageerror',lambda e:errors.append(str(e)))
 for theme in ['sunrise','candy','berry','lime','aurora','sea','nebula','amber']:
  for route in ['home','explore','assistant','me']:
   p.goto(f'{ref}/prototype/index.html?reset=1&theme={theme}#{route}');p.wait_for_function('window.App&&window.Ambient');p.evaluate('Ambient.sample(8)');p.wait_for_timeout(100)
   p.screenshot(path=str(OUT/'before'/f'{theme}-{route}.png'))
 p.set_viewport_size({'width':1440,'height':1000});p.goto(ref);p.wait_for_function("document.querySelector('#runtime-status').textContent.includes('原型已连接')");p.wait_for_timeout(250);p.screenshot(path=str(OUT/'before/workbench-1440.png'))
 p.set_viewport_size({'width':390,'height':844})
 def nav_case(id,route,scenario,selector,expected):
  def fn():
   goto(p,route,scenario);activate(p,selector,expected)
  run(id,p,fn)
 nav_case(1,'home','default','.nav [data-route=explore]','App.currentRoute==="explore"')
 def factor():
  goto(p,'report?id=report-sample-01');p.locator('.factor-detail summary').click();activate(p,'.bottle-tile','!!document.querySelector("[role=dialog]")');check('factor:A' in p.locator('[role=dialog]').inner_text(),'Wrong factor detail')
 run(2,p,factor)
 nav_case(7,'records','topic-record','.record-item','App.currentRoute.startsWith("topic-workspace")')
 nav_case(8,'explore','default','.v3-topic[data-id=city-choice]','App.currentRoute==="topic?id=city-choice"')
 nav_case(9,'assistant','history','.history-row','App.currentRoute==="conversation?id=conversation-demo-history"')
 nav_case(10,'me','mixed-records','.v3-profile-stats [data-filter="本人记录"]','App.currentRoute==="records"&&App.snapshot.recordFilter==="本人记录"')
 nav_case(11,'me','mixed-records','.v3-profile-stats [data-route=actions]','App.currentRoute==="actions"')
 nav_case(12,'me','mixed-records','.v3-profile-stats [data-filter="全部答卷"]','App.currentRoute==="records"&&App.snapshot.recordFilter==="全部答卷"')
 nav_case(13,'me','ongoing-action','.v3-action-resume','App.currentRoute==="action-detail?id=action-demo-v2"')
 nav_case(14,'appearance','default','[data-action=avatar][data-family=original][data-id="2"]','App.snapshot.avatar===2&&App.snapshot.avatarFamily==="original"')
 nav_case(15,'appearance','default','[data-action=avatar][data-family=scene][data-id="3"]','App.snapshot.avatar===3&&App.snapshot.avatarFamily==="scene"')
 nav_case(19,'question?id=session-demo-seed','question','[data-action=answer][data-id=a]','App.snapshot.sessions[0].answers["demo-q1"]==="a"')
 nav_case(24,'conversations','history','.history-row','App.currentRoute==="conversation?id=conversation-demo-history"')
 nav_case(25,'membership','default','[data-action=plan][data-id=monthly]','App.snapshot.plan==="monthly"')
 nav_case(26,'orders','paid-annual','.record-item','App.currentRoute==="order?id=DEMO-ANNUAL-001"')
 nav_case(27,'settings','default','[data-action=font-size][data-id=large]','App.snapshot.fontSize==="large"')
 def textarea():
  goto(p,'topic-workspace?topic=work-choice');field=p.locator('#topic-options');field.fill('合成测试。'*200);field.focus();p.keyboard.press('Control+End');p.wait_for_timeout(150)
  data=field.evaluate('e=>({resize:getComputedStyle(e).resize,overflow:getComputedStyle(e).overflowY,valueLength:e.value.length,clientHeight:e.clientHeight,scrollHeight:e.scrollHeight,selection:e.selectionEnd})')
  check(data['resize']=='none','Shared resize rule missing');check(data['selection']==data['valueLength'],'Long text end inaccessible');check(data['scrollHeight']>=data['clientHeight'],'Invalid text geometry')
  (OUT/'controls/textarea-computed.json').write_text(json.dumps(data,indent=2))
 run(29,p,textarea)
 # Verify the runtime owners that supersede old literal templates, without
 # injecting old markup and pretending a removed product control is reachable.
 owners=p.evaluate('Object.fromEntries(["home","explore","assistant","me","records","appearance","topic-workspace"].map(k=>[k,Views.map[k].toString()]))')
 check('AssessmentPreview.home' in owners['home'],'Home owner changed')
 for route,marker in [('explore','v3-topic-grid'),('assistant','v3-assistant-head'),('me','v3-notebook'),('records','这里还没有这类记录'),('appearance','v4-avatar-options'),('topic-workspace','v3-topic-form')]:
  check(marker in owners[route],'Unexpected current owner: '+route)
 (OUT/'runtime-owners.json').write_text(json.dumps(owners,ensure_ascii=False,indent=2))
 b.close()
server.shutdown();refserver.shutdown()
for f in findings:
 if f['runtime']=='current':
  result=next(x for x in checks if x['finding']==f['id']);f['runtimeEvidence']=result;f['screenshot']=f'controls/{f["id"]:02}.png'
  f['disposition']='Rule assumption does not fit the shared owner; direct runtime behavior passed.' if result['status']=='PASS' else 'Unresolved: runtime check failed; do not waive this finding.'
report={'originalStrictAudit':'29 errors; not suppressed and not relabeled as a clean strict pass','findings':findings,'checks':checks,'pageErrors':errors,'limits':'Superseded templates are source-owner verified, not claimed as user-reachable tests. This report checks these two rules only; it does not prove total usability or award-quality design.'}
(OUT/'static-findings-29.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
summary='''知遇测评候选：供独立审阅，未合并或部署。
before：已验收1301519的8主题×4主页面和工作台截图；after：本候选关键页面、窄屏、输入、弹层、键盘及工作台截图。
原速录像与像素报告在artifact的site/qa/soft-fields-restored目录。所有测试为合成本机数据。
视觉改动：390px首页说明不再单字落行；探索相关议题和主任务的纸面层级区分；个人资料入口从4张卡改为统一分组；320px收藏不竖排、5分类不留孤行；报告下一步减少嵌套卡；工作台增加目录可读性、长文分组，整页预览保留底部提示，文档模式隐藏无关工具。
仍需审美判断：各主题的纸面/背景层级是否足够，暖色主题的大色域是否适合长时阅读；低高度工作台整页缩放仍会缩小字，原尺寸入口保留；200%文字排版仍密集；原人物素材分辨率约220px，禁止擅自替换。测试数量不是审美评分。
静态29项：27项按钮缺内联handler、2项textarea缺内联resize。当前16个按钮逐一用键盘激活并核对结果，1个textarea核对计算样式和长输入；另11个按钮与1个textarea为已替代模板，核对当前Views.map所有者而不伪造可达路径。逐项裁决见static-findings-29.json。任何运行失败仍标未解决，不以基线相同豁免。
这些规则指向的真实缺陷若由运行验证证实就必须修复；该裁决不掩盖另外发现的收藏竖排、孤行、预览说明被裁剪等真实问题，它们已单独修复。真机、软键盘、读屏和完整跨浏览器验证未完成。
'''
(OUT/'REVIEW.txt').write_text(summary)
table=''.join('<tr><td>'+str(f['id'])+'</td><td>'+html.escape(f['source'])+'</td><td>'+html.escape(f['runtime'])+'</td><td>'+html.escape(f['disposition'])+'</td></tr>' for f in findings)
gallery='<h2>逐主题截图：修改前 → 候选</h2>'
for theme in ['sunrise','candy','berry','lime','aurora','sea','nebula','amber']:
 gallery+=f'<h3>{theme}</h3><p><a href="before/{theme}-home.png">原首页</a> → <a href="after/{theme}-home.png">候选首页</a> · <a href="before/{theme}-me.png">原个人页</a> → <a href="after/{theme}-me.png">候选个人页</a> · <a href="after/{theme}-modal.png">候选弹层</a></p>'
gallery+='<h2>工作台</h2><p><a href="before/workbench-1440.png">修改前</a> → <a href="after/workbench-1440.png">候选</a> · <a href="after/workbench-390-logic.png">窄屏只读方案</a></p>'
(OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>知遇候选证据</title><style>body{max-width:1000px;margin:40px auto;font:16px/1.8 system-ui}pre{white-space:pre-wrap}td{padding:12px;border-bottom:1px solid #ddd}</style><h1>知遇测评 · 候选审阅</h1><pre>'+html.escape(summary)+'</pre>'+gallery+'<p><a href="after/report.json">最终关键状态</a> · <a href="static-findings-29.json">29项逐项证据</a></p><table>'+table+'</table>')
print(json.dumps({'runtimeChecks':checks,'pageErrors':errors},ensure_ascii=False))
sys.exit(1 if errors or any(x['status']=='FAIL' for x in checks) else 0)
