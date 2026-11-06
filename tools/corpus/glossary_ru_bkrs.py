#!/usr/bin/env python3
# coding: utf-8
"""从官方 БКРС DSL 导入紧凑中俄释义；既有学习词表优先，重音不猜同形异音。

输入为官方 gzip 文本；输出只放 data/generated，不覆盖人工学习表。
例：python3 tools/corpus/glossary_ru_bkrs.py --input data/external/bkrs/dabkrs_261006.gz \
    --stress-dir /path/to/russian-dictionary --output-dir data/generated/bkrs
"""
import argparse
import csv
import gzip
import hashlib
import json
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from pathlib import Path

CYRILLIC = re.compile(r'[А-Яа-яЁё\u0301]+')
HAN = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff]{1,8}')
TAG = re.compile(r'\[[^\]]*\]')

# БКРС 的首义可能偏旧；对实际抽查发现的常用义问题作显式校正。
CONTEXT_OVERRIDES = {'整合': ['v. интегри́ровать', 'n. интегра́ция']}


def blocks(path):
    """官方 DSL 条目由空行分隔；指令块不当词条。"""
    with gzip.open(path, 'rt', encoding='utf-8-sig') as f:
        block = []
        for line in f:
            if line.strip():
                block.append(line.rstrip('\n'))
            elif block:
                yield block
                block = []
        if block:
            yield block


def compact_senses(markup):
    # 例句、链接不是释义；保留括号中的领域限制，避免把限定义变成普遍义。
    markup = re.sub(r'\[ex\].*?\[/ex\]', '', markup, flags=re.S)
    parts = re.split(r'\[m\d+\]|\[/m\]|;|\s+\d+\)\s*', markup)
    senses = []
    for part in parts:
        part = re.sub(r'\[ref(?: [^\]]*)?\].*?\[/ref\]', '', part, flags=re.S)
        text = TAG.sub('', part).replace('~', '').replace('|', '/')
        text = re.sub(r'^\s*\d+[).]\s*', '', text)
        text = re.sub(r'\s+', ' ', text).strip(' ,;')
        # 某些义项自身带中文读音（如 jiàoxué），不是俄语译词。
        first, separator, rest = text.partition(' ')
        if separator and re.search('[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]', first):
            text = rest.strip()
        # 不截断长句；只保留完整的紧凑义项，避免词典正文挤满候选窗。
        if not 2 <= len(text) <= 90 or len(text.split()) > 12:
            continue
        if not CYRILLIC.search(text) or re.search(r'[\u3400-\u9fff<>\\]', text):
            continue
        if text.count('(') != text.count(')'):
            continue
        if text.startswith(('см.', 'ср.', 'то же,', 'то же что')):
            continue
        if text not in senses:
            senses.append(text)
        if len(senses) == 2:
            break
    return senses


def stress_index(directory):
    lemmas, forms = {}, {}

    def add(index, value):
        if not re.fullmatch(r"[А-Яа-яЁё']+", value):
            return
        key = value.replace("'", '').lower()
        accented = value.replace("'", '\u0301').lower()
        if sum(c in 'аеёиоуыэюя' for c in key) <= 1 or 'ё' in key:
            accented = key
        elif '\u0301' not in accented:
            return
        index.setdefault(key, set()).add(accented)

    for path in sorted(directory.glob('*.csv')):
        with path.open() as f:
            for row in csv.DictReader(f, delimiter='\t'):
                add(lemmas, row['accented'])
                for field, value in row.items():
                    if field in ('bare', 'translations_en', 'translations_de', 'partner'):
                        continue
                    if isinstance(value, str):
                        for variant in re.split('[,;/]', value):
                            add(forms, variant.strip())
    # 不优先假设某词是主格：同形异音也可能来自其他词的变格。
    for key, options in lemmas.items():
        forms.setdefault(key, set()).update(options)
    return forms


def pinyin_split(source, count, syllables):
    """按声调位置和汉字数校验读音；有多种切分就不导入中文候选。"""
    toned = []
    for c in source.lower():
        normalized = unicodedata.normalize('NFD', c)
        base = normalized[0]
        if base == 'u' and '\u0308' in normalized:
            base = 'v'
        if base.isascii() and base.isalpha():
            toned.append((base, any(t in normalized for t in '\u0300\u0301\u0304\u030c')))
        elif c in " '\u2019-":
            continue
        else:
            return None
    letters = ''.join(c for c, _ in toned)

    @lru_cache(None)
    def visit(start, remaining):
        if not remaining:
            return [()] if start == len(letters) else []
        result = []
        for end in range(start + 1, min(len(letters), start + 6) + 1):
            syl = letters[start:end]
            if syl not in syllables or sum(t for _, t in toned[start:end]) > 1:
                continue
            for suffix in visit(end, remaining - 1):
                result.append((syl,) + suffix)
                if len(result) > 1:
                    return result
        return result

    choices = visit(0, count)
    return ' '.join(choices[0]) if len(choices) == 1 else None


