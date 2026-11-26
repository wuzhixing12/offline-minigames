#!/usr/bin/env python3
"""
离线小游戏合集 · 构建辅助脚本

三个命令：
  python3 build.py check                漂移检测：games/*.html 与 index.html 是否一致
  python3 build.py inline               只对带 <!-- INLINE: xxx --> 标记的新游戏块做同步
  python3 build.py new  mygame          生成 games/mygame.html 骨架 + index.html 占位块

说明：
  index.html 里 24 款老游戏（breakout / snake / tetris ...）在并入时已经去掉了各自的
  <html><head> 外层，代码混在主文档里；对这些游戏，继续用编辑器手动改 index.html 即可。

  从本脚本 new 命令创建的**新游戏**会有清晰的 INLINE 标记：
    <!-- INLINE: mygame -->   完整独立游戏 HTML   <!-- /INLINE: mygame -->
  改完 games/mygame.html 后跑 inline 就能自动同步回 index.html。
"""

from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
INDEX = ROOT / "index.html"
GAMES_DIR = ROOT / "games"
BUILDIGNORE = ROOT / ".buildignore"


def _load_buildignore() -> set[str]:
    if not BUILDIGNORE.exists():
        return set()
    return {
        line.strip()
        for line in BUILDIGNORE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }

INLINE_OPEN = lambda name: f"<!-- INLINE: {name} -->"
INLINE_CLOSE = lambda name: f"<!-- /INLINE: {name} -->"


# ────────────────────────────── check ──────────────────────────────

def cmd_check() -> int:
    index = INDEX.read_text(encoding="utf-8", errors="replace")
    games = sorted(p.stem for p in GAMES_DIR.glob("*.html"))
    ignore = _load_buildignore()

    drift_missing = [
        b for b in games
        if b not in ignore and index.count(b) == 0
    ]

    inline_names = set(
        n.decode() for n in re.findall(rb"INLINE: ([a-zA-Z0-9_\-]+)\s*-->", index.encode())
    )
    extra_inline = sorted(n for n in inline_names if n not in set(games))

    ok = True
    if drift_missing:
        print("⚠  games/ 里有这些文件，但 index.html 完全没出现过：")
        for b in drift_missing:
            print(f"    - {b}.html")
        ok = False
    else:
        print("✓  所有 games/*.html 都在 index.html 里有引用")

    if extra_inline:
        print("⚠  index.html 里有这些 INLINE 标记，但 games/ 里没源文件：")
        for b in extra_inline:
            print(f"    - {b}")
        ok = False
    else:
        print("✓  所有 INLINE 标记都有对应的 games/*.html 源文件")

    print("→  没有漂移" if ok else "→  存在漂移，请处理")
    return 0 if ok else 1


# ────────────────────────────── inline ──────────────────────────────

def cmd_inline() -> int:
    index_text = INDEX.read_text(encoding="utf-8", errors="replace")
    games = sorted(p for p in GAMES_DIR.glob("*.html"))

    updated = index_text
    total = 0
    skipped_no_mark = []

    for fp in games:
        base = fp.stem
        open_tag = INLINE_OPEN(base)
        close_tag = INLINE_CLOSE(base)
        pattern = re.compile(
            re.escape(open_tag) + r".*?" + re.escape(close_tag),
            re.DOTALL,
        )
        m = pattern.search(updated)
        if not m:
            skipped_no_mark.append(base)
            continue
        body = fp.read_text(encoding="utf-8").strip() + "\n"
        replacement = f"{open_tag}\n{body}{close_tag}"
        updated = pattern.sub(replacement, updated)
        total += 1

    INDEX.write_text(updated, encoding="utf-8")
    print(f"✓  已内联 {total} 个带标记的游戏")
    if skipped_no_mark:
        print(
            f"ℹ  跳过 {len(skipped_no_mark)} 个老游戏（index.html 里没有 INLINE 标记，"
            f"请手动编辑 index.html；用 `python3 build.py new <name>` 创建的新游戏才有标记）"
        )
        for b in skipped_no_mark:
            print(f"    · {b}.html")
    return 0


# ────────────────────────────── new ──────────────────────────────

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
html,body{{margin:0;height:100%;background:#070b14;color:#e9eefb;}}
#wrap{{display:flex;align-items:center;justify-content:center;height:100%;flex-direction:column;gap:16px;font-family:system-ui,-apple-system,sans-serif;}}
button{{padding:8px 16px;background:#38bdf8;color:#000;border:none;border-radius:8px;cursor:pointer;font-size:14px;}}
</style>
</head>
<body>
<div id="wrap">
  <h2>{title}</h2>
  <p>在这里写你的游戏逻辑。</p>
  <button id="btn">点我</button>
</div>
<script>
(function () {{
  var n = 0;
  document.getElementById('btn').addEventListener('click', function () {{
    n++;
    this.textContent = '已点击 ' + n + ' 次';
  }});
}})();
</script>
</body>
</html>
"""

MENU_HINT = "\n<!-- NEW-GAME-PLACEHOLDER: 菜单 / 分类列表 / 元数据 需手动补充 -->\n"


def cmd_new(name: str) -> int:
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "", name)
    if not safe:
        print("✗ 游戏名只能含字母、数字、下划线、短横线")
        return 2
    fp = GAMES_DIR / f"{safe}.html"
    if fp.exists():
        print(f"✗ {fp} 已存在")
        return 2

    fp.write_text(TEMPLATE.format(title=safe), encoding="utf-8")
    print(f"✓ 已创建 {fp}")

    idx = INDEX.read_text(encoding="utf-8")
    open_tag = INLINE_OPEN(safe)
    close_tag = INLINE_CLOSE(safe)
    if open_tag in idx:
        print(f"⚠  index.html 里已有 INLINE: {safe}，跳过占位插入")
    else:
        close_body = idx.rfind("</body>")
        if close_body < 0:
            print("✗ index.html 没找到 </body>")
            return 1
        inject = (
            f"\n{open_tag}\n"
            + fp.read_text(encoding="utf-8")
            + f"\n{close_tag}"
            + MENU_HINT
        )
        idx = idx[:close_body] + inject + idx[close_body:]
        INDEX.write_text(idx, encoding="utf-8")
        print(f"✓ 已在 index.html 末尾 </body> 前加入内联块 + 菜单占位")

    print()
    print("→ 接下来：")
    print(f"   1. 编辑 games/{safe}.html 写游戏")
    print(f"   2. 把 index.html 里菜单占位替换为真实菜单项（分类、难度、时长、评级）")
    print(f"   3. 改完 games/{safe}.html 后跑 `python3 build.py inline` 同步回 index.html")
    return 0


# ────────────────────────────── main ──────────────────────────────

USAGE = f"""
离线小游戏合集 · 构建辅助脚本

  python3 build.py check             漂移检测：games/*.html 与 index.html 是否一致
  python3 build.py inline            同步带 <!-- INLINE: xxx --> 标记的新游戏
  python3 build.py new <name>        新建一个 <name>.html 骨架并在 index.html 占位
""".strip()


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(USAGE)
        return 0
    cmd = argv[1]
    if cmd == "check":
        return cmd_check()
    if cmd == "inline":
        return cmd_inline()
    if cmd == "new":
        if len(argv) < 3:
            print("✗ new 需要一个名字，例如 `python3 build.py new mygame`")
            return 2
        return cmd_new(argv[2])
    print(f"✗ 未知命令: {cmd}\n{USAGE}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
