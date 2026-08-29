# Obsidian 整理与保护规范

本文件用于需要处理复杂 Obsidian Markdown 语法、Properties、代码、公式、任务或插件字段时查阅。

## 目录

1. 标题与段落
2. Properties / Frontmatter
3. 标签与别名
4. Wikilinks 与嵌入
5. Callout
6. 代码与公式
7. 任务、Dataview 与块 ID
8. 引用、脚注与注释
9. 表格、高亮与强调
10. 整理时禁止的变换

## 1. 标题与段落

- 文件已有主标题且合理时保留。
- 文件没有主标题时，可以从内容或文件名补一个 `#` 标题。
- 正文默认使用 `##` / `###`；深层标题只在确有父子层级时使用。
- 不要把每个列表项升级成标题。
- 段落表达连续论证；列表表达并列、步骤、条件、优缺点或清单。
- 允许为了可读性拆句和分段，但不要改变因果、范围、概率、否定词和数字。

## 2. Properties / Frontmatter

推荐形式：

```yaml
---
tags:
  - ros/noetic
  - localization
aliases:
  - 双天线航向
source: 原有来源
custom_field: 保留用户自定义值
---
```

规则：

- 先读取已有 Frontmatter，再决定是否修改。
- 未知字段必须保留；不要套模板后丢失自定义属性。
- 多值字段合并时去重，并尽量保留原顺序。
- 不把 `#tag` 形式机械写入 YAML；Properties 中通常使用不带 `#` 的标签值。
- 不从文件时间戳猜测 `created` / `modified`，除非用户要求把文件元数据写入属性。
- 不把来源 URL 猜成“官方链接”。

## 3. 标签与别名

### tags

好标签：
- 稳定学科：`ros/noetic`、`gnss`、`remote-sensing`
- 长期项目：`project/lio`、`phd/literature`
- 稳定工作流：`status/to-review`

避免：
- 为正文每个名词建标签；
- 一篇笔记产生十几个只出现一次的标签；
- 同时维护多个同义标签，如 `AI`、`ai`、`artificial-intelligence`，除非用户已有这种体系。

### aliases

- 只添加真实常用别名、缩写、中文/英文对照或历史名称。
- 不为了“丰富元数据”制造无用 aliases。

## 4. Wikilinks 与嵌入

常用形式：

```markdown
[[Note]]
[[Note|显示文字]]
[[Note#Heading]]
[[Note#^block-id]]
[[#本页标题]]
![[image.png]]
![[image.png|420]]
![[Note#Heading]]
```

保护要求：

- 嵌入 `![[...]]` 视为附件引用，不得在普通整理中改目标。
- 原有 wikilink 目标不要随意替换；改变显示别名也要确保语义一致。
- heading 重命名可能破坏 `[[Note#Heading]]`；没有全库索引时应避免无必要的 heading 改名。
- block ID `^id` 可能被其他笔记引用，必须保留精确文本。

## 5. Callout

基本形式：

```markdown
> [!note] 标题
> 内容
```

折叠：

```markdown
> [!question]- 补丁：术语是什么？
> 解释
```

使用规则：

- `note`：关键说明；
- `tip`：实践建议；
- `warning` / `danger`：风险；
- `question`：概念补丁、待澄清问题；
- `abstract` / `summary`：确有必要的短总结；
- `example`：独立示例。

不要把普通段落全部装进 callout。已有 callout 的 `+` / `-` 折叠状态要保留。

## 6. 代码与公式

### 代码

- fenced code block 内文本默认逐字保护，包括空格、缩进和注释。
- inline code 如命令、路径、参数、topic 名、函数名等不要润色。
- 不擅自把 bash 命令改成“更规范”的替代命令。

### 数学

- `$...$` 与 `$$...$$` 内公式不要语言化改写。
- 可整理公式周围说明文字，但不要改变符号定义、上下标或单位。
- 编号公式、LaTeX environment 或自定义宏应原样保护。

## 7. 任务、Dataview 与块 ID

保护以下结构：

```markdown
- [ ] 待办事项
- [x] 已完成事项
status:: active
priority:: high
^reference-block
```

- 任务状态属于数据，不要把 `- [ ]` 改成普通 bullet。
- Dataview inline field 的键名、`::` 和值都可能参与查询。
- DataviewJS 代码块按代码保护。
- block ID 需要精确保留；移动可以，但不要删除或改名。

## 8. 引用、脚注与注释

保护：

```markdown
> 引用内容
[^1]: 脚注正文
这是术语[^1]
%% Obsidian comment %%
```

- 引用可以移动到对应论述附近，但不要改成普通正文导致来源边界消失。
- 脚注引用与定义要配对。
- Obsidian 注释可能存储编辑信息或私密辅助文本；默认保留且不要主动展开到正文。

## 9. 表格、高亮与强调

- 只有真正需要横向比较时才用表格。
- 保留有意义的 `==高亮==`。
- 新增加粗用于关键术语或结论，不要每句都加粗。
- 不自动加入 emoji、彩色 HTML 或复杂 CSS class。

## 10. 整理时禁止的变换

除非用户明确要求，不要：

- 自动重命名文件；
- 自动移动附件；
- 把未验证概念变成 wikilink；
- 把现有 heading 大规模改名；
- 删除看似“多余”的 Properties 字段；
- 删除任务、脚注、注释、block ID、Dataview 字段；
- 改写代码、命令、路径、LaTeX；
- 新增虚假来源、论文、URL、数字或结论；
- 为追求统一格式而消除用户已有的有意义结构。
