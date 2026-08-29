---
name: obsidian-vault-curator
description: 分析、设计、整理和维护 Obsidian Markdown 笔记与 Vault，尤其适用于笔记长期保存在 GitHub 仓库中的知识库。用于先分析现有 Vault 的数据形态、目录、Frontmatter、标签、链接、任务、日志、来源与笔记长度等结构特征，再为用户选择合适的混合笔记逻辑与方法，并从仓库外的私有持久化状态目录恢复 Vault 绑定和已采用的笔记方法；支持 GitHub connector 安全读写、单篇/多篇重构、Properties 合并、wikilinks、概念补丁、批量知识关联与冲突可控提交。必须保护原始语义与隐私，绝不把用户仓库地址、私有路径、令牌或个人笔记内容写入 Skill 源码仓库或 Skill 包。
---

# Obsidian Vault Curator

把内容已有但结构欠佳的 Obsidian 笔记整理成简洁、可检索、可关联、可长期维护的知识库内容。优先保护信息与 Obsidian 语义，再改善结构与可读性。

本 Skill 支持 GitHub-backed Vault，也支持用户直接提供 Markdown 或本地 Vault。GitHub-backed 模式必须把用户绑定信息保存在 **Skill 仓库之外** 的私有持久化状态目录中。

按需读取：
- `references/private-state.md`：私有持久化状态目录、绑定、权限、迁移与隐私规则。
- `references/github-backend.md`：GitHub 读取、分支、原子提交、PR、冲突和重试策略。
- `references/note-methodology.md`：Vault 诊断、笔记类型识别、混合笔记方法、试点与长期方法规则。
- `references/formatting-rules.md`：排版、Properties、任务、代码、公式和 callout 规则。
- `references/vault-linking.md`：Vault 索引、真实双链、批量整理和文件迁移规则。
- `references/examples.md`：完全虚构的通用示例。

## 工作模式

1. **Vault 诊断与方法设计**：分析现有数据形态，识别反复出现的笔记类型与工作流，推荐适合的笔记逻辑和方法。
2. **GitHub 单篇整理**：从已绑定 Vault 读取一篇笔记，按已采用的方法整理后安全写回。
3. **GitHub 批量整理**：处理多篇笔记、跨笔记链接或元数据一致性，通过临时分支与 PR 写回。
4. **单篇文件整理**：整理用户直接提供的 Markdown 或本地 `.md` 文件。
5. **概念补丁**：只解释用户点名的术语，不重排整篇。
6. **Vault / 多篇整理**：扫描多篇笔记，验证真实链接后建立关联。
7. **审计模式**：只指出结构、链接、标签、元数据、方法或语法问题，不写回。

## 私有状态必须与 Skill 仓库隔离

不要在 Skill 源码目录、Skill ZIP、README 示例或公开 GitHub 仓库中保存以下信息：

- 用户实际 Vault repository；
- 私有分支或 Vault 根路径；
- access token、PAT、cookie 或 connector credential；
- 用户真实笔记标题、附件名、目录结构或笔记正文；
- 从用户知识库推断出的身份、项目、研究主题或组织信息。

状态目录解析顺序：

1. 若环境变量 `OBSIDIAN_CURATOR_STATE_DIR` 已设置，使用该目录；
2. 否则使用用户主目录下的 `~/.obsidian-vault-curator/`；
3. 状态目录必须位于 Skill 源码树和 Vault Git 仓库之外；若检测到位于其中，拒绝写入并要求换目录。

标准布局：

```text
<state-root>/
├── profiles/
│   └── default.json
├── runtime/
│   └── last-success.json
├── cache/
│   ├── vault-index.json
│   └── vault-patterns.json
├── methods/
│   └── note-system.json
└── locks/
    └── github-write.lock
```

首次绑定、修改绑定或保存笔记方法时，优先运行 `scripts/state_store.py`。`methods/note-system.json` 只保存方法与结构偏好，不保存原始笔记正文。详细规则见 `references/private-state.md`。

如果当前运行环境没有可持久写入的私有文件系统，不要假装已经持久化，也不要退回到把配置塞进 Skill 包或公开仓库。应明确说明限制，并仅在当前会话使用用户提供的绑定，或使用用户指定的私有持久存储位置。

## GitHub-backed 启动流程

每次任务都重新从私有状态目录加载绑定，不依赖聊天记忆：

