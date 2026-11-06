# coding: utf-8
"""词典导入时的语义边界、格式与拼音校验。"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('bkrs', Path(__file__).parents[1] / 'glossary_ru_bkrs.py')
bkrs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bkrs)


class ImportTests(unittest.TestCase):
    def test_compact_senses_keep_qualifiers_and_drop_examples(self):
        self.assertEqual(bkrs.compact_senses('[m1]1) ключ (для двери); 2) источник[/m][ex]例句 пример[/ex]'),
                         ['ключ (для двери)', 'источник'])

    def test_references_and_long_definitions_are_not_truncated(self):
        self.assertEqual(bkrs.compact_senses('[m1][ref]词条[/ref][/m]'), [])
        self.assertEqual(bkrs.compact_senses('[m1]' + 'длинное ' * 30 + '[/m]'), [])

    def test_pinyin_is_removed_and_partial_qualifiers_are_rejected(self):
        self.assertEqual(bkrs.compact_senses('[m1]jiàoxué обучение[/m]'), ['обучение'])
        self.assertEqual(bkrs.compact_senses('[m1]ключ (для; двери)[/m]'), [])

    def test_pinyin_requires_unambiguous_character_alignment(self):
        syllables = {'zhong', 'guo', 'xi', 'an', 'xian', 'x', 'ian'}
        self.assertEqual(bkrs.pinyin_split('zhōngguó', 2, syllables), 'zhong guo')
        self.assertEqual(bkrs.pinyin_split('xiān', 1, syllables), 'xian')
        self.assertIsNone(bkrs.pinyin_split('xiān', 2, syllables))
        self.assertIsNone(bkrs.pinyin_split('_', 2, syllables))

    def test_stress_index_retains_homograph_ambiguity(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'words.csv').write_text("bare\taccented\tform\nзамок\tза'мок\tзамо'к\n")
            self.assertEqual(bkrs.stress_index(Path(directory))['замок'], {'за́мок', 'замо́к'})


if __name__ == '__main__':
    unittest.main()
