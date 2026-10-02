# 完整页面工作台证据

> **证据版本说明：** 仓库 `report.json` 是较早的本地快照（98个visited、5项工作台检查），不是最终CI结果。上一候选 `12e44f8` 的 [精确CI 37013361993](https://github.com/zhiyuxinxi/zhiyuxinxi.github.io/actions/runs/37013361993) 已通过99节点、6项工作台检查与468次主题路由检查；[原始CI摘要及全部99个visited ID](https://github.com/zhiyuxinxi/zhiyuxinxi.github.io/blob/2e06f42aef38c4b30c58facfff34d1b93e96b3d4/site/qa/complete-workbench/ci-summary.json) 可直接读取。
>
> 本次路由同步定向修复增加“全新答卷完成”和“探索真实进入4个非默认专题”两项测试；本地 [shell-report.json](shell-report.json) 单独记录8项工作台检查，不覆盖或冒充完整主题矩阵。最终以对应精确修复提交的CI产物为权威。
>
> 桌面“整页适合窗口”缩放完整手机视口；窄屏按宽度缩放，页面通过滚动查看，不声称窄屏能同时看到整张手机。

基线 main：614dac3f8faf82da7c6b93c02b809306e4cefe8a。全部为本机HTTP、Chromium与隔离合成数据；不是生产AI/计分/账号/支付验证。

- [1480×1100 左树＋整页预览](layout-1480.png)
- [1188×761 小桌面整页](layout-1188.png)
- [1188 原尺寸滚动查看](actual-1188.png)
- [390 窄屏预览](layout-390.png) / [展开功能树](mobile-tree.png)
- `page-*.png`：全部39个真实路由的晨光整页截图。
- [完整树与route映射](../../review/complete-workbench-review.md)
- [工作台与全路由接入报告](report.json)
- [premium静态审计](static-audit.json)：29项基线问题保持，无新增，不声称strict通过。

报告范围严格区分：全路由×12主题检查真实渲染、共享背景/主题角色、无产品旧顶栏与横向溢出；不冒充全部业务状态的视觉/对比度验收。产品核心流程、柔光动画、六入口和导航对比使用原有独立测试。

候选CI会重新生成当前精确提交的证据；本地录像因ffmpeg下载被策略拒绝，完整运动录像验证交由只读CI执行，不改动限制。
