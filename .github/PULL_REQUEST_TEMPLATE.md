name: 📦 Pull Request 模板
description: 开 PR 时自动附上这份清单
title: "feat|fix|chore|refactor|docs: 简短描述"

labels: ''
assignees: ''

body: |
  ## 改了什么

  <!-- 一句话总结 + 关键改动点 -->
  - 
  - 

  ## 为什么改

  <!-- 关联 Issue、用户反馈，或者自己的动机 -->
  - 关联 #XXX / 灵感来自…

  ## 改动范围

  - [ ] 只动了 `games/*.html`（新增或修改独立源码）
  - [ ] 改了 `index.html`（老游戏内联代码）
  - [ ] 改了 README / CONTRIBUTING / docs
  - [ ] 改了 CI / build / 部署脚本
  - [ ] 加了 screenshot

  ## 本地验证

  - [ ] `python3 build.py check` 跑过，exit 0，无漂移
  - [ ] `python3 build.py inline` 跑过（新游戏）
  - [ ] 本地双击打开 index.html 能正常进入
  - [ ] 改动涉及的那款游戏手动跑过一轮

  ## 有没有 breaking change？

  - [ ] 没有
  - [ ] 有：存档格式变了 / 游戏规则有大改，简述一下

  ## 还需要注意的事

  <!-- 比如 README 里的游戏列表要同步、截图要补、上线前要跑一轮... -->
  - 
