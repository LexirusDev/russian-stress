"""Formatting and annotation regressions; no model download required."""
import re
import unittest
from accentuate import ACUTE, WORD, accentuate, display_word


class FakeEngine:
    omographs = {'замок': ['з+амок', 'зам+ок']}
    skill_custom_dict = {}

    def process_all(self, text):
        mapping = {'привет': 'прив+ет', 'молоко': 'молок+о', 'люблю': 'любл+ю',
                   'замок': 'зам+ок', 'елка': '+ёлка', 'я': '+я', 'русский': 'р+усский'}
        return WORD.sub(lambda m: mapping.get(m.group().lower(), m.group()), text)


class AnnotationTests(unittest.TestCase):
    def test_format_preservation_and_code_urls(self):
        source = '# 学习 **Привет**!\r\n| 词 | Молоко |\r\n`привет` https://example.com/привет\r\n```ru\r\nмолоко\r\n```\r\n[Привет](https://example.com/молоко)\r\n'
        result, _ = accentuate(source, FakeEngine())
        expected = source.replace('**Привет**', '**Приве́т**').replace('| Молоко |', '| Молоко́ |').replace('[Привет]', '[Приве́т]')
        self.assertEqual(result, expected)

    def test_explicit_stress_and_idempotency(self):
        source = 'Я лю́блю молоко. Молоко́!'
        result, _ = accentuate(source, FakeEngine())
        self.assertEqual(result, 'Я лю́блю молоко́. Молоко́!')
        self.assertEqual(accentuate(result, FakeEngine())[0], result)

    def test_yo_case_and_monosyllables(self):
        self.assertEqual(display_word('ЕЛКА', '+ёлка'), 'ЁЛКА')
        self.assertEqual(display_word('елка', '+ёлка', keep_yo=False), 'е́лка')
        self.assertEqual(display_word('Я', '+я'), 'Я')
        self.assertEqual(display_word('Я', '+я', mark_monosyllables=True), 'Я́')
        self.assertEqual(display_word('ё́лка', '+ёлка'), 'ё́лка')

    def test_engine_cannot_rewrite_text(self):
        class BadEngine(FakeEngine):
            def process_all(self, text):
                return 'м+ама'
        with self.assertRaises(ValueError):
            accentuate('Молоко', BadEngine())
        with self.assertRaises(ValueError):
            display_word('молоко', '+молоко')

    def test_review_and_override(self):
        engine = FakeEngine()
        result, review = accentuate('замок', engine)
        self.assertEqual(result, 'замо́к')
        self.assertEqual(review[0]['word'], 'замок')
        engine.skill_custom_dict = {'замок': 'з+амок'}
        self.assertEqual(accentuate('Замок', engine)[0], 'За́мок')

    def test_no_russian(self):
        self.assertEqual(accentuate('中文 only 🐈\n', FakeEngine()), ('中文 only 🐈\n', []))

    def test_long_line_and_skeleton(self):
        source = ('Молоко 🐈\t' * 170) + '\n'
        result, _ = accentuate(source, FakeEngine())
        self.assertEqual(result.replace(ACUTE, ''), source)
        self.assertEqual(result.count(ACUTE), 170)


if __name__ == '__main__':
    unittest.main()
