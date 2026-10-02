# 完整页面评审工作台候选

基线 main：`614dac3f8faf82da7c6b93c02b809306e4cefe8a`。仅修改 site 权威源及只读候选 CI；根镜像由发布流程维护。本候选不发布 main。

## 发现与范围

原工作台已有左右布局、真实同源 iframe、搜索、键盘树、主题对照及场景隔离，可直接复用。原47任务中38有路由，9仅流程规格；实际 Views.map 有39路由，遗漏 complete。新增五页此前统一写“交互原型”，不够准确。现有 context/usage 的真实弹层也未接入目录。

候选77个页面/功能节点覆盖39个真实路由：65个有实际预览入口（包括同页子状态和4个需从宿主操作的流程说明），7个流程规格、5个仅记录的新需求。另保留14个隔离检查场景及8个服务端责任域，共99个可选择节点。新5页及其7个子状态均标“设计预览 · 业务待实现”；已有登录、账号、购买页面保持原示例，新需求没有新增登录/支付/分享/防刷页面。

默认收起说明及高级工具，桌面整页按可用高度缩放，并提供原尺寸滚动查看；窄屏沿用抽屉目录与按宽度预览。产品内容仍在原390×844等真实视口渲染，不压缩内部布局。配色、文字、人物和业务逻辑没有重新设计。

## 优势保留与双视角检查

| 保留项 | 处理与验收 |
|---|---|
| site权威源、根目录自动镜像 | 不直接改根产品文件 |
| 用户logo、知遇测评名称、人物比例 | 原资产未改；桌面/手机实拍 |
| 无产品品牌工具栏 | 39路由×12主题检查；工作台工具不进入产品 |
| 外观仅从我的设置进入 | 保留现有产品入口与原回归 |
| 原8主题＋4历史主题及柔光双色背景 | 不改主题/ambient/product.css；全路由真实渲染接入检查 |
| 首页2主＋4次入口 | 保留六入口交互与隔离状态回归 |
| 保存认识→小尝试→观察→原依据和版本 | 原领域14项及真实浏览器回环测试 |
| 未保存内容保护 | 树切换先取得iframe状态；被阻止时不重载 |
| 中文搜索/键盘/窄屏 | 嵌套搜索、清空、上下左右/Home/End、抽屉Escape测试 |

产品挑刺：用页面数量冒充业务完成、将UI预览写成正式功能、漏掉完成回执/过程状态、切场景损失草稿、现有弹层误写完全未设计。候选分别通过成熟度标识、真实路由清单、子状态桥接、保存保护和宿主流程说明解决。

视觉挑刺：默认说明和工具占据高度，桌面只露人物与卡片上缘。候选默认收起辅助区，并用“整页适合窗口 / 原尺寸”明确选择。主题接入检查不能代表12主题所有弹层/长页状态已完成像素对比验收，工作台不显示这种完成承诺。

## 实现归属

- `handoff/routes.json`：页面与状态节点；`handoff/workbench-map.json`：业务分组与隔离场景。
- `tools/build_workbench.py`：同步上述清单到现有 `workbench-data.js`，保留原需求/事件/评审资料。
- `workbench.js`：唯一目录、搜索、键盘、真实iframe、缩放、成熟度说明。
- `experience-v4.js`：既有同源父子通信桥，仅增加受限预览状态/已有说明弹层及状态元数据。元数据不携带输入正文。
- `assessment-preview.js`：仅增加只读当前布局状态getter；不改变题源、计分、数据存储或服务。

## 验证边界

`tools/workbench_coverage.py` 对比真实 Views.map 与目录，无遗漏才通过；逐项点击节点，检查配置/过程/结果回传、重载链接、键盘搜索、桌面适合窗口/原尺寸与窄屏。

