#!/usr/bin/env python3
"""Add Russian stress marks while projecting only annotations onto original text."""
import argparse
import contextlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACUTE = '\u0301'
WORD = re.compile(r'[А-Яа-яЁё]+(?:\u0301[А-Яа-яЁё]*)*')
ENGINE_WORD = re.compile(r'[+А-Яа-яЁё\u0301]+')
VOWELS = 'аеёиоуыэюя'
# Protect code, links' destinations, URLs, email addresses and HTML tags.
# This covers ordinary chat Markdown, not every dialect of Markdown or HTML.
PROTECTED = re.compile(
    r'(?ms)^\s*```[^\n]*\n.*?^\s*```[^\n]*$'
    r'|^\s*~~~[^\n]*\n.*?^\s*~~~[^\n]*$'
    r'|(`+)[^\n]*?\1'
    r'|!?\[[^\]\n]*\]\([^\n]*?\)'
    r'|https?://[^\s<>]+'
    r'|[\w.+-]+@[\w.-]+\.[\w-]+'
    r'|<[^>\n]*>'
    r'|^ {4}[^\n]*$'
    r'|^\s*\[[^\]\n]+\]:[^\n]*$'
)


def base(word):
    return word.replace('+', '').replace(ACUTE, '').lower().replace('ё', 'е')


def display_word(original, annotated, keep_yo=True, mark_monosyllables=False):
    if ACUTE in original:  # Explicit human annotations are authoritative.
        return original
    letters, stress = [], set()
    pending = False
    for char in annotated:
        if char == '+':
            pending = True
        elif char == ACUTE:
            if not letters or letters[-1].lower() not in VOWELS:
                raise ValueError('Engine stress mark does not follow a vowel')
            stress.add(len(letters) - 1)
        else:
            if pending:
                if char.lower() not in VOWELS:
                    raise ValueError('Engine stress mark does not precede a vowel')
                stress.add(len(letters))
            letters.append(char)
            pending = False
    if pending or base(original) != base(''.join(letters)) or len(original) != len(letters):
        raise ValueError('Engine changed a word; refusing to replace the source text')
    monosyllable = sum(c.lower() in VOWELS for c in original) <= 1
    output = []
    for index, char in enumerate(original):
        if keep_yo and char.lower() == 'е' and letters[index].lower() == 'ё':
            char = 'Ё' if char.isupper() else 'ё'
        output.append(char)
        # ё already shows the vowel; preserve manual stress above, but do not add it.
        if index in stress and char.lower() != 'ё' and (mark_monosyllables or not monosyllable):
            output.append(ACUTE)
    return ''.join(output)


def protected_mask(text):
    mask = [False] * len(text)
    for match in PROTECTED.finditer(text):
        start, end = match.span()
        # A Markdown link label is readable text; only its destination is protected.
        if re.match(r'!?\[', match.group()):
            start = text.index('](', start, end) + 1
        mask[start:end] = [True] * (end - start)
    return mask


def accentuate(text, engine, keep_yo=True, mark_monosyllables=False):
    mask = protected_mask(text)
    edits, review = [], []
    # Keep each source line independent so rows and bilingual pairs do not mix.
    offset = 0
    for line in text.splitlines(keepends=True):
        words = [m for m in WORD.finditer(line)
                 if not any(mask[offset + m.start():offset + m.end()])]
        # Bound context length rather than silently truncating long model inputs.
        for start in range(0, len(words), 80):
            chunk = words[start:start + 80]
            left = 0 if start == 0 else chunk[0].start()
            right = words[start + 80].start() if start + 80 < len(words) else len(line)
            context = list(line[left:right])
            allowed = set(' —.,!?:;\"\'()«»')
            for i, char in enumerate(context):
                if char == ACUTE:
                    context[i] = ''
                elif mask[offset + left + i] or (not re.fullmatch(r'[А-Яа-яЁё]', char) and char not in allowed):
                    context[i] = ' '
            result = engine.process_all(''.join(context))
            annotated = list(ENGINE_WORD.finditer(result))
            if len(annotated) != len(chunk) or any(
                base(a.group()) != base(b.group()) for a, b in zip(chunk, annotated)
            ):
                raise ValueError('RUAccent changed word sequence; no output was written')
            for source, prediction in zip(chunk, annotated):
                key = source.group().replace(ACUTE, '').lower()
                explicit = getattr(engine, 'skill_custom_dict', {}).get(key)
                value = display_word(source.group(), explicit or prediction.group(), keep_yo, mark_monosyllables)
                edits.append((offset + source.start(), offset + source.end(), value))
                variants = getattr(engine, 'omographs', {}).get(key, [])
                if ACUTE not in source.group() and variants:
                    review.append({'word': source.group(), 'result': value,
                                   'offset': offset + source.start(),
                                   'reason': 'homograph; context-based prediction, not a guarantee',
                                   'variants': variants})
                elif ACUTE not in source.group() and sum(c.lower() in VOWELS for c in value) > 1 and ACUTE not in value and 'ё' not in value.lower():
                    review.append({'word': source.group(), 'result': value,
                                   'offset': offset + source.start(), 'reason': 'no stress returned'})
        offset += len(line)
    parts, last = [], 0
    for start, end, replacement in edits:
        parts.extend((text[last:start], replacement))
        last = end
    parts.append(text[last:])
    return ''.join(parts), review


def load_engine(runtime, dictionary=None):
    if not (runtime / 'ready.json').exists():
        raise ValueError('Runtime is not ready. Run scripts/setup_runtime.py first.')
    # No text is sent to Hugging Face. Require the downloaded assets, even offline.
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    from ruaccent import RUAccent
    custom = json.loads(dictionary.read_text(encoding='utf-8')) if dictionary else {}
    if not isinstance(custom, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in custom.items()):
        raise ValueError('Custom dictionary must be a JSON object mapping words to +marked forms')
    engine = RUAccent()
    engine.load(omograph_model_size='turbo3.1', use_dictionary=True,
                tiny_mode=False, device='CPU', workdir=str(runtime / 'models'),
                custom_dict=custom)
    # Apply explicit corrections after the engine's homograph resolver as well.
    engine.skill_custom_dict = custom
    return engine


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--text')
    source.add_argument('--input', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--runtime', type=Path, default=ROOT / '.runtime')
    parser.add_argument('--custom-dict', type=Path)
    parser.add_argument('--keep-e', action='store_true', help='Do not restore е to ё')
    parser.add_argument('--mark-monosyllables', action='store_true')
    args = parser.parse_args()
    try:
        # Keep CRLF and every other original separator, including in output files.
        text = args.text if args.text is not None else (args.input.read_bytes().decode('utf-8') if args.input else sys.stdin.read())
        with contextlib.redirect_stdout(sys.stderr):
            engine = load_engine(args.runtime.resolve(), args.custom_dict)
            result, review = accentuate(text, engine, not args.keep_e, args.mark_monosyllables)
        if args.output:
            args.output.write_bytes(result.encode('utf-8'))
        else:
            sys.stdout.write(result)
        if args.report:
            args.report.write_text(json.dumps({'review_candidates': review,
                'note': 'Candidates for review, not calibrated confidence scores.'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        elif review:
            print(f'\n{len(review)} word(s) may need review; use --report for details.', file=sys.stderr)
    except (ValueError, ImportError, OSError) as error:
        print(f'russian-stress: {error}', file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
