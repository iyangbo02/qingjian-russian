# 俄语版开发与验证说明

基于 [青简](https://github.com/qingjian-team/qingjian) 上游提交 `c08ae57cb88b6a4a46f4a5e9c1d6d11c5e69222e`，原作者 [@yenharvey](https://github.com/yenharvey) 与青简贡献者。此分支未合并当前上游新版。

## 改动范围

Core 语言枚举、平台配置、macOS/Windows 设置、Linux/Windows 装配和 CLI 增加 `ru`；俄语云端提示、Unicode 重音解析、释义表打包与数据元信息同步。界面生词色改为蓝色，保留 AppKit 系统文字绘制退路。

学习表位于 `assets/glossary/glossary-ru.tsv`（1,656 条），补充候选位于 `assets/glossary/ru-study-dict.tsv`（64 条）。示例：学习 → учи́ться / изуча́ть，词典 → слова́рь，飞机 → самолёт。配对有 AI 辅助，未经完整专业校对，不保证每个义项或重音正确。

词形通常为名词单数主格与动词不定式，不提供自动变格、语音或俄语等级表。未覆盖候选不显示译词。

## macOS 构建

按上游文档安装 Rust 及构建依赖，准备产品数据。此前使用 Rust 1.96.0 构建。

```sh
tools/release/data-fetch.sh
apps/macos/scripts/bundle.sh --pkg
```

若需开发调试包，可用 `PROFILE=debug apps/macos/scripts/bundle.sh --pkg`。产物位于 `target/pkg/`。未配置自己的 Apple 签名与公证时，它是本地开发签名，不是官方安装包。使用上游数据不意味着本分支获得上游认可。

源码打包默认包含小型学习表。大型词典需要自行取得数据并运行 [导入流程](docs/notes/russian-dictionaries.md)。重新安装会覆盖应用资源内自行导入的扩展表，请先备份。

学习语言选俄语；macOS 推荐在 `[general]` 中同时配置 `learning_language = "ru"` 与 `renderer = "system"`。2026-10-24 候选窗有俄语但汉字空白/方框，经切换系统绘制后使用者确认恢复；没有声称已修复位图渲染器根因。俄语和蓝色生词标记保留。

## 验证边界

此前 macOS 编译、本地安装及 CLI 查询已验证；Windows/Linux 接入代码未经本分支各平台实机验证。当前公开版本的测试结果见 `VALIDATION.md`。云端服务需自行配置，尚未完成俄语在线调用验证。

建议运行：

```sh
cargo test --locked -p qingjian-core -p qingjian-platform -p qingjian-translate -p qingjian-predict -p qingjian-render
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/corpus/tests
python3 tools/corpus/glossary_es.py --verify assets/glossary/glossary-ru.tsv
```

完整源代码沿用 GPL-3.0-or-later，OpenRussian 数据改编单独遵循 CC-BY-SA-4.0；上游版权和贡献历史保留。
