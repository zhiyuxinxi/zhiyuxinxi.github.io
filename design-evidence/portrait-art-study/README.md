# 完整画像候选证据

运行页面：site/review/portrait-art-study/index.html；匿名不等子树：?structure=7。未发布。

390截图来自Chromium 390px视口、DPR2，交付图片等比缩至1x。1440为桌面全页。真实8主题及独立四侧面不变；匿名7主题名称仅说明结构类型。

interaction-regression.json：15状态、4拓扑、40匿名节点可达；拖动、CDP双指缩放、语义缩放、焦点、浮层关闭恢复、主题切换、持久Canvas、减弱动态。该轮之后仅修改匿名概览名称和编号，再由targeted-report.json验证最终8/7整图标签、实际渲染曲线、装饰避让、A/B与深6浮层。

targeted-report.json：最终8/7完整拓扑及概览缩略渲染路径，均无采样交叉、扇区越界或向内折返。第一轮屏幕坐标误用于世界坐标扇区检查，校正坐标原点后复核通过；没有因此改变被检验的几何。每曲线120段采样，无中心排除区。

static-audit.json：9个actionless-button静态提示，因按钮在外部JS绑定，实际操作回归已执行；不宣称静态严格审计通过。Select/Listbox继续原生控件所有权。

限制：Chromium模拟，未验证实体设备、Safari/Firefox或屏幕阅读器；其他主题未逐一进行新素材美术验收。中心暖色光球较醒目、末端点节奏与稀疏卷枝仍待独立审美复核。测试通过不代表美术验收或获奖认证。
