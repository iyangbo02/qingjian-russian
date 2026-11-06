# Qingjian Russian · 青简俄语衍生版

基于 [qingjian-team/qingjian](https://github.com/qingjian-team/qingjian) 改进的**非官方俄语学习版本**。感谢原作者 [@yenharvey](https://github.com/yenharvey)、[@qingjian-team](https://github.com/qingjian-team) 及所有上游贡献者。输入引擎和原有功能来自青简，本仓库主要增加俄语译词、学习用重音和词典导入工具。

本分支基于上游提交 [`c08ae57`](https://github.com/qingjian-team/qingjian/commit/c08ae57cb88b6a4a46f4a5e9c1d6d11c5e69222e)（0.1.5-dev 开发阶段），**没有合并上游后续版本**。本项目不代表青简官方，也不宣称拥有青简名称、logo 或上游代码的原创权。完整 Git 历史与原有许可证保留。

## 增加了什么

- 学习语言增加俄语（`ru`），候选汉字旁显示俄语释义。
- 自带 1,656 条中俄学习词条及 64 条中文术语候选；多音节俄语词标注重音，保留 ё。
- 生词译文从橙黄色调整为蓝色，兼顾浅色与深色背景；熟词仍为灰色。
- 提供 БКРС 离线词典导入工具，可在用户本机扩充覆盖范围。
- 云端补译提示支持俄语与重音要求，需要自行配置服务。

这是一款**中文输入法附带俄语译词**，不是俄语键盘，也不会自动根据句子对俄语变格或变位。

安装提示：macOS 安装包欢迎页/完成页、命令行构建安装及 Linux 安装脚本会自动说明 БКРС 可选导入入口；Windows 安装器完成页也有提示。提示不等于自动下载或导入。

## 词表规模与准确性

**仓库默认只包含 1,656 条学习词，不包含 157 万条词典全文。** БКРС 2026-10-06 数据曾在本机导入为 1,575,086 个合并释义词条，并补充 20,000 个中文候选；这不等于日常汉字的全部覆盖。导入器保留完整紧凑义项，同形异音或未知词形不猜重音。

中俄配对有 AI 辅助编写，未经过专业人员完整校对；释义与重音可能有误。БКРС 全量数据的再分发条款尚未完全核实，因此这里只公开导入工具、来源和重建步骤，不分发全量数据或包含它的安装包。见 [词典导入说明](docs/notes/russian-dictionaries.md)。

## 构建与使用

目前公开源码，不提供经过 Apple 公证的俄语版安装包。macOS 上已本机使用；Windows 与 Linux 有俄语接入代码，但本分支未完成各平台实机验证。

按 [上游开发文档](docs/) 准备 Rust 与平台依赖。在仓库根目录执行：

```sh
tools/release/data-fetch.sh
apps/macos/scripts/bundle.sh --pkg
```

产物在 `target/pkg/`。产品数据由脚本从上游发布资源获取；俄语学习词表由本仓库打包。构建详细说明见 [俄语指南](RUSSIAN-README.md)。

安装后选择「青简 → 偏好设置 → 通用 → 学习语言 → 俄语」。本机为了避开候选汉字空白/方框问题，采用以下设置；如果遇到相同问题，可在配置文件中合并：

```toml
[general]
learning_language = "ru"
renderer = "system" # macOS 使用系统文字绘制
```

macOS 配置位置：`~/Library/Application Support/Qingjian/config.toml`。已有 `[general]` 时在该节内修改，不要重复添加节。汉字显示问题的根因尚未确认，此设置是已在本机验证的绕行方法。

俄语版与官方版使用相同应用标识和用户目录，会相互覆盖；安装任一版本前请备份个人词库、配置和扩展词典。官方安装包不包含本分支的俄语改动。

## 来源与许可

- 上游源码：[@yenharvey](https://github.com/yenharvey) 与 [qingjian-team/qingjian](https://github.com/qingjian-team/qingjian)，沿用 [GPL-3.0-or-later](LICENSE)。
- 本分支代码改动：同样采用 GPL-3.0-or-later；修改清单见 [俄语指南](RUSSIAN-README.md)。
- OpenRussian 重音及词形参考：快照 `50e210c4803237779cb562bc1abcea529066031c`，[原始数据](https://github.com/Badestrand/russian-dictionary)，[CC-BY-SA-4.0 许可](assets/glossary/LICENSE-OPENRUSSIAN.txt)。改编方式和使用的词形见 [来源记录](assets/glossary/ru-stress-sources.json)。
- 中俄学习表的代码/配对与参考数据保留各自许可，详见 [词表来源](assets/glossary/README.md)；不把第三方数据重新声明为单一 GPL 数据。
- БКРС 来源与本地使用说明见 [扩展词典文档](docs/notes/russian-dictionaries.md)。

仅作为学习和社区改进用途。俄语版问题请在本仓库反馈；官方版问题请先在官方最新版复现后向上游反馈。
