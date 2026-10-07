# 俄语重音 · Russian Stress

A Codex skill that uses **RUAccent on CPU** to add Russian stress marks on request. 中文可以说：“用俄语重音技能给这段俄语标重音”；也可以显式调用 `$russian-stress`。

```text
Я люблю русский язык! → Я люблю́ ру́сский язы́к!
На двери висит замок. → На двери́ виси́т замо́к.
На горе стоит старый замок. → На горе́ стои́т ста́рый за́мок.
Елка растет в лесу. → Ёлка растёт в лесу́.
```

Supports local CPU inference on Apple Silicon Mac, Unicode accents, ё restoration, bilingual text, basic Markdown preservation, existing manual accents, and review reports for known homographs. Ordinary Russian generation does not activate it unless stress marking is requested. Predictions can be wrong; short entries and proper names need review.

## Install

Copy this directory into your Codex skills directory as `russian-stress` (normally `~/.codex/skills/russian-stress`), with `SKILL.md` directly inside it. With [uv](https://docs.astral.sh/uv/) available, run from the skill directory:

```sh
python3 scripts/setup_runtime.py
.runtime/venv/bin/python scripts/accentuate.py \
  --input input.md --output accented.md --report review.json
```

Setup uses Python 3.11, downloads approximately 725 MB of pinned assets, and creates a private environment. Subsequent inference uses the local cache offline. The runtime and model weights are excluded from Git.

```sh
python3 scripts/test_accentuate.py
.runtime/venv/bin/python scripts/smoke_test.py
```

Read [SKILL.md](SKILL.md) for the agent workflow and [runtime notes](references/runtime.md) for dependencies and limitations. This is a Codex skill, not a standalone GUI app or an iOS integration.

## Upstream and license

The wrapper is licensed under MIT. RUAccent and its model/dictionary assets have their own upstream licenses and are downloaded separately; they are not included in this repository.

- [RUAccent](https://github.com/Den4ikAI/ruaccent)
- [Model assets](https://huggingface.co/ruaccent/accentuator)
- [RUAccent paper, COLING 2025](https://aclanthology.org/2025.coling-main.444/)
