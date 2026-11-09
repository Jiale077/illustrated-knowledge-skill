# 图文知识学习 · Illustrated Knowledge

给一个主题，从资料查证到图文笔记，一次完成并保存到 Obsidian。

这是一套 Agent 技能与归档工具。Agent 负责检索、写作、生成和检查图片；Python 脚本负责把已完成的文章、图片、提示词与资料记录复制到笔记库。

## 生成什么

- 一篇通俗但保留推理过程的中文知识文章，通常 3000–6000 字。
- 开头完整的概念定义卡片，以及必要的背景、动机与技术由来。
- 通常 3–5 张原理图、对比图或流程图，结尾有一张更完整的综合总结图。
- 靠近关键结论的来源链接、资料底稿和每张图的最终提示词。
- 带 YAML frontmatter、Obsidian 图片嵌入和有效关联链接的笔记。

默认图片采用 Jiale 的 AI 工坊风格：暖白纸底、墨线轮廓、橙色重点与少量青绿结果色。图片中的条件说明与正文协同，减少重复的防御性措辞。

## 使用示例

```text
用图文知识学习，以 MoE 的工作原理为主题跑一遍，最后保存到 Obsidian。
```

```text
用 $illustrated-knowledge 学习 KV Cache：从为什么需要它讲到内存占用，配图并入库。
```

```text
只修改这篇文章开头的定义卡片，图片和正文保持原样。
```

[查看 MoE 示例](examples/moe.md)：示例配图沿用原版，开头定义保留架构、机制和用途的信息。

![MoE Top-2 路由示例](examples/images/moe-top2.png)

## 安装到 Codex

将仓库下载或克隆到技能目录，使 `SKILL.md` 位于 `illustrated-knowledge` 目录根下：

```sh
git clone https://github.com/Jiale077/illustrated-knowledge.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/illustrated-knowledge"
```

也可用技能安装器从仓库安装。其他 Agent 需要支持 `SKILL.md`、文件读写、联网检索和图片工具。

## 配置笔记库

复制 `config.example.json` 为 `config.local.json`，填写 `vault` 的真实绝对路径，并将 `note_area`、`image_root` 改为库内相对目录。配置由 Agent 读取，归档脚本仍需显式传参。

已有知识库规范优先使用：目录、元信息和关联链接会参考实际库内容。开篇卡片样式文件为 `assets/jiale-knowledge.css`，只影响特定 callout。具体操作见 [归档说明](references/obsidian.md)。

## 运行环境与依赖

| 依赖 | 用途 | 要求 |
| --- | --- | --- |
| 宿主原生 Image / imagegen | 生成、编辑真实配图 | 完整图文流程必需；没有图片能力时只交付明确标注缺口的草稿 |
| 联网检索工具 | 官方文档、论文和原始资料查证 | 必需 |
| Python 3.10+ | 本地归档 | 脚本只使用标准库 |
| [Agent Reach](https://github.com/Panniantong/Agent-Reach) | 平台搜索与内容读取 | 优先复用已安装版本；渠道以本机实际状态为准 |
| [content-research-writer](https://github.com/ComposioHQ/awesome-claude-skills/tree/master/content-research-writer) | 辅助写作 | 可选 |
| [baoyu-article-illustrator](https://github.com/JimLiu/baoyu-skills/tree/main/skills/baoyu-article-illustrator) | 辅助分析配图位置与类型 | 可选 |

本包不内置上述第三方技能，也不替代其账户、渠道或图片工具配置。普通网页和论文可直接使用宿主联网工具；平台内容优先使用 Agent Reach。缺少可选依赖时按本包规则完成相应工作，不强制安装整套工具。

## 目录

```text
SKILL.md                   Agent 入口与完整流程
agents/openai.yaml          技能展示信息
config.example.json        可公开的配置模板
references/                写作、配图与归档规则
assets/jiale-knowledge.css  开篇定义卡片样式
scripts/archive_note.py    本地归档工具
examples/                  MoE 示例及原版配图
tests/                     归档行为验证
```

`config.local.json`、工作目录和缓存已被忽略。仓库中不包含个人笔记库、私人会话记录或账号配置。

## 验证与归档预览

```sh
python3 -m unittest discover -s tests -v
python3 scripts/archive_note.py --help
```

归档先执行 `--dry-run`。脚本只新建笔记，同名时追加版本后缀；修改已有笔记由 Agent 先备份再按范围更新。所有文件检查均不能替代事实查证和视觉检查。
