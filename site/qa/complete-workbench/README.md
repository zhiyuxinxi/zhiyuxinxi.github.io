# 完整页面工作台证据

## 最终验收权威来源

功能候选仍为 `12e44f8047351477653c4df9beae01cfd7c2ae62`。本目录的 `report.json` 是提交前本地快照：98个已访问节点、5项工作台检查，未包含随后增加的 `state:question` 与旧iframe消息隔离检查。它不是最终CI报告，不得用它证明99节点/6项检查通过。

最终依据为 [CI 37013361993](https://github.com/zhiyuxinxi/zhiyuxinxi.github.io/actions/runs/37013361993)，精确 head SHA 为上述功能候选。全部6项工作台检查通过，真实逐节点导航99项（明确含 `state:question`），39×12=468次主题路由检查通过，pageErrors为空。

- [可直接读取的最终CI摘要](ci-summary.json)：从该次完成的job日志中提取原始JSON；包含全部99个实际visited ID、6项结果及468次矩阵汇总。
- [原始job日志](https://github.com/zhiyuxinxi/zhiyuxinxi.github.io/actions/runs/37013361993/job/110858190836)：工作台结果输出时间为2026-10-02 13:39:49 UTC。
- [该次CI完整产物](https://github.com/zhiyuxinxi/zhiyuxinxi.github.io/actions/runs/37013361993/artifacts/11229395979)：其中 `complete-workbench/report.json` 为最终完整矩阵报告，另含CI截图。产物保留至2026-10-09。SHA256：`729ab19640d40c05a818b79efb1d47f15e7396b4675969e1c3cfdb1a1e181d24`。

本补充只更新证据与说明，不修改功能源码。下面的仓库截图和本地报告用于预览及历史追溯；最终通过数以以上精确CI为准。

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
