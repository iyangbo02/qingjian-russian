# 俄语扩展词典

## 数据分层

`assets/glossary/glossary-ru.tsv` 是 1,656 条学习用词；保留其定向译词和重音。
`tools/corpus/glossary_ru_bkrs.py` 从 [大БКРС 官方下载](https://bkrs.info/p47) 的 gzip DSL 文本导入大规模中俄释义，输出到被 Git 忽略的 `data/generated/bkrs/`。
同词以既有学习表为准，个人释义依旧由 `LayeredTranslator` 优先查询。

每词最多保留两个完整、紧凑的义项：去 DSL 标签、例句与纯交叉引用，保留括号内限制；不截断长句，不把中文释义或拼音当俄语。词条仅收 1–8 个汉字。
俄语重音来自 OpenRussian 的唯一词形候选；变格与词典形合并判歧义。未收录或同形异音的词保留无重音写法，不能声称全部重音已核对。

另导入至多 20,000 个 2–4 字中文候选：需在现有英文通用表中收录、基础中文词库缺失，且官方拼音按字数只有唯一合法切分。底频 5，避免压过原有常用候选。该候选表可通过现有用户词库功能加载，不改核心排序逻辑。

## 重建

在仓库根目录执行（下载日期和文件 URL 需从官网确认）：

```sh
mkdir -p data/external/bkrs
curl -L --fail https://bkrs.info/downloads/daily/dabkrs_261006.gz -o data/external/bkrs/dabkrs_261006.gz
python3 tools/corpus/glossary_ru_bkrs.py \
  --input data/external/bkrs/dabkrs_261006.gz \
  --stress-dir /path/to/russian-dictionary \
  --output-dir data/generated/bkrs
cargo run --locked --release -p qingjian-dict-convert -- \
  --out-dir data/generated/bkrs pack glossary --language ru \
  --input data/generated/bkrs/glossary-ru.tsv \
  --name '青简中俄扩展词典（БКРС 2026-10-06）' \
  --license 'LicenseRef-BKRS AND CC-BY-SA-4.0 AND GPL-3.0-or-later' \
  --attribution '大БКРС bkrs.info 官方下载；OpenRussian 唯一词形重音；原学习表优先'
python3 -m unittest discover -s tools/corpus/tests -p test_glossary_ru_bkrs.py
python3 tools/corpus/glossary_es.py --verify data/generated/bkrs/glossary-ru.tsv
```

OpenRussian 快照：`50e210c4803237779cb562bc1abcea529066031c`，仓库 https://github.com/Badestrand/russian-dictionary。
来源 URL、原文件 SHA256、数量及重音覆盖统计记录在产物 `provenance.json`。

## 本机部署与许可

此数据只用于用户的本地安装。官网的[传播说明](https://bkrs.info/w/бкрс/распространение)称词典开放且可自由传播，但未找到标准 SPDX 许可；不把完整第三方数据提交到代码仓库或公开安装包。
OpenRussian 重音数据为 CC-BY-SA-4.0；既有学习词表许可不变。保留官方说明、来源记录与许可文件。

本机将合并的 `glossary-ru.qj` 原子替换至用户安装的 `Qingjian.app/Contents/Resources/`，并重新签署本地开发签名；中文补充词库放在用户数据 `dicts/bkrs-common.tsv`。部署前备份旧数据。
替换后可临时关闭学习译词、再选择俄语，利用现有配置热加载重读；不需要注销系统。

当前通用打包脚本仍使用仓库内的小型学习表。重装旧包或升级上游应用会覆盖应用内扩展表；需要用本页命令重新部署。原词典与生成文件保存在本机，导入工具可重复使用。

本次导入统计：1,575,086 个合并词条；70,322/91,919 个基础中文词面有俄语释义（76.5%）；新增中文候选 20,000 个。

## 本机译词颜色

生词译文改用蓝色：位图渲染器浅色主题 `#004BA0`，深色主题 `#78BEFF`；macOS 系统绘制退路使用系统蓝色。所有学习语言共用生词配色，熟词仍为灰色。部署时只替换可执行文件并重新签名，保留扩展词库；重启输入法进程即可加载，无需注销。

2026-10-24：用户报告候选窗仍有俄语，但汉字空白或方框。独立位图预览可正常显示汉字，未确认运行中故障的根因。本机 `[general]` 设置 `renderer = "system"` 并重启输入法，改走 AppKit 字体回退；用户确认显示恢复。俄语语言设置、扩展词库与蓝色生词样式保留。恢复位图路径需先进一步验证字体加载和运行时字形缓存。
