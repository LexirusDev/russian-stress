# CPU runtime and provenance

- RUAccent: https://github.com/Den4ikAI/ruaccent
- Models: https://huggingface.co/ruaccent/accentuator
- Paper: https://aclanthology.org/2025.coling-main.444/
- Fixed package: `ruaccent==1.5.8.3`; model: `turbo3.1`, dictionary and full rule pipeline enabled.
- Fixed model snapshot: `b78ae5ea1e62beaf138bed1865cd8c3b0b5ca855`.

The PyPI release pins an old Transformers/tokenizers stack. The setup helper installs RUAccent without those obsolete dependencies and installs a tested ONNX-only stack separately. This is intentional: ordinary `pip install ruaccent` can try to compile tokenizers on Apple Silicon. No PyTorch, CUDA, or GPU is needed. A Transformers warning about missing training frameworks is expected; ONNX inference is used instead.

Use Python 3.11 and uv. The helper creates `.runtime/venv`, downloads model assets to `.runtime/models`, and copies the upstream rule engine resources into the installed package's `koziev` directory. Downloads are pinned and resumable. The ready marker is written only after all downloads and copies finish. To repair incomplete setup, rerun the helper; do not create the marker manually. Model assets are about 725 MB (about 693 MiB); total environment and disk usage are larger. Loading the complete dictionaries also uses additional RAM.

For a source checkout or a copied skill, run:

```sh
python3 scripts/setup_runtime.py
.runtime/venv/bin/python scripts/accentuate.py --text 'Я люблю русский язык!'
```

Each skill installation has its own private runtime by default. A custom runtime can be supplied with `--runtime /absolute/path` to both helpers; execute accentuate.py using that runtime's Python interpreter. After complete setup, inference sets `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`; source text is processed locally.

Run wrapper regressions without downloading models:

```sh
python3 scripts/test_accentuate.py
```

Run the actual CPU integration checks after setup:

```sh
.runtime/venv/bin/python scripts/smoke_test.py
```

The wrapper preserves formatting by aligning Russian word tokens and adding annotations to the original string. It processes lines separately and bounds long lines to 80-word chunks; cross-line or distant context is therefore limited. Markdown protection covers ordinary fenced/indented code, inline code, links and URLs, not a complete CommonMark parser. Review homographs in short or ambiguous text. Arbitrary Unicode combining marks other than the supported U+0301, nested Markdown destinations, and non-Russian Cyrillic languages need separate handling.

The skill wrapper is separate from the upstream engine and assets. Upstream currently advertises MIT in its repository, while the pinned PyPI metadata still says Apache-2.0; the model repository has separate metadata. Nothing from those packages or model assets is redistributed in this skill source. Consult the exact upstream licenses before redistributing engines, dictionaries or model weights.
