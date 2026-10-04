# 认识首页与探索目录候选

从当前main cf3737ce01c19df9832dde8d20609105deedcea7建立独立分支。只修改site/源，不镜像根目录、不部署；画像图和研究分支未合入。

## 实际修改

首页原版说明略增日常情境用途，人物比例、同框版本切换、四副入口保持。探索增加不可点击的简短介绍，8张卡统一横矩形、语义图标、问题标题及用途；分类为主，找主题默认收起。

公开目录增加keywords/aliases。NFKC、首尾空白/连续空白/大小写归一化；完整短查询按标题或别名完全匹配→标题包含→关键词/别名包含排序，同档保持目录序。分类与搜索取交集；不分词、不纠错、不调用AI，不索引私人资料。查询只在内存，返回保留、刷新清空、不写URL或持久化、不上传。清空立即回焦点；输入法组合时保留原结果，结束更新且不重建输入节点。

## 尚未完成

AI重置版具体改写说明尚缺准确题库来源。当前主站契约仍将题文列为待定；未能核实近四周/行为锚点与该版本的对应，故候选仅保留准备中说明。拿到真实设计来源后再完善，不能视为该项已完成；没有编造更准确、诊断或实时AI能力。

## 已执行证据

- report.json：320/390/1440×12主题共36组合通过；首页切换主按钮位置变化0px；卡片非竖长、无水平溢出，卡片正文/分类最低对比度7.61:1；7组关键词/别名/空结果、中文组合输入、清空焦点、分类交集、键盘、查询不落盘、页面载入后离线无搜索请求、背景连续及减弱动态通过。无JS异常。
- product-regression.json：现行43路由×12主题、八专题本机保存闭环、首页版本、工作台等全部通过。
- premium-audit.json：严格静态审计失败29项；audit-comparison.json确认与main基线规则/文件计数一致，没有新增。模板委派按钮和统一CSS textarea规则未被脚本识别，不以此宣称严格通过。
- design-lint.log：DESIGN.md 0 errors，3个既有token警告。
- viewport文件为390px实际首屏；其余为完整页面截图，固定底栏出现在视口位置，不代表文档中插入底栏。

旧manifest的10个命令已在隔离副本执行，精确退出状态见configured-commands.json：themes、runtime（18项）、recordContract（14项）、previewUI、navigation、development、backendLogic通过。visual失败：旧首页/助理选择器与现行main结构、旧独立页夹具启动方式不兼容，完整日志保留；不把失败删除或改称通过。motion在创建录像上下文时因Playwright ffmpeg缺失失败。workbench的8项外框检查已通过，随后全主题路由扫描超过360秒超时，不宣称该脚本全量通过；现行product_structure_review的43×12独立矩阵已通过。

补充scene-contrast.json用浏览器计算后的两色端点与101个混色样本检查新增背景文字角色，最低5.07:1；属于角色数值检查，不是全屏像素或无障碍认证。

## 边界

浏览器已载入静态资源后断网可用；未增加网页冷启动离线缓存。未验证实体手机软键盘、Safari或全辅助技术。此候选待独立视觉审阅，未发布。

重放：CHROMIUM_PATH=/usr/bin/chromium python site/tools/home_explore_review.py site /tmp/home-explore-review；现行整体回归使用site/tools/product_structure_review.py。
