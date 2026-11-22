# AMD Radeon RX 5700 XT on Windows: two llama.cpp builds

Qwen3.5-9B Q4_K_M ran through Vulkan on one AMD Radeon RX 5700 XT. The host CPU was AMD Ryzen 5 3600 6-Core Processor. The same GGUF and test settings were used for both builds.

| Build | Prompt, 512 tokens | Output, 128 tokens | Exact JSON answers |
| --- | ---: | ---: | ---: |
| b11193 (4e7481175) | 139.5 tokens/s | 30.0 tokens/s | 6/6 |
| b12631 (e300919cc) | 467.0 tokens/s | 52.8 tokens/s | 6/6 |

The candidate's median output rate was 1.76 times baseline. The four visits ran in A, B, B, A order, with three samples of each metric per visit. Each median covers six samples. Generated-token speed is measured separately from prompt speed.

### Repeatability

- b11193 output samples: 30.2, 30.1, 30.0 tokens/s
- b12631 output samples: 52.9, 52.9, 52.8 tokens/s
- b12631 output samples: 52.9, 52.4, 52.5 tokens/s
- b11193 output samples: 28.8, 29.9, 30.0 tokens/s

### Answer check

The two servers scored 6/6 and 6/6 on six short synthetic extraction, arithmetic and missing-data questions. The grader compared each parsed JSON object with the expected object. Each server used a 4,096-token context, one slot, temperature zero, seed 73, a 64-token output limit, and disabled thinking. This small check only covers the included questions.

Replay the timing experiment with the included skill. The JSON records individual timing samples, build commits and the model hash. The quality fixture and raw answers are included.

Model SHA-256: 03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8

[Baseline build](https://github.com/ggml-org/llama.cpp/releases/tag/b11193) · [Candidate build](https://github.com/ggml-org/llama.cpp/releases/tag/b12631) · [Pinned GGUF](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/blob/3885219b6810b007914f3a7950a8d1b469d598a5/Qwen3.5-9B-Q4_K_M.gguf)

### Next experiment proposed by local Qwen

Run a new test where you keep the model, hardware, and quantization identical but vary the prompt length from short to very long. Measure how the output tokens per second change as the context window grows to see if performance degrades with longer inputs.

I tested the newer build at three starting depths. Each row is the median of three 128-token generation runs. The context was filled with benchmark tokens. This measures speed after prefill and does not test retrieval from long documents.

| Tokens already in context | Median output tokens/s |
| ---: | ---: |
| 0 | 52.4 |
| 512 | 51.7 |
| 3072 | 50.8 |