39×12主题矩阵只声明真实渲染、共享主题/背景角色、无旧顶栏与横向溢出；提供晨光全部39路由整页截图。这不是“12×所有交互状态视觉全部验收”。原产品回归、双色运动像素和导航对比测试独立保留。静态premium审计29项与基线一致，不能称strict零错误（27项动态代理无法静态识别＋2项共享textarea规则）。

## 完整目录与真实route映射

同路由的stage/action是现有页面内状态，非新增业务页。标“从页面操作”的节点只定位宿主页，按任务说明操作，不自动导入、导出、删除或生成记忆。

| 业务层级 / 节点 | ID | 真实路由 / 状态 | 成熟度 |
|---|---|---|---|
| 四个主入口 / 认识 | `home` | home | 交互示例 |
| 四个主入口 / 探索 | `explore` | explore | 交互示例 |
| 四个主入口 / 助理 | `assistant` | assistant | 交互示例 |
| 四个主入口 / 我的 | `me` | me | 交互示例 |
| 认识 · 测评与轻探索 / 专心作答 | `question` | question?id=session-demo-seed · scenario=question | 交互示例 |
| 认识 · 测评与轻探索 / 专心作答 / 保存失败与重试 | `save-failure-flow` | question?id=session-demo-seed · scenario=save-failure | 流程内状态 · 从页面操作 |
| 认识 · 测评与轻探索 / 作答检查与完成 | `review` | review?id=session-demo-seed · scenario=complete | 交互示例 |
| 认识 · 测评与轻探索 / 作答检查与完成 / 作答完成（3题示例） | `complete` | complete?id=session-demo-seed · scenario=complete | 交互示例 |
| 认识 · 测评与轻探索 / 继续与恢复 | `recovery` | —（说明节点） | 流程内状态 · 非独立页面 |
| 认识 · 测评与轻探索 / AI重置版 | `ai-reset` | ai-reset | 设计预览 · 业务待实现 |
| 认识 · 测评与轻探索 / 单因子测评 | `single-factor` | single-factor · stage=config | 设计预览 · 业务待实现 |
| 认识 · 测评与轻探索 / 单因子测评 / 作答过程布局 | `single-factor-process` | single-factor · stage=process | 设计预览 · 业务待实现 |
| 认识 · 测评与轻探索 / 单因子测评 / 结果空状态 | `single-factor-result` | single-factor · stage=result | 设计预览 · 业务待实现 |
| 认识 · 测评与轻探索 / 每日打卡 | `daily-checkin` | daily-checkin · stage=config | 设计预览 · 业务待实现 |
| 认识 · 测评与轻探索 / 每日打卡 / 作答过程布局 | `daily-checkin-process` | daily-checkin · stage=process | 设计预览 · 业务待实现 |
| 认识 · 测评与轻探索 / 每日打卡 / 结果空状态 | `daily-checkin-result` | daily-checkin · stage=result | 设计预览 · 业务待实现 |
| 认识 · 测评与轻探索 / 简化版16PF | `short-16pf` | short-16pf · stage=config | 设计预览 · 业务待实现 |
| 认识 · 测评与轻探索 / 简化版16PF / 作答过程布局 | `short-16pf-process` | short-16pf · stage=process | 设计预览 · 业务待实现 |
| 认识 · 测评与轻探索 / 简化版16PF / 结果空状态 | `short-16pf-result` | short-16pf · stage=result | 设计预览 · 业务待实现 |
| 认识 · 测评与轻探索 / 模拟性格 | `personality-sandbox` | personality-sandbox · stage=config | 设计预览 · 业务待实现 |
| 认识 · 测评与轻探索 / 模拟性格 / 假设配置结果 | `personality-sandbox-result` | personality-sandbox · stage=result | 设计预览 · 业务待实现 |
| 认识 · 测评与轻探索 / 轻量探索 | `light-suite` | simulation | 交互示例 |
| 认识 · 测评与轻探索 / 本机内容 | `content` | content | 说明 / 空状态 · 业务待实现 |
| 结果 · 报告与阅读 / 读懂一份结果 | `report` | report?id=report-sample-01 | 交互示例 |
| 结果 · 报告与阅读 / 读懂一份结果 / 报告来源与版本说明 | `report-source` | report?id=report-sample-01 · action=source-report | 交互示例 |
| 结果 · 报告与阅读 / 理解的方法 | `article` | article?id=read-traits | 交互示例 |
| 结果 · 报告与阅读 / 理解的方法 / 16个因子说明 | `factor-library` | explore · action=all-factors | 交互示例 |
| 结果 · 报告与阅读 / 放在一起看 | `compare` | compare | 说明 / 空状态 · 业务待实现 |
| 结果 · 报告与阅读 / 分享预览 | `share` | share | 交互示例 |
| 探索 · 生活问题与记录 / 了解这项探索 | `assessment-detail` | topic?id=work-choice | 交互示例 |
| 探索 · 生活问题与记录 / 了解这项探索 / 表达与相处 · 说明 | `topic-relationships` | topic?id=relationships | 交互示例 |
| 探索 · 生活问题与记录 / 了解这项探索 / 城市与生活 · 说明 | `topic-city-choice` | topic?id=city-choice | 交互示例 |
| 探索 · 生活问题与记录 / 了解这项探索 / 学习与动力 · 说明 | `topic-learning` | topic?id=learning | 交互示例 |
| 探索 · 生活问题与记录 / 了解这项探索 / 与自己相处 · 说明 | `topic-self-space` | topic?id=self-space | 交互示例 |
| 探索 · 生活问题与记录 / 专题整理工作区 | `topic-workspace` | topic-workspace?topic=work-choice | 交互示例 |
| 探索 · 生活问题与记录 / 专题整理工作区 / 表达与相处 · 整理 | `workspace-relationships` | topic-workspace?topic=relationships | 交互示例 |
| 探索 · 生活问题与记录 / 专题整理工作区 / 城市与生活 · 整理 | `workspace-city-choice` | topic-workspace?topic=city-choice | 交互示例 |
| 探索 · 生活问题与记录 / 专题整理工作区 / 学习与动力 · 整理 | `workspace-learning` | topic-workspace?topic=learning | 交互示例 |
| 探索 · 生活问题与记录 / 专题整理工作区 / 与自己相处 · 整理 | `workspace-self-space` | topic-workspace?topic=self-space | 交互示例 |
| 探索 · 生活问题与记录 / 专题整理工作区 / 已保存整理与版本 | `workspace-saved` | topic-workspace?topic=work-choice&id=topic-note-demo-v2 · scenario=topic-record | 交互示例 |
| 探索 · 生活问题与记录 / 本人观察 | `journal` | journal | 交互示例 |
| 探索 · 生活问题与记录 / 测评与记录 | `records` | records | 交互示例 |
| 探索 · 生活问题与记录 / 我的小尝试 | `actions` | actions | 交互示例 |
| 探索 · 生活问题与记录 / 小尝试与回看 | `action-detail` | action-detail?id=action-demo-v2 · scenario=ongoing-action | 交互示例 |
| 探索 · 生活问题与记录 / 小尝试与回看 / 已留下观察与原依据 | `action-observed` | action-detail?id=action-demo-v2 · scenario=action-review | 交互示例 |
| 助理 · 对话与长期理解 / 聊过的话题 | `conversations` | conversations · scenario=history | 交互示例 |
| 助理 · 对话与长期理解 / 对话正文 | `conversation` | conversation?id=conversation-demo-history · scenario=history | 交互示例 |
| 助理 · 对话与长期理解 / 本次引用 | `context` | assistant · action=context | 交互示例 · 服务待实现 |
| 助理 · 对话与长期理解 / AI用量 | `usage` | assistant · action=quota | 交互示例 · 服务待实现 |
| 助理 · 对话与长期理解 / 按需解析 | `analysis` | —（说明节点） | 流程规格 · 待实现 |
| 助理 · 对话与长期理解 / 正在认识的自己 | `portrait` | portrait | 交互示例 |
| 助理 · 对话与长期理解 / 助理记忆 | `memories` | memories | 交互示例 |
| 助理 · 对话与长期理解 / 助理记忆 / 记忆候选、确认与来源 | `memory-flow` | memories | 流程内状态 · 从页面操作 |
| 助理 · 对话与长期理解 / 生活空间 | `life-spaces` | —（说明节点） | 流程规格 · 待实现 |
| 助理 · 对话与长期理解 / 助理技能 | `skills` | —（说明节点） | 流程规格 · 待实现 |
| 我的 · 外观与资料管理 / 偏好 | `settings` | settings | 交互示例 |
| 我的 · 外观与资料管理 / 偏好 / 密度、动态与字号 | `settings-preferences` | settings · action=v3-preferences | 交互示例 |
| 我的 · 外观与资料管理 / 主题与形象 | `appearance` | appearance | 交互示例 |
| 我的 · 外观与资料管理 / 隐私与引用 | `privacy` | privacy | 交互示例 |
| 我的 · 外观与资料管理 / 我的数据 | `data` | data | 交互示例 |
| 我的 · 外观与资料管理 / 我的数据 / 导入、导出与范围选择 | `data-transfer-flow` | data | 流程内状态 · 从页面操作 |
| 我的 · 外观与资料管理 / 我的数据 / 删除确认与失败保护 | `data-delete-flow` | data | 流程内状态 · 从页面操作 |
| 我的 · 外观与资料管理 / 备份与冲突 | `sync` | —（说明节点） | 流程规格 · 待实现 |
| 我的 · 外观与资料管理 / 轻提醒 | `reminders` | —（说明节点） | 流程规格 · 待实现 |
| 我的 · 外观与资料管理 / 通知 | `notifications` | —（说明节点） | 流程规格 · 待实现 |
| 我的 · 外观与资料管理 / 帮助与反馈 | `support` | support | 交互示例 |
| 现有身份与会员示例 / 登录与注册 | `auth` | auth | 交互示例 |
| 现有身份与会员示例 / 账号与安全 | `account` | account | 交互示例 |
| 现有身份与会员示例 / 使用与会员 | `membership` | membership | 交互示例 |
| 现有身份与会员示例 / 购买确认 | `checkout` | checkout | 交互示例 |
| 现有身份与会员示例 / 订单记录 | `orders` | orders · scenario=paid-annual | 交互示例 |
| 现有身份与会员示例 / 原单核验与售后 | `order` | order?id=DEMO-ANNUAL-001 · scenario=paid-annual | 交互示例 |
| 最新需求 · 仅记录 / 登录方式与流程 | `login-requirement` | —（说明节点） | 需求已记录 · 未设计/开发 |
| 最新需求 · 仅记录 / 手机号登录 | `phone-requirement` | —（说明节点） | 需求已记录 · 未设计/开发 |
| 最新需求 · 仅记录 / 微信 / 支付宝支付 | `payments-requirement` | —（说明节点） | 需求已记录 · 未设计/开发 |
| 最新需求 · 仅记录 / 朋友圈分享 | `moments-requirement` | —（说明节点） | 需求已记录 · 未设计/开发 |
| 最新需求 · 仅记录 / 防刷与服务端校验 | `abuse-requirement` | —（说明节点） | 需求已记录 · 未设计/开发 |
| 关键状态检查 / 首次打开 | `state:default` | home | 隔离场景演示 |
| 关键状态检查 / 继续答题 | `state:resume` | home · scenario=resume | 隔离场景演示 |
| 关键状态检查 / 答卷 + 小尝试并存 | `state:combined` | home · scenario=combined | 隔离场景演示 |
| 关键状态检查 / 答案保存失败 | `state:save-failure` | question?id=session-demo-seed · scenario=save-failure | 隔离场景演示 |
| 关键状态检查 / 已完成体验 | `state:complete` | home · scenario=complete | 隔离场景演示 |
| 关键状态检查 / 混合记录与分类 | `state:mixed-records` | me · scenario=mixed-records | 隔离场景演示 |
| 关键状态检查 / 已保存专题 | `state:topic-record` | topic-workspace?topic=work-choice&id=topic-note-demo-v2 · scenario=topic-record | 隔离场景演示 |
| 关键状态检查 / 进行中的小尝试 | `state:ongoing-action` | action-detail?id=action-demo-v2 · scenario=ongoing-action | 隔离场景演示 |
| 关键状态检查 / 已留过真实观察 | `state:action-review` | action-detail?id=action-demo-v2 · scenario=action-review | 隔离场景演示 |
| 关键状态检查 / 引用后等待登录 | `state:source-login` | assistant · scenario=source-login | 隔离场景演示 |
| 关键状态检查 / 共用次数已用尽 | `state:quota` | assistant · scenario=quota | 隔离场景演示 |
| 关键状态检查 / 原历史对话 | `state:history` | conversation?id=conversation-demo-history · scenario=history | 隔离场景演示 |
| 关键状态检查 / 原年方案订单 | `state:paid-annual` | order?id=DEMO-ANNUAL-001 · scenario=paid-annual | 隔离场景演示 |
| 服务端责任域 / 身份与空间 | `backend:BR-001` | —（说明节点） | 服务端责任规格 · 未接入 |
| 服务端责任域 / AI请求与共用额度 | `backend:BR-002` | —（说明节点） | 服务端责任规格 · 未接入 |
| 服务端责任域 / 原单与权益 | `backend:BR-003` | —（说明节点） | 服务端责任规格 · 未接入 |
| 服务端责任域 / 内容发布资格 | `backend:BR-004` | —（说明节点） | 服务端责任规格 · 未接入 |
| 服务端责任域 / 服务消息与反馈 | `backend:BR-005` | —（说明节点） | 服务端责任规格 · 未接入 |
| 服务端责任域 / 数据与注销请求 | `backend:BR-006` | —（说明节点） | 服务端责任规格 · 未接入 |
| 服务端责任域 / 运行与成本 | `backend:BR-007` | —（说明节点） | 服务端责任规格 · 未接入 |
| 服务端责任域 / 配置与审计 | `backend:BR-008` | —（说明节点） | 服务端责任规格 · 未接入 |

