#!/usr/bin/env python3
"""Install a private CPU runtime and download a pinned RUAccent model snapshot."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVISION = 'b78ae5ea1e62beaf138bed1865cd8c3b0b5ca855'
DEPENDENCIES = [
    'transformers==4.44.2', 'huggingface-hub==0.25.2',
    'onnxruntime==1.23.2', 'numpy==1.26.4',
    'sentencepiece==0.2.1', 'python-crfsuite==0.9.12', 'razdel==0.5.0',
]


def download(runtime):
    from huggingface_hub import snapshot_download
    import ruaccent
    models = runtime / 'models'
    print('Downloading pinned RUAccent CPU assets (approximately 725 MB)…', file=sys.stderr)
    snapshot_download(
        'ruaccent/accentuator', revision=REVISION, local_dir=str(models),
        local_dir_use_symlinks=False, max_workers=4,
        allow_patterns=['dictionary/*', 'dictionary/rule_engine/*',
                        'nn/nn_accent/*', 'nn/nn_stress_usage_predictor/*',
                        'nn/nn_yo_homograph_resolver/*', 'nn/nn_omograph/turbo3.1/*',
                        'koziev/*'],
    )
    module = Path(ruaccent.__file__).resolve().parent
    shutil.copytree(models / 'koziev', module / 'koziev', dirs_exist_ok=True)
    (runtime / 'ready.json').write_text(json.dumps({
        'model_revision': REVISION, 'model': 'turbo3.1', 'device': 'CPU',
    }, indent=2) + '\n')
    print('CPU runtime ready.', file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, default=ROOT / '.runtime')
    parser.add_argument('--download-only', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    runtime.mkdir(parents=True, exist_ok=True)
    if args.download_only:
        download(runtime)
        return
    uv = shutil.which('uv')
    if not uv:
        raise SystemExit('uv is required. Install uv, then rerun this script; Python 3.11 is used for the private runtime.')
    env = runtime / 'venv'
    subprocess.run([uv, 'venv', '--python', '3.11', str(env)], check=True)
    python = env / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    # The PyPI release pins transformers 4.12.2: its tokenizer lacks Apple Silicon
    # wheels. Install the same RUAccent release with this tested ONNX-only stack.
    subprocess.run([uv, 'pip', 'install', '--python', str(python), '--no-deps',
                    'ruaccent==1.5.8.3'], check=True)
    subprocess.run([uv, 'pip', 'install', '--python', str(python), *DEPENDENCIES], check=True)
    subprocess.run([str(python), str(Path(__file__).resolve()), '--runtime', str(runtime),
                    '--download-only'], check=True)


if __name__ == '__main__':
    main()
