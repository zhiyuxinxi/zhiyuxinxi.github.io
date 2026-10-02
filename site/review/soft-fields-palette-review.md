# 主色改动复核：明确区分保留与重配

实现仍固定为 `aaeb53e245c583c72ddc55acb37c2915f9675224`，本文件只说明问题，不改运行时。

## 范围纠正

八主题名称、数量与业务状态保留，不等于原主色保留。当前候选field-a/b均为实施者手选；不是原颜色的算法映射，也没有新的用户配色授权。旧colors元数据保留而运行时scene/field换色，造成双源表达不一致。不能向用户称“原色未变”。本轮用户明确授权背景面积/方向与控件适配，应优先保留原场景锚点，通过承托表面与文字解决对比。

## 每主题对照与未实施建议

|主题|main原scene-a/b/c|当前候选field-a/b|候选选择依据与偏移|建议原色双锚点（待review，未实施）|
|---|---|---|---|---|
|晨光奶油|#fff19d / #ff875d / #ffd586|#f5b36d / #ef8d92|手选较浓蜜金与珊瑚粉；偏离原黄橙关系。|#fff19d / #ff875d|
|糖霜星云|#ffeda0 / #ff74b2 / #ffc77c|#efa0d4 / #ffc676|手选柔粉与杏金；粉色由鲜粉偏向紫粉。|#ffeda0 / #ff74b2|
|莓果汽泡|#ffabd6 / #c594ff / #8cafff|#c7a0ee / #ed94b4|手选柔紫与莓粉；原冰蓝方向退出主色。|#ffabd6 / #c594ff|
|青柠薄雾|#edff99 / #88edbd / #93e0ff|#c7dc72 / #71cdb4|手选偏深黄绿与薄荷；原轻亮感降低。|#edff99 / #88edbd|
|流光天幕|#c3dfff / #e3b6ff / #ffcfe5|#a6baef / #d1a5d0|手选较深雾蓝与烟紫；整体明度下降。|#c3dfff / #e3b6ff|
|海盐晴蓝|#b3f2ff / #7fdfd0 / #e2ffa9|#85c6e9 / #8cd7cb|手选较深晴蓝与青绿；原浅蓝/薄绿关系改变。|#b3f2ff / #7fdfd0|
|夜航星云|#6254b8 / #3e88b5 / #8c6ca1|#152c5e / #4a2b68|为深色文字/表面体系手选深蓝与暗紫；明显降低场景亮度并移除原蓝青。|#6254b8 / #3e88b5|
|琥珀潮汐|#c27978 / #b88961 / #dfad73|#643049 / #925033|为浅文字对比手选梅红与深赭；后续再收暗亮端。原玫瑰/流金关系改变。|#c27978 / #dfad73|

以上候选选择只是实施者的视觉假设，不能当作用户决策。琥珀建议原a/c突出玫瑰与流金，其余建议原a/b；未选的第三色可作为中间/材料角色参考，不新增第三片主色场。实际采用哪一对仍待独立像素review。

## 实际像素观察

查看main已有首页证据与候选截图：晨光由奶黄/橙色环境变为浓金/粉色环境；夜航由较亮紫蓝、青色强调变为深蓝/暗紫、浅紫强调。这是明显视觉身份改动，不是单纯透明度或承托面适配。候选整体染色、阅读/输入实底与对比验证有价值，但不能据此批准未授权换色。

## 32秒原速录像与136秒方向关键帧

- [原速33.88秒录像](../qa/soft-fields/natural-32-seconds.webm)
- [完整8主题×16相位像素报告](../qa/soft-fields/report.json)

以下均为实际浏览器截图，用Ambient.sample在同一确定性时间线上取样；不是136秒连续录像。内容临时隐藏仅用于看清完整色场。

|主题|0秒|32秒|56秒|88秒|120秒|136秒|
|---|---|---|---|---|---|---|
|晨光奶油|[0秒](../qa/soft-fields/field-sunrise-0.png)|[32秒](../qa/soft-fields/field-sunrise-32.png)|[56秒](../qa/soft-fields/field-sunrise-56.png)|[88秒](../qa/soft-fields/field-sunrise-88.png)|[120秒](../qa/soft-fields/field-sunrise-120.png)|[136秒](../qa/soft-fields/field-sunrise-136.png)|
|糖霜星云|[0秒](../qa/soft-fields/field-candy-0.png)|[32秒](../qa/soft-fields/field-candy-32.png)|[56秒](../qa/soft-fields/field-candy-56.png)|[88秒](../qa/soft-fields/field-candy-88.png)|[120秒](../qa/soft-fields/field-candy-120.png)|[136秒](../qa/soft-fields/field-candy-136.png)|
|莓果汽泡|[0秒](../qa/soft-fields/field-berry-0.png)|[32秒](../qa/soft-fields/field-berry-32.png)|[56秒](../qa/soft-fields/field-berry-56.png)|[88秒](../qa/soft-fields/field-berry-88.png)|[120秒](../qa/soft-fields/field-berry-120.png)|[136秒](../qa/soft-fields/field-berry-136.png)|
|青柠薄雾|[0秒](../qa/soft-fields/field-lime-0.png)|[32秒](../qa/soft-fields/field-lime-32.png)|[56秒](../qa/soft-fields/field-lime-56.png)|[88秒](../qa/soft-fields/field-lime-88.png)|[120秒](../qa/soft-fields/field-lime-120.png)|[136秒](../qa/soft-fields/field-lime-136.png)|
|流光天幕|[0秒](../qa/soft-fields/field-aurora-0.png)|[32秒](../qa/soft-fields/field-aurora-32.png)|[56秒](../qa/soft-fields/field-aurora-56.png)|[88秒](../qa/soft-fields/field-aurora-88.png)|[120秒](../qa/soft-fields/field-aurora-120.png)|[136秒](../qa/soft-fields/field-aurora-136.png)|
|海盐晴蓝|[0秒](../qa/soft-fields/field-sea-0.png)|[32秒](../qa/soft-fields/field-sea-32.png)|[56秒](../qa/soft-fields/field-sea-56.png)|[88秒](../qa/soft-fields/field-sea-88.png)|[120秒](../qa/soft-fields/field-sea-120.png)|[136秒](../qa/soft-fields/field-sea-136.png)|
|夜航星云|[0秒](../qa/soft-fields/field-nebula-0.png)|[32秒](../qa/soft-fields/field-nebula-32.png)|[56秒](../qa/soft-fields/field-nebula-56.png)|[88秒](../qa/soft-fields/field-nebula-88.png)|[120秒](../qa/soft-fields/field-nebula-120.png)|[136秒](../qa/soft-fields/field-nebula-136.png)|
|琥珀潮汐|[0秒](../qa/soft-fields/field-amber-0.png)|[32秒](../qa/soft-fields/field-amber-32.png)|[56秒](../qa/soft-fields/field-amber-56.png)|[88秒](../qa/soft-fields/field-amber-88.png)|[120秒](../qa/soft-fields/field-amber-120.png)|[136秒](../qa/soft-fields/field-amber-136.png)|

青柠A主色优势区域质心（归一化）：0秒(0.246,0.508)，32秒(0.249,0.479)，56秒(0.075,0.465)，88秒(0.159,0.773)，120秒(0.681,0.116)，136秒(0.470,0.570)。0/32秒同为约50%面积且构图相近，短窗不足以显示全部方向变化。56/88/120秒均接近16%面积但少数主色分别落在左侧、左下、右上；136秒多数主色进一步换向。这支持“方向不是固定单轴”，不等于证明运动已自然好看。

下一步：等待独立图片review；在此之前不重配、不重跑整套、不部署。
