# 如何贡献

欢迎任何形式的贡献：Bug 报告、游戏想法、PR、代码评审。

## 贡献渠道

- **Bug / 建议** → 开一个 Issue，用模板填好
- **新增游戏 / 改进现有游戏** → Fork 后开 PR
- **问个问题** → 也可以直接开 Issue，标签选 question

## PR 流程

1. Fork 本仓库，开一个描述性的分支，比如 `add-2048-mobile` 或 `fix-tetris-rotation`
2. 在本地跑 `python3 build.py check` 确保没有漂移
3. **已有游戏**直接改 `index.html` 里对应的 `<textarea id="src-*">`，再同步一份到 `games/<id>.html`
4. **新游戏** 用 `python3 build.py new <name>`，写好后跑 `python3 build.py inline` 同步
5. 提交前双击打开 `index.html` 本地预览一下，确保游戏能正常跑
6. 开 PR，描述里写清楚改了什么 / 为什么改

## 规范

- 所有游戏用纯 **HTML + CSS + 原生 JavaScript**，不引任何 CDN / npm / 字体
- 无图片、无音频、无追踪 — 合集要能 **飞行模式下完全离线可玩**
- 存档用 `localStorage`，全部包 try/catch，存储被禁也不能让游戏崩
- 代码风格对齐现有游戏即可，不强求统一 lint
- 中文 / 英文说明都可以，README 里的游戏列表目前是中文

## 本地开发

```bash
cd offline-minigames
python3 -m http.server 8000
# 打开 http://localhost:8000 预览合集
python3 build.py check   # 每次改完跑一下漂移检测
```

更详细的开发说明见 [README · 开发章节](README.md#开发)。

## 不接受的改动

- 引入外部依赖（CDN、npm、字体、图标库）
- 加埋点 / 统计 / 任何联网请求（除了用户主动触发的）
- 把游戏源码从 `index.html` 里移除（合集必须保持单文件可玩；`games/` 只是副本）
