# 俄语重音 · Russian Stress

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![macOS Apple Silicon](https://img.shields.io/badge/macOS-Apple_Silicon-black?logo=apple&logoColor=white)
![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)

给俄语文本自动标注重音的 [Codex](https://github.com/openai/codex) skill：基于 [RUAccent](https://github.com/Den4ikAI/ruaccent) 在本地 CPU 推理（Apple Silicon Mac），装好后离线可用，无需联网。

*A Codex skill that adds Russian stress marks on request, using RUAccent with local CPU inference on Apple Silicon Macs. No network needed after setup.*

中文可以说："用俄语重音技能给这段俄语标重音"；也可以显式调用 `$russian-stress`。

```text
Я люблю русский язык! → Я люблю́ ру́сский язы́к!
На двери висит замок. → На двери́ виси́т замо́к.
На горе стоит старый замок. → На горе́ стои́т ста́рый за́мок.
Елка растет в лесу. → Ёлка растёт в лесу́.
```

## 适用人群

- 俄语学习者 / 教师：备课、制作练习材料时批量标重音
- 用 Codex 处理俄语文本的开发者

## 功能

- 本地 CPU 推理（Apple Silicon），装好后完全离线
- Unicode 重音符号、ё 还原
- 中俄双语混合文本
- 保留基础 Markdown 格式
- 尊重已有的手标重音
- 同形异义（омографы）输出复核报告

## 安装

把本目录复制到 Codex skills 目录并命名为 `russian-stress`（通常是 `~/.codex/skills/russian-stress`），保证 `SKILL.md` 直接在该目录下。有 [uv](https://docs.astral.sh/uv/) 的话，在 skill 目录里运行：

```sh
python3 scripts/setup_runtime.py
.runtime/venv/bin/python scripts/accentuate.py \
  --input input.md --output accented.md --report review.json
```

安装需要 Python 3.11，会下载约 725 MB 的固定版本资源并创建独立环境；之后推理走本地缓存，完全离线。运行时和模型权重不进 Git。

```sh
python3 scripts/test_accentuate.py
.runtime/venv/bin/python scripts/smoke_test.py
```

Agent 工作流见 [SKILL.md](SKILL.md)，依赖与限制见 [runtime notes](references/runtime.md)。这是一个 Codex skill，不是独立 GUI 应用，也不是 iOS 集成。

## 局限

模型预测可能出错，短文本和专有名词需要人工复核。普通的俄语生成不会触发它，只有明确要求标重音时才工作。

## 上游与许可证

Wrapper 本体 MIT 许可证。RUAccent 及其模型/词典资源遵循各自上游许可证，需单独下载，不包含在本仓库中。

- [RUAccent](https://github.com/Den4ikAI/ruaccent)
- [Model assets](https://huggingface.co/ruaccent/accentuator)
- [RUAccent paper, COLING 2025](https://aclanthology.org/2025.coling-main.444/)
