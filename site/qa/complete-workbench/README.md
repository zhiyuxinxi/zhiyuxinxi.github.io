# 完整页面工作台证据

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
