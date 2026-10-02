# 阶段一页面说明整合：恢复候选

日期：2026-10-02。候选分支：`design/zhiyu-page-handoff-recovery`。仅供独立 review，未合并 main、未部署，下一阶段无界面架构分析未开始。

## 来源与范围

- main 核实为 `afd1bf2af36ef130c8636c137b131183b3ffab54`。
- 续接恢复快照 `ef09e1ded5ea8cb4cb1da04c0c86f32737891f31`，保留已有说明整合与原工作台。
- 公开审计来源：`design/zhiyu-audit-data` 固定提交 `5f2d14e153ed166c015de363fbfcbade2706f748`，正常 git fetch 获取。
- ZIP：355021 bytes，SHA256 `dfc65d26f350967ec9cd3bf6e855ecae855d058ea1141c71f1d1096dad77f2ac`。未使用 Library，未读取或发布 private 溯源版。
- `tools/build_development_handoff.py` 重新生成185个公开分块，与快照分块逐字节相同。`handoff/development/manifest.json` 保留分块字节数及 SHA256，运行时只读取公开静态资源。

## 交付行为

逐页开发说明覆盖39个真实route、299组按钮、146个代表性状态；业务目的、状态、输入、handler、本机实体、计划云端/API、隐私权限、异常恢复、关联验收与待决按区折叠。新增实体引用核查展示，保留源码证据链接的公开仓库及固定提交约束。页面、共享契约、历史动作按需加载，初始真实页面预览不加载说明数据。中文搜索、清空焦点、查询恢复、失败重试和过期响应保护均已实测。

历史对账覆盖119职责/551动作，另有后台22职责/66动作。价值裁决14保留、96合并、8建议删除、1待确认，与当前承载状态分开筛选。15项真实遗漏中13项应并入现有宿主、2项建议删除；13不是全部未完成项。原ID/动作搜索、分页、原动作展开与去向跳转保留。没有因历史数量恢复空页面，也没有实现13项真实业务缺口。

全部题库随安装默认本地、首启不下载是已确认要求，当前正式题源未提供。用户条件式提出的本地计分、本地报告、会员云存仍待确认；微信/支付宝/手机号、分享和防刷仅记录。真实业务出网仍为0；说明面板读取同源JSON不属于业务服务接入。

修复隐藏iframe的0×0初始视口导致Canvas尺寸为NaN的问题：零尺寸时延迟像素分配，API继续初始化；显示后原resize监听正常绘制。没有吞异常、重建产品页面或清空本机资料。实际产品源码仅此3行守卫变化。

发布工作流未来镜像根目录时需携带 `development-review.js`，已补白名单，并将新增说明测试加入发布验证。此修改未触发发布。移除已被真实数据取代的 `development-review.pending.json` 空占位；未删除任何原历史职责或动作数据。参考schema仍保留，但运行时权威数据为上述审计分块。

## 本次真实验证

环境：本机 Chromium 151.0.7922.173、Playwright 1.62.0，真实本地HTTP；合成隔离数据。

|检查|结果|证据|
|---|---|---|
|说明数据完整性、安全、39页加载、搜索/IME、历史筛选跳转、窄屏、失败重试、过期响应、零尺寸恢复与静态请求范围|13/13，pageErrors=[]|[说明报告](../qa/development-review/report.json)|
|原工作台路由/99节点、实际页面内跳转、子状态、键盘搜索、陈旧消息、fit/原尺寸、390px抽屉|8/8，pageErrors=[]|[工作台报告](../qa/complete-workbench/shell-report.json)|
|原型完整HTTP业务回归|18/18；含8主题×6页面|[HTTP报告](../qa/handoff-recovery/hosted-smoke.json)、[主题矩阵](../qa/handoff-recovery/hosted-theme-matrix.json)|
|视觉布局|40/40|[布局结果](../qa/handoff-recovery/design-candidate-snapshot-results.json)|
|六入口UI|9/9|[六入口结果](../qa/handoff-recovery/six-paths-ui-results.json)|
|12主题导航对比|12/12|[导航结果](../qa/handoff-recovery/nav-contrast-report.json)|
|主题生成、77节点工作台生成、记录领域契约、3个修改JS语法、git diff --check|通过|对应项目命令实际运行，生成源码未漂移|

命令：`CHROMIUM_PATH=/usr/bin/chromium python site/tools/development_review_test.py site`；`CHROMIUM_PATH=/usr/bin/chromium WORKBENCH_SHELL_ONLY=1 python site/tools/workbench_coverage.py site`；`python site/tools/build_workbench.py`；`python site/tools/build_themes.py`；`node site/tools/record_loop_contract.mjs site`；浏览器命令同环境变量执行 `hosted_smoke.py`、`design_snapshots.py`、`six_paths_ui.py`、`nav_contrast.py`，参数均为 `site`。

HTTP回归首次17/18，旧断言同步读取已变为异步的规格说明；更新等待真实文本后完整重跑18/18。过期响应测试首次误把树选页后的默认预览当说明页；按真实流程切回说明后重跑13/13。这两处是测试同步/流程修正，未改变既有树导航行为。

## 真实截图

- [桌面逐页说明](../qa/development-review/desktop-development.png)
- [桌面历史13项待补筛选](../qa/development-review/desktop-history-gaps.png)
- [390px说明](../qa/development-review/narrow-development.png)
- [390px输入契约展开](../qa/development-review/narrow-input-contract.png)
- [390px历史对账](../qa/development-review/narrow-history.png)
- [1188px工作台fit](../qa/complete-workbench/layout-1188.png)、[原尺寸](../qa/complete-workbench/actual-1188.png)、[窄屏树抽屉](../qa/complete-workbench/mobile-tree.png)

上述说明/工作台截图为本次运行实拍，已查看桌面历史与窄屏说明像素。扩大回归仅另存本次JSON结果，其他既有截图目录不作为本次像素证据。

## 限制与review门禁

Premium严格静态扫描29项，main基线同样29项，逐项完全相同，新增说明代码0项。主要为既有动态模板按钮/共享textarea样式未被通用扫描器识别；不将严格扫描称为通过，也未为消除扫描计数改写产品。见[静态报告及基线对照](../qa/handoff-recovery/premium-audit.json)。

`tidal_motion.py` 本次未完成：Playwright录像依赖FFmpeg不存在，官方安装命令下载返回403 Domain forbidden；停止该下载路径，未绕限制。既有背景视觉方案未改，新增零尺寸恢复已由专项真实浏览器覆盖；本次不宣称32秒录像、468个全主题route矩阵或真机/完整辅助技术矩阵重验。

这是一阶段说明候选，不是APP业务实现，也不是正式题库、计分常模、账号、支付、同步或AI验收。请父线程独立审核候选SHA、实际截图、数据口径与发布资产后另行放行；main保持原基线。


## 父review放行后的发布收尾补充

父线程独立review通过后，修正shell-only报告scope及生成器：仅8项工作台壳回归，不声称重跑468矩阵。说明测试使用CI已安装的Playwright浏览器，`CHROMIUM_PATH`仅为显式本机覆盖。首轮正式发布成功后，定向实际点击检查又发现隐藏期间算出的极小外框fit比例可能保留；切回实际页面时增加下一帧fit重算，并在contract/history/review三种直达路径恢复后实际点击探索及核树同步。此修复不改产品路由、数据和背景算法。最终发布及公网只读核验以父线程收到的Actions链接与提交SHA为准；以上“候选未部署”是最初交付时点记录。
