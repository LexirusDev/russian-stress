#!/usr/bin/env python3
"""Real CPU checks; run with the private runtime's Python after setup."""
import argparse
import json
import time
from pathlib import Path
from accentuate import ROOT, ACUTE, accentuate, load_engine


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, default=ROOT / '.runtime')
    args = parser.parse_args()
    started = time.monotonic()
    engine = load_engine(args.runtime.resolve())
    loaded = time.monotonic()
    cases = [
        ('Я люблю русский язык!', 'Я люблю́ ру́сский язы́к!'),
        ('На двери висит замок.', 'На двери́ виси́т замо́к.'),
        ('На горе стоит старый замок.', 'На горе́ стои́т ста́рый за́мок.'),
        ('Елка растет в лесу.', 'Ёлка растёт в лесу́.'),
    ]
    results = []
    for source, expected in cases:
        result, _ = accentuate(source, engine)
        assert result == expected, (source, result, expected)
        results.append({'input': source, 'output': result})
    mixed = '# 学习 **Привет**! 🐈\r\n| 中文 | Я люблю русский язык! |\r\n`молоко` https://example.com/молоко\r\n```ru\r\nмолоко\r\n```\r\n[молоко](https://example.com/молоко)\r\n已有：молоко́\r\n'
    result, _ = accentuate(mixed, engine)
    assert result.replace(ACUTE, '') == mixed.replace(ACUTE, '')
    assert '`молоко`' in result and '```ru\r\nмолоко\r\n```' in result
    assert '[молоко́](https://example.com/молоко)' in result
    assert accentuate(result, engine)[0] == result
    results.append({'input': mixed, 'output': result})
    print(json.dumps({'status': 'passed', 'device': 'CPU', 'offline': True,
                      'load_seconds': round(loaded - started, 2),
                      'inference_seconds': round(time.monotonic() - loaded, 2),
                      'results': results}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
