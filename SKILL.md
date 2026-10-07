---
name: russian-stress
description: 使用 RUAccent 为俄语内容标注重音并恢复 ё。用户要求“俄语重音”“俄语标重音”“带重音的俄语”“用俄语重音的技能”或 Russian stress/accent 时使用，支持生成后的句子、词汇例句和学习材料；仅生成普通俄语而未要求重音时不启用。
---

# 俄语重音 / Russian Stress

在用户需要时，对最终俄语内容调用本地 RUAccent CPU 引擎，输出元音后的 Unicode 组合锐音符 U+0301（如 молоко́）。目录名和显式调用名为 `russian-stress`，中文名称为“俄语重音”。

## 使用

先完成俄语措辞，再标注。提供完整句子作为上下文；不要为节省时间逐词调用。引擎只能预测，同形异音词、专名、孤立词条需要结合用户想表达的意思复核。

以此 SKILL.md 所在目录为 `SKILL_DIR`；不要依赖最初开发机器的绝对路径。

初次使用若 `.runtime/ready.json` 或 `.runtime/venv/bin/python` 不存在：

```sh
python3 "$SKILL_DIR/scripts/setup_runtime.py"
```

需要 uv、Python 3.11；setup 会建立独立环境、固定 RUAccent 与主要依赖版本，并下载固定版本的约 725 MB 模型和词典。安装失败时说明具体错误，不把模型自行猜测的结果冒充工具输出。运行文件、缓存和模型均不应提交到 Git。

使用 UTF-8 文件传入文本，避免把用户内容拼进 shell 命令。输入输出路径放在当前任务的临时工作目录，若需要交付文件再放入任务 outputs：

```sh
"$SKILL_DIR/.runtime/venv/bin/python" "$SKILL_DIR/scripts/accentuate.py" \
  --input input.md --output accented.md --report review.json
```

也支持标准输入或 `--text`；后者只用于可以安全传参的短例句。推理固定使用 CPU 和本地资产，默认禁用 Hugging Face 联网。短文不需要常驻服务；批量材料尽量一次处理，减少重复加载模型。

## 输出与复核

- 只添加重音和将必要的 е 恢复为 ё；保留中文、其他语言、大小写、标点、空白及基本 Markdown 结构。脚本把模型标注投射回原文；模型改写词序或拼写时拒绝输出。
- 保留用户已标的重音。普通单音节词默认不新增重音，ё 默认不再叠加锐音符；用户需要时用 `--mark-monosyllables`，需要保留原来的 е 拼写时用 `--keep-e`。
- 代码块、行内代码、URL、链接地址、邮箱和 HTML 标签不参与标注；链接显示文字可以标注。复杂 HTML、LaTeX、DOCX 或 EPUB 需先提取俄语正文再回填，此脚本不是这些格式的解析器。
- 查看 `review.json` 的 `review_candidates`：包含引擎词典识别的同形异音词及未标出的多音节词。这不是校准置信度，也不能发现全部错误。重点复核短词条、不同词义和人名。上下文不足而意思不清楚时保留候选读音或简短询问，不随意选一个。
- 手工修正优先在原文加 Unicode 重音再处理；这可以限定到某一次出现。`--custom-dict corrections.json` 接受如 `{"москва": "москв+а"}` 的全局词形覆盖；不要用全局覆盖固定歧义词的一个意思。
- 标注完成后直接返回需要的俄语内容；只有存在相关歧义、工具失败或用户要求验证细节时附说明。不在普通输出中展示 `+`、模型路径或内部日志。

安装和可移植性细节见 [references/runtime.md](references/runtime.md)。