def run(args):
    args.output_dir.mkdir(parents=True, exist_ok=True)
    curated = {}
    for line in args.curated.read_text().splitlines():
        if line and not line.startswith('#'):
            word, *senses = line.split('\t')
            curated[word] = senses
    stress = stress_index(args.stress_dir)
    stats = Counter()
    unresolved = Counter()

    def accent(match):
        word = match[0]
        key = word.lower()
        if '\u0301' in key or 'ё' in key or sum(c in 'аеёиоуыэюя' for c in key) <= 1:
            return word
        options = stress.get(key, set())
        if len(options) != 1:
            unresolved[key] += 1
            stats['unresolved_tokens'] += 1
            return word
        stats['accented_tokens'] += 1
        value = next(iter(options))
        return value[0].upper() + value[1:] if word[0].isupper() else value

    base_words = {line.split('\t')[0] for line in args.base_dict.read_text().splitlines()
                  if line and not line.startswith('#')}
    english_words = {line.split('\t')[0] for line in args.english.read_text().splitlines()
                     if line and not line.startswith('#')}
    syllables = set(re.findall(r'"([a-z]+)"', args.syllables.read_text()))
    imported, candidate_pool = {}, {}
    for block in blocks(args.input):
        stats['source_blocks'] += 1
        word = block[0]
        if len(block) != 3 or not HAN.fullmatch(word) or word in curated or word in imported:
            continue
        senses = compact_senses(block[2])
        if not senses:
            continue
        imported[word] = [CYRILLIC.sub(accent, s) for s in senses]
        # 只补英文通用表也收录的短词；低底频，不挤掉常用输入候选。
        if 2 <= len(word) <= 4 and word not in base_words and word in english_words:
            py = pinyin_split(block[1].strip(), len(word), syllables)
            if py:
                candidate_pool[word] = py
    imported.update({word: senses for word, senses in CONTEXT_OVERRIDES.items()
                     if word not in curated})
    combined = {**imported, **curated}
    for filename, rows in [('glossary-bkrs-ru.tsv', imported), ('glossary-ru.tsv', combined)]:
        with (args.output_dir / filename).open('w') as f:
            f.write('# 大БКРС 官方数据 + OpenRussian 无歧义重音；来源与限制见 provenance.json。\n')
            for word in sorted(rows):
                f.write(word + '\t' + '\t'.join(rows[word]) + '\n')
    candidates = sorted(candidate_pool, key=lambda w: (len(w), w))[:args.candidate_limit]
    with (args.output_dir / 'bkrs-common.tsv').open('w') as f:
        f.write('# БКРС 拼音；仅补通用英文表也收录的中文短词；词频 5。\n')
        for word in candidates:
            f.write(word + '\t' + candidate_pool[word] + '\t5\n')
    stats.update({'imported_entries': len(imported), 'curated_entries': len(curated),
                  'total_entries': len(combined), 'base_dictionary_words': len(base_words),
                  'base_words_with_russian_before': len(base_words & curated.keys()),
                  'base_words_with_russian_after': len(base_words & combined.keys()),
                  'new_chinese_candidates': len(candidates)})
    provenance = {'dictionary_source': args.source_url,
                  'dictionary_download': 'https://bkrs.info/p47',
                  'dictionary_terms': 'https://bkrs.info/w/бкрс/распространение',
                  'dictionary_license': 'LicenseRef-BKRS-official-distribution-statement',
                  'dictionary_note': '官网称开放且可自由传播；未发现标准 SPDX 许可。第三方数据不提交到仓库或公开发行包。',
                  'source_sha256': hashlib.sha256(args.input.read_bytes()).hexdigest(),
                  'stress_source': 'https://github.com/Badestrand/russian-dictionary',
                  'stress_revision': '50e210c4803237779cb562bc1abcea529066031c',
                  'stress_license': 'CC-BY-SA-4.0',
                  'modifications': '去 DSL 标签；最多两个完整短义项；按唯一词形重音补标；同形异音或未收录词不猜；既有学习表优先。',
                  'context_overrides': CONTEXT_OVERRIDES,
                  'stats': dict(stats), 'frequent_unstressed': unresolved.most_common(100)}
    (args.output_dir / 'provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(stats), ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--source-url', default='https://bkrs.info/downloads/daily/dabkrs_261006.gz')
    parser.add_argument('--stress-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--curated', type=Path, default=Path('assets/glossary/glossary-ru.tsv'))
    parser.add_argument('--base-dict', type=Path, default=Path('assets/lexicon/dict.tsv'))
    parser.add_argument('--english', type=Path, default=Path('assets/glossary/glossary-en.tsv'))
    parser.add_argument('--syllables', type=Path, default=Path('crates/qingjian-core/src/parser/syllable.rs'))
    parser.add_argument('--candidate-limit', type=int, default=20000)
    run(parser.parse_args())


if __name__ == '__main__':
    main()
