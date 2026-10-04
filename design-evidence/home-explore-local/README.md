# 认识首页与探索目录候选

最新状态：缩放预览开始点击回归已修复。workbench-scroll-fixed.json：8/8 流程及516/516路由主题组合通过，无页面异常。下方未关闭描述是修复前历史；以本段及末尾根因记录为准。静态29项基线、未执行的实体手机/Safari/视频及独立视觉复核边界仍保留。未部署。

从当前main cf3737ce01c19df9832dde8d20609105deedcea7建立独立分支。只修改site/源，不镜像根目录、不部署；画像图和研究分支未合入。

## 实际修改

首页原版说明略增日常情境用途，人物比例、同框版本切换、四副入口保持。探索增加不可点击的简短介绍，8张卡统一横矩形、语义图标、问题标题及用途；分类为主，找主题默认收起。

公开目录增加keywords/aliases。NFKC、首尾空白/连续空白/大小写归一化；完整短查询按标题或别名完全匹配→标题包含→关键词/别名包含排序，同档保持目录序。分类与搜索取交集；不分词、不纠错、不调用AI，不索引私人资料。查询只在内存，返回保留、刷新清空、不写URL或持久化、不上传。清空立即回焦点；输入法组合时保留原结果，结束更新且不重建输入节点。

## AI 说明来源与边界

已按授权读取实际题目设计来源，确认 AI 辅助重写题目及选项、具体生活情境与行为描述。首页按此完善说明，没有引入近四周、提高准确度、诊断或实时 AI 作答承诺。原始题目及私有评审不放入本仓库。默认“暂不可开始”是 main 已有行为，正式题库未启用；没有借本次文案更新开放真实业务。

探索介绍已改为独立的轻量半透明容器，保持两行左右、无点击、箭头或 CTA。

## 已执行证据

- report.json：320/390/1440×12主题共36组合通过；首页切换主按钮位置变化0px；卡片非竖长、无水平溢出，卡片正文/分类最低对比度7.61:1；7组关键词/别名/空结果、中文组合输入、清空焦点、分类交集、键盘、查询不落盘、页面载入后离线无搜索请求、背景连续及减弱动态通过。无JS异常。
- product-regression.json：现行43路由×12主题、八专题本机保存闭环、首页版本、工作台等全部通过。
- premium-audit.json：严格静态审计失败29项；audit-comparison.json确认与main基线规则/文件计数一致，没有新增。模板委派按钮和统一CSS textarea规则未被脚本识别，不以此宣称严格通过。
- design-lint.log：DESIGN.md 0 errors，3个既有token警告。
- viewport文件为390px实际首屏；其余为完整页面截图，固定底栏出现在视口位置，不代表文档中插入底栏。

历史执行记录（修复前）：旧manifest的10个命令已在隔离副本执行，精确退出状态见configured-commands.json：themes、runtime（18项）、recordContract（14项）、previewUI、navigation、development、backendLogic通过。visual失败：旧首页/助理选择器与现行main结构、旧独立页夹具启动方式不兼容，完整日志保留；不把失败删除或改称通过。motion在创建录像上下文时因Playwright ffmpeg缺失失败。workbench的8项外框检查已通过，随后全主题路由扫描超过360秒超时，不宣称该脚本全量通过；现行product_structure_review的43×12独立矩阵已通过。

补充scene-contrast.json用浏览器计算后的两色端点与101个混色样本检查新增背景文字角色，最低5.07:1；属于角色数值检查，不是全屏像素或无障碍认证。

## 边界

浏览器已载入静态资源后断网可用；未增加网页冷启动离线缓存。未验证实体手机软键盘、Safari或全辅助技术。此候选待独立视觉审阅，未发布。

重放：CHROMIUM_PATH=/usr/bin/chromium python site/tools/home_explore_review.py site /tmp/home-explore-review；现行整体回归使用site/tools/product_structure_review.py。

## 本轮检查修复与复测

- visual-verified.json：修正失效的旧首页/画像选择器，使用真实工作台隔离样例；同时补充默认空报告断言。41 个案例通过，包括 28 秒人物静止/装饰动效观察与弹层焦点。保留历史 visual.log，不以跳过案例换取通过。
- product-regression.json：43 路由 × 12 主题，另检查所有实际渲染的启用按钮具有委派动作或真实表单提交、textarea 计算样式禁止拖动。无未绑定控件、可拖动输入框或溢出。
- audit-reconciliation.json：29 个静态报错逐项解释与 main 一致的原因；原审计器未修改，严格审计仍为失败，运行时证据不冒充静态通过。
- baseline-probe.json：main 与候选的默认禁用、旧选择器缺失、独立页不能启用工作台夹具等行为一致。
- 工作台扫描以 load 加应用/桥接显式等待替代每次固定 networkidle 等待，未减少任何路由或主题。workbench-first-run.json 的 516 个组合全部通过，但测评流程在点击开始后等待 question 路由超时（并非完成页滚动复位），单独重跑通过、连续全套复跑再次超时；保留失败，后续复测单独记录。
- 录像未补装 ffmpeg；动效证据使用浏览器时序观测、连续性/减弱动态断言与静态截图，不宣称视频录制通过。

### 工作台交互问题：失败历史（下方记录修复）

候选全量复跑仍为 7/8 外框流程通过、516/516 路由主题渲染通过；失败位于点击开始后等待第一题。main 同脚本 8/8 通过；候选独立五次复测四次通过、一次失败，因此暂列候选间歇问题，不能归入基线。未放宽等待或删除断言。完整复测、基线与堆栈分别见 workbench-retest.json、workbench-baseline.json、workbench-shell-diagnostic.json。设计候选可以独立审阅，但这不是发布验收通过。

失败现场 start-click-failure.png / start-click-failure-state.json：route=home、active=null、fixture=true、scrollY=50；点击后没有创建 session。尚未证实是缩放预览定位/滚动时序还是实际指针交互缺陷，因此不声称已修复。

### 指针点击修复与证据

真实原因是 ui.css 全局 html scroll-behavior:smooth：开始按钮自动滚动定位仍在动画中，缩放 iframe 内的指针坐标与移动后的按钮错开。事件记录显示滚动从 4→26→40→50px 持续变化，pointerdown/click 实际 target 为 home-assessment 容器，未进入 start 动作。不是 session 保存、题库或完成页滚动故障。

将全局滚动定位改为 auto，路由/焦点恢复即时完成；没有加点击重试、延迟等待、直接调用 App 或宽松断言。保留首页文案、介绍容器及背景装饰动效。pointer-before.json 为原版同一诊断 7/10，修复后为 pointer-after.json 的 10/10（10 个独立场景，不是失败后重试）；before/after-events 保存事件、命中与按钮坐标。首页探索 36 组合与 7 组检索再次通过。长期复现工具为 site/tools/workbench_pointer_review.py，失败返回非零退出码。

仓库内正式复现工具也已运行，pointer-canonical.json 的 10 个独立场景全部通过；保留真实 pointer 点击及完整三题完成流程，没有用 DOM click 或 dispatchEvent 绕过命中测试。

最后全工作台复测 workbench-scroll-fixed.json：8 项真实流程、516 路由主题组合全部通过，无 JS 异常。开始点击阻塞关闭；测试通过不替代独立视觉评审。
