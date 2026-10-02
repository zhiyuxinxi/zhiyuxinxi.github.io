# 底栏选中态：精准修复验证

修复experience-v2.css中.theme-peach/.theme-blue规则覆盖共享选中图标底色的问题。product.css的共享选择器改为body[data-theme-mode] .nav button.active .navicon，统一使用primary底色与on-primary图标，不重配任何主题或页面。

定向验证12主题×4选中标签×2端点=96状态，384组图标/文字：全部通过。选中背景及前景分别与运行时primary/on-primary计算值严格相等；未选中图标保持透明底。截图背景实际取像素测得全部图标最低7.331，选中图标最低7.486，标签最低7.144。

- [完整计算样式与像素报告](report.json)
- [杏桃首页24秒](peach-home-24.png) / [杏桃助理24秒](peach-assistant-24.png)
- [海盐晴空首页24秒](blue-home-24.png) / [海盐晴空助理24秒](blue-assistant-24.png)

|主题|认识选中|探索选中|助理选中|我的选中|
|---|---|---|---|---|
|晨光奶油|[home](sunrise-home-24.png)|[explore](sunrise-explore-24.png)|[assistant](sunrise-assistant-24.png)|[me](sunrise-me-24.png)|
|糖霜星云|[home](candy-home-24.png)|[explore](candy-explore-24.png)|[assistant](candy-assistant-24.png)|[me](candy-me-24.png)|
|莓果汽泡|[home](berry-home-24.png)|[explore](berry-explore-24.png)|[assistant](berry-assistant-24.png)|[me](berry-me-24.png)|
|青柠薄雾|[home](lime-home-24.png)|[explore](lime-explore-24.png)|[assistant](lime-assistant-24.png)|[me](lime-me-24.png)|
|流光天幕|[home](aurora-home-24.png)|[explore](aurora-explore-24.png)|[assistant](aurora-assistant-24.png)|[me](aurora-me-24.png)|
|海盐晴蓝|[home](sea-home-24.png)|[explore](sea-explore-24.png)|[assistant](sea-assistant-24.png)|[me](sea-me-24.png)|
|夜航星云|[home](nebula-home-24.png)|[explore](nebula-explore-24.png)|[assistant](nebula-assistant-24.png)|[me](nebula-me-24.png)|
|琥珀潮汐|[home](amber-home-24.png)|[explore](amber-explore-24.png)|[assistant](amber-assistant-24.png)|[me](amber-me-24.png)|
|青屿晨光|[home](green-home-24.png)|[explore](green-explore-24.png)|[assistant](green-assistant-24.png)|[me](green-me-24.png)|
|杏桃晚风|[home](peach-home-24.png)|[explore](peach-explore-24.png)|[assistant](peach-assistant-24.png)|[me](peach-me-24.png)|
|海盐晴空|[home](blue-home-24.png)|[explore](blue-explore-24.png)|[assistant](blue-assistant-24.png)|[me](blue-me-24.png)|
|灵感紫|[home](violet-home-24.png)|[explore](violet-explore-24.png)|[assistant](violet-assistant-24.png)|[me](violet-me-24.png)|

同目录另有8秒端帧。新增tools/nav_contrast.py已接入premium-ui.json及只读候选CI。所有图均为本次合成场景，没有私有历史图片。本机未重复无关长视频测试；常规候选CI按既有门槛运行。未部署。
