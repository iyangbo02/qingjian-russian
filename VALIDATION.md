# 公开源码验证

2026-11-06，在 macOS Apple Silicon 上对本公开工作树执行：

- `cargo test --locked -p qingjian-core -p qingjian-platform -p qingjian-translate -p qingjian-predict -p qingjian-render`：383 项 Rust 测试通过，无失败。
- БКРС 导入器：5 项 Python 测试通过。
- 俄语学习 TSV：1,656 条合法、0 条错误。
- `git diff --check`：通过。

这些检查不代表 Windows/Linux 实机验证，也不代表词表经过专业译者完整校对。大型词典全文不在本仓库。

安装提示更新（2026-11-06）：两个 shell 安装入口通过 `bash -n`；macOS `--pkg` / `--install` 以假 cargo 在构建前终止，确认提示实际打印且未安装应用；Linux 以无效前缀在写入前终止，确认提示打印。Windows 完成页只检查源码，未构建或实机验证。
