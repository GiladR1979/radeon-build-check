---
name: radeon-build-check
description: Compare two Windows Vulkan llama.cpp builds on the same Radeon and GGUF, record raw token rates, and turn measured results into a reproducible hardware note.
---

# Compare Radeon inference builds

Use two extracted Windows x64 Vulkan releases and one GGUF the operator can already run. Confirm which adapter to use with the release's llama-bench.exe --list-devices. Close other GPU workloads for the comparison.

Run scripts/compare_builds.py with Python 3.10+ and the arguments below. Each executable needs its matching DLLs beside it. Keep both installations in separate folders.

~~~powershell
python scripts/compare_builds.py --baseline 'C:\baseline\llama-bench.exe' --candidate 'C:\candidate\llama-bench.exe' --model 'C:\models\model.gguf' --device Vulkan0 --out run.json
~~~

The script runs baseline, candidate, candidate, baseline. Each visit measures a 512-token prompt and 128 output tokens three times. Read the six samples per metric per build in the JSON. If repeats disagree about which build wins, describe the result as inconclusive. Preserve the GGUF hash, GPU, build commits and flags when sharing.

A reader should be able to tell how many output tokens each build generated per second. Report prompt processing separately. A timing benchmark cannot establish answer quality. To check behavior, send the same previously specified task to both versions with matching prompt, settings and output limit. Score against an expected answer, and report the sample size and any failures.

For a short release note, ask the local model to explain the operator's measurements to an owner of that card. Verify every figure against the JSON, scope claims to the tested hardware and workload, and invite independent reproduction. Keep publishing a separate decision for the operator.
