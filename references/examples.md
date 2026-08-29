# Obsidian Vault Curator examples

All examples in this file are fictional and intentionally unrelated to any user's real Vault, identity, organization, project, or research topic.

## Example 1: restructure one note

### Input

```markdown
数据库索引可以加快查询，但是写入会变慢。我总是忘记什么时候该建索引。

![[index-overview.png]]

常用查询字段可以考虑索引，但是不能什么字段都建。还要看选择性和写入频率。
```

### Output

```markdown
---
tags:
  - database/indexing
aliases:
  - 数据库索引笔记
---

# 数据库索引

数据库索引可以加快查询，但通常会增加写入和维护成本。

![[index-overview.png]]

## 何时考虑建立索引

- 字段经常出现在查询条件中。
- 结合字段选择性判断索引价值。
- 同时考虑写入频率，避免对高频写入表过度建立索引。
```

The output only restructures information already present in the input.

## Example 2: concept patch

### Input fragment

```markdown
- 缓存策略需要考虑 TTL。
```

The user asks what TTL means.

### Output fragment

```markdown
- 缓存策略需要考虑 TTL。
  > [!question]- 补丁：TTL 是什么？
  > TTL（Time To Live）表示缓存条目在失效前可保留的时间。到期后，系统通常需要重新获取或重新计算数据。
```

## Example 3: do not invent wikilinks

Assume the Vault index confirms only these notes exist:

- `Caching Basics.md`
- `Database Indexes.md`

If the text mentions “cache invalidation”, do not automatically create `[[Cache Invalidation]]` unless that target really exists.

A verified link may instead be embedded naturally:

```markdown
这个问题与 [[Caching Basics|缓存基础]] 中的失效策略有关。
```

## Example 4: preserve plugin fields

### Input

```markdown
---
status: active
tags: [reading]
custom_plugin_field: keep-me
---

progress:: 40%

- [ ] 阅读下一章
```

After curation, preserve:

- `status: active`;
- `custom_plugin_field: keep-me`;
- `progress:: 40%`;
- the unchecked task state.

Metadata may be normalized, but unknown fields must not be removed by a template.

## Example 5: private binding is never a repository fixture

The Skill may remember a user's GitHub Vault through the external private state directory. Public examples must never include a real repository identifier, real note path, real attachment name, or copied private note content.
