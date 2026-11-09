# 配置与 Obsidian 归档

## 目标库配置

复制根目录 `config.example.json` 为 `config.local.json`，填写自己的路径；本地配置已加入 `.gitignore`。

- `vault`：目标 Obsidian 库的绝对路径。可为空，由当前用户上下文确定。
- `note_area`：笔记目录，相对于库根目录；优先采用库内已有分类。
- `image_root`：附件目录，相对于库根目录。

配置由 Agent 读取，归档脚本使用显式命令行参数，不会自动读取配置。运行前读取目标库实际存在的指引和同类笔记。

## 笔记结构

下面是最小元信息示例，保留目标库已有的字段约定：

```yaml
---
title: 主题名称
type: knowledge
tags: [学习, 主题关键词]
created: YYYY-MM-DD
status: draft
---
```

正文引用公开来源时使用 Markdown 链接，关联库内内容使用已经核实的 wikilink。输出草稿用 `<!-- figure:01 -->` 标记配图位置；每个 ID 只出现一次。

## 开头定义卡片

标题下用完整的概念定义开篇，交代主题性质、核心机制与用途。MoE 的实例：

```markdown
> [!jiale-definition]
> **MoE（混合专家）**是一种按输入调用并组合专家网络的模型架构；大语言模型常用稀疏路由，让每个词元只激活少数专家，以扩大参数容量并控制计算量。
```

卡片采用浅橙背景、细侧线和适度圆角，正文常规字重，只局部强调主题名；隐藏标签栏和图标。CSS 位于 `assets/jiale-knowledge.css`。

目标库首次使用时，将 CSS 复制到 `.obsidian/snippets/jiale-knowledge.css`；在 `.obsidian/appearance.json` 的 `enabledCssSnippets` 列表中追加 `jiale-knowledge`，保留其他设置。已有同名样式先读取，尊重用户定制。CSS 只作用于 `jiale-definition` callout。

## 图片清单与归档

保存 `images.json`：

```json
[
  {
    "id": "01",
    "path": "images/01-flow.png",
    "alt": "这张图展示的内容",
    "caption": "图 1：引导读者观察的重点。",
    "prompt": "prompts/01-flow.md"
  }
]
```

`path`、`prompt` 相对于清单文件，也可以填真实绝对路径。图片 ID 与正文标记一一对应。脚本接受 PNG、JPEG、WebP。

从技能安装目录调用，替换所有示例路径：

```sh
python3 scripts/archive_note.py \
  --note /path/to/work/article.md \
  --images /path/to/work/images.json \
  --vault /path/to/ObsidianVault \
  --area Learning \
  --image-root Attachments/illustrated-knowledge \
  --record /path/to/work/sources.md \
  --record /path/to/work/illustration-plan.md \
  --dry-run
```

核对预览后移除 `--dry-run` 执行。结果输出 JSON，包含笔记、图片与记录文件路径。图片、提示词和资料记录会复制进库，正文替换为 `![[附件相对路径]]` 与图注。同名笔记追加 `-v2` 等后缀；附件使用本地时间生成的独立目录。

纯文字交付需明确传入 `--text-only`；此模式不能与非空图片清单混用。修改已有笔记时先备份，按授权原位更新；此脚本不提供覆盖模式。

脚本核对文件、基本元信息、标记和路径。事实、图中文字与视觉可读性由 Agent 另行检查；只有实际预览过界面，才能报告界面验证完成。
