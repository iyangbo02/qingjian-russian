# 释义表

候选词右侧那一行「词性 + 译词」的数据，一张表一门学习语言。

格式：`词\t[词性. ]译词[|读音]\t…`，UTF-8 **无 BOM**、LF 换行、按码点排序。
解析在 `crates/qingjian-translate/src/glossary/mod.rs`，规则是严格的：任一行缺词或缺释义，
整张表加载失败（`.qj` 打包走同一套解析）。

本目录各表的来源与许可见下；俄语重音数据另保留 CC-BY-SA-4.0 许可和署名。

## 英语 / 日语（`glossary-en.tsv` / `glossary-ja.tsv`）

由 `tools/gloss-gen` 用 LLM（DeepSeek）离线批量生成，不含任何第三方词典内容。

- `data/generated/gloss-llm.jsonl`：模型原始输出，一行一个词（词性、英文译词、日文译词与假名），可续跑：
  `cargo run --release -p qingjian-gloss-gen -- generate --words assets/lexicon/dict.tsv --min-count 1 --max-chars 8`
- `glossary-en.tsv` / `glossary-ja.tsv`：输入法加载的表，由 `... export --out-dir assets/glossary` 导出。

2026-09-05 对 `assets/lexicon/dict.tsv` 全量生成：23.9 万词（含旧语料词表的 3.8 万），
词库多字词 91% 有英文释义、98% 有日文释义。

## 西班牙语（`glossary-es.tsv`）

由 `tools/corpus/glossary_es.py` 用 **Azure Translator** 机器翻译生成，**不是 LLM**，
也不经过 `gloss-gen` 的 `export`（那只写 en / ja 两张表），是这个脚本的直接产物。

- 词表、词性、英文释义都取自 `glossary-en.tsv`；译文来自 Azure Translator F0 免费层
  （每月 200 万字符，跑完全量用掉约 127 万）。
- 可复现，有 Azure 免费 key 就能重跑：
  `AZURE_TRANSLATOR_KEY=… AZURE_TRANSLATOR_REGION=… uv run tools/corpus/glossary_es.py`
- 覆盖：`glossary-en.tsv` 的 232,213 个词里 193,292 个有西语释义（83.2%）。
- 翻译策略（按词性分源语言）与三组对照实验记在脚本的模块 docstring 里。

**已知问题**（2026-09-14 生成，机器翻译，未经人工校对）：

- 名词约 13% 还是复数（`朋友 -> amigos`，不是 `amigo`）
- 个别错译：`椅子 -> presidente`、`工作 -> obra`、`必须 -> debe`
- 生僻字与专名的准确率低
- 动词走英文源（`to {英文释义} (verb)`）后约 86% 是原形，其余是别的动词形式
- 有一部分条目的译词还是英文，没有翻成西语：
  - 整条是英文的：「会 + 动词」这一类几乎全是（`会买 -> will buy`、`会去 -> will go`、
    `会飞 -> can fly`），另有 `你需要 -> you need`、`下了 -> got off`、`不得 -> must not`、
    `中耳炎 -> otitis media`。这类全小写的英文短语共 177 条
  - 单个词没翻的：`三明治 -> sandwich`、`五金 -> hardware`
  - 英西混排的：`也会 -> will también`、`会令 -> will hacer`、`不送 -> no Ver Off`
  - 与 `glossary-en.tsv` 的英文释义逐字相同的条目里，绝大多数是同形词或专名
    （`abdomen`、`vector`、`Ding Wei`），属正常
- 7 条没有词性（源表 `glossary-en.tsv` 里就没有），如 `刷拉 -> swish`、`嗡嗡 -> buzz`、
  `御 -> carruaje imperial`；其中 `第 -> No` 是错译（源表的英文释义是 `-th`）
- 短语中间的词首字母有时会被无端大写：`开发区 -> zona de Desarrollo`、`一等奖 -> primer Premio`

欢迎报错译：有反馈之后可以再用 LLM 在现有表上精修一轮。

## 英→中（`glossary-zh.tsv`）

英文候选（中英混输、英文模式）右侧显示的中文释义。词按 wordfreq 词频 ≥ 2500 加技术词表全部，
约 4.5 万词：

```
cargo run --release -p qingjian-gloss-gen -- english --include assets/lexicon/05_english/05_tech/*.tsv
cargo run --release -p qingjian-gloss-gen -- export-english
```

`data/generated/gloss-en-llm.jsonl` 是它的原始输出。表的键是小写，Engine 查表时把候选转小写。

## 中间产物

模型原始输出的三个 JSONL（`gloss-llm.jsonl`、`gloss-en-llm.jsonl`、`pinyin-llm.jsonl`）都在
`data/generated/`，不进 git：它们只是续跑用的中间产物，每重跑一轮就变一份，仓库只保留导出的最终表。
发布时随 `.qj` 一起作为 Release 附件保存，重跑前先从那里下载。

生成时的提示词在 `tools/gloss-gen/src/prompt.rs`（中→英 / 日）与 `tools/gloss-gen/src/english.rs`（英→中）。

## 俄语（`glossary-ru.tsv`）

当前 1,656 个中文词条。在原有 1,000 条基础上新增 656 条：学术与课程 196 条、论文与课堂 166 条、日常生活 209 条、通讯与电脑 85 条。

选词涵盖数字产品市场、全球化、稳定币跨境支付和数字教育。仅收录通用术语。

`ru-study-dict.tsv` 提供 64 个重要中文术语的拼音候选（AI 编写，GPL-3.0-or-later）。macOS 随包置于 `dicts/ru-study.tsv`，在偏好设置词库页开启；也可导入为用户词库。
中文与俄语译词配对由 AI 编写，未经过专业译者完整校对。
重音和词形参考 [OpenRussian 数据](https://github.com/Badestrand/russian-dictionary)
的 `50e210c4803237779cb562bc1abcea529066031c` 快照（nouns / verbs / adjectives / others）。
OpenRussian 数据为 CC-BY-SA-4.0；原有中俄配对为 GPL-3.0-or-later。
本表保留两类来源的许可，标识为 `GPL-3.0-or-later AND CC-BY-SA-4.0`。
数据许可全文在 `LICENSE-OPENRUSSIAN.txt`，使用到的重音词形与定向选择在 `ru-stress-sources.json`。

改动：将撇号重音转为 Unicode U+0301；按中文释义处理同形异音（锁 `замо́к`、面粉 `мука́`、写 `писа́ть`）。
少量缺失项定向核对；语法补充词条与中俄配对由 AI 编写，核对来源见 JSON。
多音节词标主重音，单音节词不额外标记；含 ё 的词保留 ё，不再叠加重音。
名词通常用单数主格，动词用不定式；只有复数形式的名词保留复数。
没有词汇等级表、自动变格、动词体配对或语音；未覆盖候选不会显示译词。
云端补译提示要求相同的重音写法，但模型输出的词义和重音仍可能有误。

打包：
`cargo run -p qingjian-dict-convert -- pack glossary --language ru --license "GPL-3.0-or-later AND CC-BY-SA-4.0" --attribution "中俄配对由 AI 编写；重音来源 OpenRussian.org，定向校核"`

俄语大型离线词典的本地导入工具为 `tools/corpus/glossary_ru_bkrs.py`，保留本目录学习词优先级；第三方全文不存入本目录，来源与重建方式见 [扩展说明](../../docs/notes/russian-dictionaries.md)。
