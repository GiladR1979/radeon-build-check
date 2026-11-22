# Radeon build check

How much difference can the llama.cpp build make on the same graphics card? On my Windows RX 5700 XT (8 GB), Qwen3.5-9B went from **30.0 to 52.8 output tokens/s** when I switched from b11193 to b12631. I kept the model file and settings the same. Each number is the median of six runs. Both builds got the same six short answer checks right.

I repeated the whole comparison and got **29.6 and 52.6 output tokens/s**. Both sets of raw samples are here. [First run](sample/timings.json) · [Second run](sample/repeat-timings.json)

The [field note](sample/field-note.md) includes the exact builds, the model download, and a follow-up with more tokens in context.

## Run it on your card

You'll need Windows, a Vulkan-capable Radeon, Python 3.10 or later, and a local GGUF that fits your machine. Download the Windows x64 Vulkan archives for [b11193](https://github.com/ggml-org/llama.cpp/releases/tag/b11193) and [b12631](https://github.com/ggml-org/llama.cpp/releases/tag/b12631). Extract each into its own folder so each executable uses its own DLLs.

From the root of this repository, run the following in PowerShell. Replace the three input paths with yours. Pick an unused output filename.

```powershell
py -3 .\radeon-build-check\scripts\compare_builds.py `
  --baseline 'C:\baseline\llama-bench.exe' `
  --candidate 'C:\candidate\llama-bench.exe' `
  --model 'C:\models\model.gguf' `
  --device Vulkan0 --out .\my-run.json
```

Use `llama-bench.exe --list-devices` to check which Vulkan device to select. The script runs the older build, the newer build twice, then the older build again. Each visit measures a 512-token prompt and 128 tokens of output separately. You can use the [skill instructions](radeon-build-check/SKILL.md) with an agent or run the Python script directly.

If you try this on another Radeon, share your card, driver, model, build numbers and the two output speeds in a GitHub issue. A slower result is worth sharing too.