1. 加载 `profiles/default.json`。
2. 若存在 `methods/note-system.json`，同时加载已采用的笔记方法；普通整理时不要每次重新设计方法。
3. 取得 Vault repository、base branch 与可选 Vault root。
4. 用 GitHub connector 确认仓库和分支仍可访问。
5. 限定所有读写路径在配置的 Vault root 内，除非用户明确要求扩大范围。
6. 从远端读取当前文件；不要复用上一轮对话缓存的正文或 SHA。
7. 先形成完整修改方案并执行保护检查，再选择写回策略。

配置不存在时进入一次性绑定模式：只询问真正缺失的信息，并把结果写到私有状态目录；以后不再重复询问。

## 默认 GitHub 写回策略：branch-first

默认不要直接写基础分支。即使只有一个文本笔记，也优先：

1. 从最新基础分支创建唯一临时分支；
2. 在内存中完成本批次所有修改；
3. 对修改结果执行语义保护检查；
4. 尽可能用 GitHub Git Data 能力把本批次变更合成 **一个原子 commit**；
5. 创建 PR；
6. 安全文本修改验证通过且 PR 可合并时，按私有配置允许自动 squash merge；
7. 重命名、移动、删除、附件变更等高风险操作默认不自动合并。

只有私有配置明确开启 direct-write，并且确实是单文件、无跨链、无移动删除、无附件变更时，才可直接更新基础分支。

完整策略见 `references/github-backend.md`。

## 错误与重试硬规则

- 同一路径绝不并行写。
- 同一任务中，每个笔记优先只生成一次完整最终内容。
- stale SHA / ref conflict 只允许刷新后重试 1 次。
- 权限、认证或 connector 失败立即停止写入，不循环重试。
- 分支名冲突只生成一次新后缀；再次失败则停止。
- 内容无变化时跳过写入，不生成空 commit。
- 临时分支准备期间基础分支发生冲突性变化时，不强推、不 force merge；保留 PR/分支并报告冲突。
- 不为了“推送成功”反复提交相同请求。

## 核心保护契约

整理时允许移动到更合理的位置，但不要无意改写、删除或破坏：

- 原文事实、数字、结论、例子、引用与限定条件；
- YAML Frontmatter / Obsidian Properties 中已有字段；
- fenced code blocks、inline code、命令、配置片段；
- `$$...$$`、`$...$`、LaTeX 公式；
- `![[...]]`、Markdown 图片、附件路径和尺寸参数；
- 已有 `[[wikilinks]]`、heading links、block links；
- block ID，如 `^block-id`；
- 任务，如 `- [ ]`、`- [x]`；
- Dataview / DataviewJS 字段与表达式；
- footnotes、引用块、HTML、Obsidian 注释；
- 已有 callout 的语义和折叠状态。

修改前后文件都可访问且脚本环境可用时，运行：

```bash
python scripts/verify_note_preservation.py ORIGINAL CURATED
```

发现保护项丢失时先修复，再写回。

## Vault 诊断与笔记方法设计

当用户要求“分析我现在的笔记怎么整理”“帮我设计笔记逻辑/笔记方法”“这个 Vault 应该怎么组织”时，不要先套模板。按以下流程：

1. **只读诊断**：先观察当前 Vault，不立即改文件。
2. **结构统计**：分析笔记数量和长度、目录深度、日期命名、Frontmatter keys、tags、wikilinks、tasks、source/url、代码、表格、callout、Dataview 等。
3. **识别反复出现的功能类型**：例如 capture、concept、source/reference、project、log/experiment、decision、technical-howto、MOC/hub、structured-reference。
4. **识别真正的摩擦点**：区分“格式不统一”和“知识逻辑混乱”，例如来源与个人结论混在一起、项目日志被当成永久知识、daily 中的结论从未沉淀、标签/文件夹/链接重复承担同一分类职责。
5. **推荐最小可用方法**：优先混合 note-type 架构，不因为流行而强推 PARA、Zettelkasten 或统一模板。
6. **小批量试点**：先挑 5–15 篇代表性笔记试整理，验证检索、阅读、维护和链接是否变好。
7. **持久化已接受的方法**：用户接受后，把方法写入外部私有状态 `methods/note-system.json`；不要写入 Skill 仓库或 Vault 正文。
8. **后续自动沿用**：未来整理时先读取该方法，根据笔记功能类型选择相应结构；只有用户要求重设计或 Vault 明显漂移时才重新诊断。

本地/materialized Vault 可运行：

```bash
python scripts/analyze_vault_patterns.py <vault-root> --output <private-report.json>
```

默认报告只含聚合结构指标，不输出笔记正文、标题或路径。完整方法见 `references/note-methodology.md`。

### 方法设计原则

