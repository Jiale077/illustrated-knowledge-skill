# README 的资料依据

本页按图文知识学习流程制作：读取实际仓库、核对安装规则、组织解释路线、生成品牌封面、复用真实示例。

| 依据 | 本页采用的信息 |
| --- | --- |
| [技能入口](../SKILL.md) 与 [写作规则](../references/writing.md) | 主题学习流程、完整定义、背景、算例和结尾总结图；README 输出形式 |
| [配置模板](../config.example.json) 与 [归档脚本](../scripts/archive_note.py) | 配置字段、显式传参、真实图片复制、版本后缀和 dry-run |
| [归档行为检查](../tests/test_archive_note.py) | 不覆盖原文、路径边界、图片与提示词复制、纯文字模式 |
| [OpenAI 官方技能说明](https://learn.chatgpt.com/docs/build-skills) | 从仓库安装技能、用户级 `.agents/skills` 目录、自动发现与刷新行为 |
| [售前工作台首页](https://github.com/Jiale077/obsidian-presales-workbench) | 品牌名、大标题、三步场景封面与从用途到安装的页面组织 |
| [视觉规范](../references/jiale-style.md) 与 [封面提示词](cover-prompt.md) | 暖白纸底、墨线、橙色重点及同系列角色；原生 Image 生成 |
| [MoE 示例](../examples/moe.md) | 真实完成的 Top-2 解释图和综合总结图，沿用原版图片 |

封面是品牌概念插图，示例图片为实际生成的教学图解。各安装说明与运行结果的核验范围分别记录，不将代码存在等同于执行成功。
