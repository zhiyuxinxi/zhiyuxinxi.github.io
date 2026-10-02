# 双主色柔光候选：真实浏览器证据

被验证的实现提交：`aaeb53e245c583c72ddc55acb37c2915f9675224`。本目录全部来自隔离的合成场景；不含私有历史图片、真实个人记录或新业务服务。

## 原速运动与报告

- [原速录像：33.88秒，覆盖完整32秒面积周期](natural-32-seconds.webm)
- [像素面积、对比、深页与连续性完整报告](report.json)
- [业务浏览器回归：18通过](hosted-smoke.json)
- [Premium原始审计](premium-audit.json) 与 [main基线](premium-audit-baseline.json)：29条相同识别限制，新增0；不宣称strict通过。

相位8秒约84/16，16秒约50/50，24秒约16/84。方向独立演化；这三个时刻并非固定方向模板。优势区域按完整背景像素分类，不能当作卡片遮挡后的可见纯色面积。

## 八主题首页：两端及中间

|主题|A占多数|中间|B占多数|
|---|---|---|---|
|晨光|[8秒](sunrise-home-8.png)|[16秒](sunrise-home-16.png)|[24秒](sunrise-home-24.png)|
|糖霜|[8秒](candy-home-8.png)|[16秒](candy-home-16.png)|[24秒](candy-home-24.png)|
|莓果|[8秒](berry-home-8.png)|[16秒](berry-home-16.png)|[24秒](berry-home-24.png)|
|青柠|[8秒](lime-home-8.png)|[16秒](lime-home-16.png)|[24秒](lime-home-24.png)|
|流光|[8秒](aurora-home-8.png)|[16秒](aurora-home-16.png)|[24秒](aurora-home-24.png)|
|海盐|[8秒](sea-home-8.png)|[16秒](sea-home-16.png)|[24秒](sea-home-24.png)|
|夜航|[8秒](nebula-home-8.png)|[16秒](nebula-home-16.png)|[24秒](nebula-home-24.png)|
|琥珀|[8秒](amber-home-8.png)|[16秒](amber-home-16.png)|[24秒](amber-home-24.png)|

## 四主页面（晨光与夜航）

|主题|认识|探索|助理|我的|
|---|---|---|---|---|
|晨光|[认识](sunrise-home-24.png)|[探索](sunrise-explore-24.png)|[助理](sunrise-assistant-24.png)|[我的](sunrise-me-24.png)|
|夜航|[认识](nebula-home-24.png)|[探索](nebula-explore-24.png)|[助理](nebula-assistant-24.png)|[我的](nebula-me-24.png)|

其余主题四主页面的8/16/24秒截图均在同目录，按“主题-路由-秒数.png”命名。

## 子页、阅读、输入与答题

- [四个新子页与AI说明的浅／深色窄屏图](subpages/)
- [长文阅读](reading-sunrise-article.png) · [报告章节](reading-sunrise-report.png)
- [输入焦点](input-sunrise.png) · [深色输入](input-nebula.png) · [窄屏大字输入](large-input-amber.png)
- [来源弹窗](modal-sunrise.png) · [深色弹窗](modal-nebula.png)
- [浅色答题](question-sunrise.png) · [深色答题](question-nebula.png)
- [320px设置](narrow-settings.png) · [320px主题页](narrow-appearance.png)
- [减少动态静态帧](reduced.png) · [稍后相同帧](reduced-later.png)

浏览器为本机Chromium；未宣称Safari、真机软键盘或完整辅助技术认证。数值通过不替代独立视觉review。本次证据提交不修改运行时、不部署。