- 不要求整个 Vault 只有一种笔记模板。
- **Capture** 服务快速记录；不要过度格式化。
- **Source** 保存外部来源；与用户自己的 synthesis/claim 分开。
- **Log / Daily / Experiment** 保留时间线；不要反复重写成 evergreen 文体。
- **Project** 围绕当前目标、状态、行动和决策。
- **Concept / Evergreen** 保存可复用理解；只有具备独立复用价值时才拆成原子笔记。
- **Decision record** 保存为什么做出选择。
- **How-to / Troubleshooting** 强调症状/目标、证据、步骤、验证和失败模式。
- **Reference** 强调快速查找；表格/列表往往优于长段落。
- **MOC / Hub** 用于真实需要导航的知识簇，不是 backlink 列表。
- 文件夹、Properties、tags、wikilinks、MOC 应分工，不要重复编码同一分类体系。

## 单篇整理流程

1. 完整读取全文，不要边读边改。
2. 识别主题、并列概念、步骤、因果和总结。
3. 标记代码、公式、嵌入、任务、引用、Properties 和链接等保护对象。
4. 用最少层级重建结构；合并重复表达但不损失信息。
5. 合并而非覆盖 Properties；清理标签；验证双链；必要时使用少量 callout。
6. 把超长段落拆成短段落或列表，修正明显语病但不改变原意。
7. 检查 YAML、标题、链接、任务、代码、公式、嵌入和保护项。
8. 按 GitHub 或本地写回约定交付。

## 结构与排版原则

- 一个笔记最多一个 `#` 主标题；正文优先 `##` / `###`。
- 不为每两三句话创建标题。
- 并列属性、条件、步骤、优缺点适合列表；连续论证适合短段落。
- 表格只用于真正的多维对比或结构化数据。
- 高亮、加粗、斜体要克制；默认不添加 emoji 装饰。
- callout 只服务于摘要、结论、警告、问题或独立示例；普通笔记通常 0–2 个。
- 图片和嵌入靠近解释内容；不要擅自改附件目标。
- 不在文末堆砌无语义的“相关笔记”列表。

## Properties / Frontmatter

- 合并而不是覆盖已有 Frontmatter。
- 保留未知字段和值。
- `tags`、`aliases` 只做去重、规范化和必要补充。
- 不凭空填写 `source`、`author`、`created`、`modified`、`status` 等事实型属性。
- 标签优先表达稳定主题或工作流分类，不把正文每个名词都变成标签。
- 用户已有命名体系时沿用，不另造第二套分类法。

## Wikilink 与知识关联

无法查看 Vault 时：
- 保留现有双链；
- 不确认目标存在时不新增 wikilink；
- 可以提出候选关联，但不要直接写入正文。

可查看 Vault 时：
1. 中小型 Vault 可运行 `scripts/build_vault_index.py` 建索引；
2. 验证笔记路径、重复 stem、heading、block ID、links 和 embeds；
3. 只链接真实存在且有明确语义关系的目标；
4. 同一概念通常只在首次或关键位置建立链接；
5. 深链接必须验证 heading / block ID；
6. 重名笔记使用可唯一解析的路径。

## 批量整理

- 先按目录或主题选择一个小批次，不做全库大爆炸式重写。
- 默认每批最多 10 个变更文件；私有配置可调低或调高。
- 每篇先做单篇整理，再做跨笔记链接和标签治理。
- 不为了 Graph View 密度硬加链接。
- 不自动重命名或移动文件；用户明确要求时才做 backlink-aware 迁移。
- 批量完成后验证代表性笔记和链接完整性。

## 概念补丁

当用户只问某个术语是什么、为什么需要或与另一个概念有何差异时：

- 不重新排版整篇；
- 在原句附近添加默认折叠的 question callout；
- 标题使用 `补丁：...`；
- 一般 2–5 句，只讲可靠定义和必要边界；
- 新增 wikilink 仍须验证真实目标。

```markdown
原句……

> [!question]- 补丁：术语是什么？
> 简洁、可靠的解释。
```

## 最终检查

交付或写回前确认：

- 没有把任何用户私有绑定或笔记内容写入 Skill 仓库/Skill 包；
- 原始事实和限定没有被改变；
- Frontmatter 可解析且未知属性仍在；
- 代码、公式、附件、任务、Dataview、footnotes 和 block ID 未损坏；
- 新增 wikilink 都有真实目标；
- GitHub 写回遵守 branch-first、有限重试和无强推规则；
- 若私有笔记方法存在，整理结果与其 note-type 规则一致；若不存在且任务涉及体系设计，先诊断再推荐；
- 无变化时没有生成提交；
- 高风险操作没有被自动合并。