| 关键状态检查 / 正在作答 · 三题示例 | `state:question` | question?id=session-demo-seed · scenario=question | 隔离场景演示 |

## 独立终评后的定向导航修复

终评发现普通route回传匹配排除了所有parentId节点，导致实际新答卷完成后的新ID无法定位complete，实际进入非默认专题也回退到默认专题名称。改为：先在普通页面候选中精确匹配route（排除弹层action、过程/结果stage、需从宿主操作的flow歧义），再匹配同base的规范父页；同base只有一个普通子页时允许匹配该子页，如complete。

新增真实浏览器路径：从首页开始新答卷，实际选完3题并完成，断言动态sessionId保留、左树complete选中和标题同步；从探索实际点击4个非默认专题，逐一断言真实route、子节点与标题同步。不是直接点击seed树节点。产品页面、布局、主题、业务均未改动。旧98/5本地报告不是最终结果；见QA说明中的精确CI权威来源及定向shell-report。

真实完成路径的实拍还揭示缩放iframe外框会被浏览器焦点自动滚动（外框scrollTop=106、scrollLeft=19，iframe自身scrollY=0），裁掉手机顶端。仅将外框overflow从hidden改为clip，禁止遮罩成为滚动容器；iframe内正常内容滚动与视口尺寸不变。两个真实路径均断言外框scrollTop/scrollLeft=0。
