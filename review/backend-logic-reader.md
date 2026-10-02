# 阶段二只读方案阅读候选

基线 main：`8d2fd8dd5ad14472622f1a2a77c599622830f307`。候选分支：`design/zhiyu-backend-logic-view`。尚未发布，等待父线程快速review。

## 数据与边界

正常git fetch取得公开方案提交 `fe35cf7aa010d718c967679616bd1a44de71908c` 的 `site/handoff/backend-logic-public.zip`；97837 bytes，SHA256 `9ca8da6cdef79d2a0c4e6d669b1ac7054b825f2ea4aad4f10cea87abe53de2ae`。5个源文件均记录字节数与哈希；网页发布两份原始JSON及原始本地validation，逐字节保持不变，未复制ZIP或私人资料。生成器 `tools/build_backend_logic.py` 可从固定包重建。

本地17实体、11操作、8时序、18待执行验收、29页面关联；云121个分类设计项，含11类数据、7条件流程、20异常、28待执行验收、13历史修补。数字是文档口径，不是已实现业务数量。

所有合法获准产品题库全部默认安装、首启不下载，且空批准清单不能假达标，保留原文。顶端直接显示三个位置候选仍待确认；会员不隐含全量上传，按次AI与长期留存独立，本地来源哈希不等于服务权威，到期本地资料不丢与免费阅读导出强建议待决等条款全部来自审定原文。未新增架构决策、APP业务、SDK、手机号、云存或上传操作。

## 阅读与导航

在“逐页开发说明／历史对账”旁增加“底层逻辑方案”，分“本地题库与引擎”“数据与云边界”两块。复用既有转义字段渲染、details、文档滚动区、按钮与中文搜索；原界面、主题、记录及原型源码未改。顶层目录与状态可筛选，搜索进入当前方案全部目录，结果每次20项。两份文档各自的已明确、建议、条件必需／必要约束、待决定／条件待确认保持原词并附定义。

实体、流程、异常、验收、关联需求／待决与出处在折叠内容内阅读；页ID可回到具体页开发说明，沿原未保存内容保护导航。官方出处仅链接当前审定文档的URL，不引入HTML或Markdown执行器。hash保存公开查询，不写本机业务资料。数据按选择文档加载，首屏实际预览不读取方案JSON；错误可重试。

候选直达：`#page=home&mode=logic`；云数据目录：`#page=home&mode=logic&logicDoc=cloud&logicSection=dataClasses`。

## 实测证据

- [新阅读器专项](../qa/backend-logic/report.json)：5项分组检查通过。数据字节哈希、数目、原状态、全部页面关联；搜索/清空/IME/目录/状态/加载更多/URL恢复；流程与页面跳转、官方出处；1440与390px直达回预览；失败重试和仅同源静态请求。浏览器错误0。需求编号格式及既有D-01至D-22/候选引用核查通过；完整161需求的逐项成员校验沿用源数据交叉审核，本轮没有拿公开子集冒充完整矩阵复核。
- [原工作台壳回归](../qa/backend-logic/workbench-shell-report.json)：8/8，包含原导航、树搜索、真实页面内跳转、fit/原尺寸与窄屏抽屉。明确未重跑468主题route矩阵。
- [原逐页说明回归](../qa/backend-logic/development-report.json)：13/13，共享渲染器扩展未改变原39页说明和历史对账行为。
- JS语法、生成器再生成、`git diff --check`通过。严格静态审计仍为29项基线问题，新阅读器0项，见[静态结果](../qa/backend-logic/premium-audit.json)。不称严格扫描全通过。

命令：`CHROMIUM_PATH=/usr/bin/chromium python site/tools/backend_logic_test.py site`；同环境运行 `development_review_test.py site`；`WORKBENCH_SHELL_ONLY=1`运行 `workbench_coverage.py site`。未运行未改动的背景/全主题长录像。正式发布仍保留原HTTP及说明门禁，增加新专项；镜像白名单新增 `backend-logic-review.js`，本轮未触发发布。

## 真实截图

- [桌面本地方案](../qa/backend-logic/desktop-local.png)
- [桌面条件流程展开](../qa/backend-logic/desktop-cloud-flow.png)
- [桌面数据边界正文](../qa/backend-logic/boundary-detail-1440.png)
- [390px目录与折叠](../qa/backend-logic/logic-390.png)
- [390px最小外发与留存正文](../qa/backend-logic/boundary-detail-390.png)

截图为本机真实Chromium/HTTP合成隔离场景。业务46项验收全部仍待执行；本轮通过的是阅读界面及数据保持检查，不是实现验证。待父review后才按明确放行发布。
