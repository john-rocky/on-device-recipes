# Can LiteRT-LM run models other than Gemma?

**Last verified: 2026-09-05** — LiteRT-LM 0.16.1 (`litertlm-android`) on a Pixel 8a (Android 16) for Recipe 2, with a re-gate row on 0.17.0; the bundle list below carries the date it was read from the Hugging Face API.

## Direct answer

Yes. LiteRT-LM runs any `.litertlm` bundle, and the litert-community organization on Hugging Face publishes ungated bundles for families other than Gemma: Qwen 2, 2.5, 3 and 3.5, SmolLM, OLMo, Phi, Ministral, LFM, Falcon-H1, granite, Nemotron and more, plus vision-language, speech-recognition and translation models. The list below is generated from the Hugging Face API and says for each one the base model, the license and the files. [litert-community/Qwen2.5-1.5B-Instruct](https://huggingface.co/litert-community/Qwen2.5-1.5B-Instruct) (Apache-2.0, converted from Qwen/Qwen2.5-1.5B-Instruct) is the one Recipe 2 uses to add an offline chat to an existing Android app, verified on a Pixel 8a. A fine-tune that is not on the list converts with [hf-to-litertlm](https://github.com/john-rocky/hf-to-litertlm) (that route, on iPhone, is [the next page](fine-tuned-hf-model-on-iphone.md)).

Before choosing this route, check three things: the bundle is ungated or you have accepted its license, the device has the memory for the file you pick (Recipe 2's 1.6 GB q8 bundle held 1,975,121 kB of process memory on the Pixel 8a while loaded), and the app can ship or download a file of that size.

## Ungated LiteRT-LM bundles other than Gemma

<!-- gen:ungated-litertlm-list:start -->
Read from the Hugging Face API on 2026-09-05: 93 repositories under [litert-community](https://huggingface.co/litert-community) carry a `.litertlm` file, and 79 of them are neither gated nor a Gemma model. They are listed below by the task on their card, with the base model and the license exactly as the card metadata gives them. The size column is the figure written in the repository name, not a count of the weights; repositories whose name carries none are left blank. Not listed: 7 ungated Gemma repositories and 7 gated ones ([functiongemma-270m-ft-mobile-actions](https://huggingface.co/litert-community/functiongemma-270m-ft-mobile-actions), [functiongemma-270m-ft-tiny-garden](https://huggingface.co/litert-community/functiongemma-270m-ft-tiny-garden), [gemma-3-270m-it](https://huggingface.co/litert-community/gemma-3-270m-it), [Gemma3-1B-IT](https://huggingface.co/litert-community/Gemma3-1B-IT), [Llama-3.2-1B](https://huggingface.co/litert-community/Llama-3.2-1B), [Llama-3.2-3B](https://huggingface.co/litert-community/Llama-3.2-3B), [MedGemma-1.5-4B-IT](https://huggingface.co/litert-community/MedGemma-1.5-4B-IT)).

**Text generation (chat and instruct models)** (57)

| repository | base model | license | size in name | `.litertlm` files | last updated |
|---|---|---|---|---|---|
| [OLMo-2-1B-Instruct](https://huggingface.co/litert-community/OLMo-2-1B-Instruct) | [allenai/OLMo-2-0425-1B-Instruct](https://huggingface.co/allenai/OLMo-2-0425-1B-Instruct) | apache-2.0 | 1B | `OLMo-2-1B-Instruct_q4_block32_ekv4096.litertlm` | 2026-09-05 |
| [FastVLM-0.5B](https://huggingface.co/litert-community/FastVLM-0.5B) | [apple/FastVLM-0.5B](https://huggingface.co/apple/FastVLM-0.5B) | apple-amlr | 0.5B | `FastVLM-0.5B.litertlm`<br>`FastVLM-0.5B.qualcomm.sm8750.litertlm`<br>`FastVLM-0.5B.qualcomm.sm8850.litertlm` | 2026-06-24 |
| [DeepSeek-R1-Distill-Qwen-1.5B](https://huggingface.co/litert-community/DeepSeek-R1-Distill-Qwen-1.5B) | [deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B) | mit | 1.5B | `DeepSeek-R1-Distill-Qwen-1.5B_multi-prefill-seq_q8_ekv4096.litertlm` | 2025-09-22 |
| [DeepSeek-R1-Distill-Qwen-7B](https://huggingface.co/litert-community/DeepSeek-R1-Distill-Qwen-7B) | [deepseek-ai/DeepSeek-R1-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B) | mit | 7B | `DeepSeek-R1-Distill-Qwen-7B_q4_block32_ekv4096.litertlm` | 2026-09-04 |
| [SmolLM2-135M-Instruct](https://huggingface.co/litert-community/SmolLM2-135M-Instruct) | [HuggingFaceTB/SmolLM2-135M-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-135M-Instruct) | apache-2.0 | 135M | `SmolLM2_135M_Instruct.litertlm` | 2026-06-01 |
| [SmolLM2-360M-Instruct](https://huggingface.co/litert-community/SmolLM2-360M-Instruct) | [HuggingFaceTB/SmolLM2-360M-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct) | apache-2.0 | 360M | `SmolLM2_360M_instruct.litertlm` | 2026-05-07 |
| [SmolLM3-3B](https://huggingface.co/litert-community/SmolLM3-3B) | [HuggingFaceTB/SmolLM3-3B](https://huggingface.co/HuggingFaceTB/SmolLM3-3B) | apache-2.0 | 3B | `SmolLM3-3B.litertlm`<br>`SmolLM3-3B_q4_block32_ekv4096.litertlm` | 2026-09-05 |
| [granite-4.0-350m-litert-lm](https://huggingface.co/litert-community/granite-4.0-350m-litert-lm) | [ibm-granite/granite-4.0-350m](https://huggingface.co/ibm-granite/granite-4.0-350m) | apache-2.0 | 350m | `granite-4.0-350m_q8_ekv1280.litertlm` | 2026-07-15 |
| [granite-4.0-h-1b](https://huggingface.co/litert-community/granite-4.0-h-1b) | [ibm-granite/granite-4.0-h-1b](https://huggingface.co/ibm-granite/granite-4.0-h-1b) | apache-2.0 | 1b | `granite-4.0-h-1b_int8.litertlm` | 2026-09-05 |
| [granite-4.0-h-350m](https://huggingface.co/litert-community/granite-4.0-h-350m) | [ibm-granite/granite-4.0-h-350m](https://huggingface.co/ibm-granite/granite-4.0-h-350m) | apache-2.0 | 350m | `granite-4.0-h-350m_fp16.litertlm`<br>`granite-4.0-h-350m_int8.litertlm`<br>`granite-4.0-h-350m_int8_gpu.litertlm` | 2026-09-05 |
| [granite-4.1-3b](https://huggingface.co/litert-community/granite-4.1-3b) | [ibm-granite/granite-4.1-3b](https://huggingface.co/ibm-granite/granite-4.1-3b) | apache-2.0 | 3b | `granite-4.1-3b_int4.litertlm`<br>`granite-4.1-3b_int8.litertlm` | 2026-09-04 |
| [granite-4.2-3b](https://huggingface.co/litert-community/granite-4.2-3b) | [ibm-granite/granite-4.2-3b](https://huggingface.co/ibm-granite/granite-4.2-3b) | apache-2.0 | 3b | `granite-4.2-3b_int4.litertlm`<br>`granite-4.2-3b_int8.litertlm` | 2026-09-04 |
| [LFM2.5-1.2B-Instruct](https://huggingface.co/litert-community/LFM2.5-1.2B-Instruct) | [LiquidAI/LFM2.5-1.2B-Instruct](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct) | other (lfm-open-license-v1.0) | 1.2B | `LFM2.5-1.2B-Instruct_int4.litertlm`<br>`LFM2.5-1.2B-Instruct_int4_gpu.litertlm`<br>`LFM2.5-1.2B-Instruct_int8.litertlm` | 2026-09-05 |
| [LFM2.5-1.2B-JP](https://huggingface.co/litert-community/LFM2.5-1.2B-JP) | [LiquidAI/LFM2.5-1.2B-JP](https://huggingface.co/LiquidAI/LFM2.5-1.2B-JP) | other (lfm-open-license-v1.0) | 1.2B | `LFM2.5-1.2B-JP_int4.litertlm`<br>`LFM2.5-1.2B-JP_int4_gpu.litertlm`<br>`LFM2.5-1.2B-JP_int8.litertlm`<br>`LFM2.5-1.2B-JP_int8_gpu.litertlm` | 2026-09-05 |
| [LFM2.5-1.2B-Thinking](https://huggingface.co/litert-community/LFM2.5-1.2B-Thinking) | [LiquidAI/LFM2.5-1.2B-Thinking](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Thinking) | other (lfm-open-license-v1.0) | 1.2B | `LFM2.5-1.2B-Thinking_int4.litertlm`<br>`LFM2.5-1.2B-Thinking_int4_gpu.litertlm`<br>`LFM2.5-1.2B-Thinking_int8.litertlm`<br>`LFM2.5-1.2B-Thinking_int8_gpu.litertlm` | 2026-09-05 |
| [LFM2.5-2.6B](https://huggingface.co/litert-community/LFM2.5-2.6B) | [LiquidAI/LFM2.5-2.6B](https://huggingface.co/LiquidAI/LFM2.5-2.6B) | other (lfm-open-license-v1.0) | 2.6B | `LFM2.5-2.6B_int4.litertlm`<br>`LFM2.5-2.6B_int8.litertlm` | 2026-09-04 |
| [LFM2.5-230M](https://huggingface.co/litert-community/LFM2.5-230M) | [LiquidAI/LFM2.5-230M](https://huggingface.co/LiquidAI/LFM2.5-230M) | other (lfm1.0) | 230M | `LFM2.5-230M_int4.litertlm`<br>`LFM2.5-230M_int8.litertlm` | 2026-09-05 |
| [Jan-nano](https://huggingface.co/litert-community/Jan-nano) | [Menlo/Jan-nano](https://huggingface.co/Menlo/Jan-nano) | apache-2.0 |  | `model.litertlm`<br>`model_block32.litertlm` | 2026-09-04 |
| [FastContext-1.0-4B-SFT](https://huggingface.co/litert-community/FastContext-1.0-4B-SFT) | [microsoft/FastContext-1.0-4B-SFT](https://huggingface.co/microsoft/FastContext-1.0-4B-SFT) | mit | 4B | `model.litertlm`<br>`model_block128.litertlm` | 2026-09-04 |
| [Phi-4-mini-instruct](https://huggingface.co/litert-community/Phi-4-mini-instruct) | [microsoft/Phi-4-mini-instruct](https://huggingface.co/microsoft/Phi-4-mini-instruct) | mit |  | `Phi-4-mini-instruct_multi-prefill-seq_q8_ekv4096.litertlm` | 2025-09-22 |
| [Phi-4-mini-reasoning](https://huggingface.co/litert-community/Phi-4-mini-reasoning) | [microsoft/Phi-4-mini-reasoning](https://huggingface.co/microsoft/Phi-4-mini-reasoning) | mit |  | `model.litertlm` | 2026-09-05 |
| [Ministral-3-3B-Instruct-2512](https://huggingface.co/litert-community/Ministral-3-3B-Instruct-2512) | [mistralai/Ministral-3-3B-Instruct-2512](https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512) | apache-2.0 | 3B | `Ministral-3-3B-Instruct-2512_q4_block32_ekv4096.litertlm` | 2026-09-04 |
| [Ministral-3-3B-Reasoning-2512](https://huggingface.co/litert-community/Ministral-3-3B-Reasoning-2512) | [mistralai/Ministral-3-3B-Reasoning-2512](https://huggingface.co/mistralai/Ministral-3-3B-Reasoning-2512) | apache-2.0 | 3B | `model.litertlm` | 2026-09-04 |
| [Nanbeige4.1-3B](https://huggingface.co/litert-community/Nanbeige4.1-3B) | [Nanbeige/Nanbeige4.1-3B](https://huggingface.co/Nanbeige/Nanbeige4.1-3B) | apache-2.0 | 3B | `model.litertlm` | 2026-09-05 |
| [Nanbeige4.2-3B](https://huggingface.co/litert-community/Nanbeige4.2-3B) | [Nanbeige/Nanbeige4.2-3B](https://huggingface.co/Nanbeige/Nanbeige4.2-3B) | apache-2.0 | 3B | `model.litertlm`<br>`model_fp32act.litertlm` | 2026-09-04 |
| [Nemotron-H-4B-Instruct-128K](https://huggingface.co/litert-community/Nemotron-H-4B-Instruct-128K) | [nvidia/Nemotron-H-4B-Instruct-128K](https://huggingface.co/nvidia/Nemotron-H-4B-Instruct-128K) | other (nvidia-open-model-license) | 4B | `Nemotron-H-4B-Instruct-128K_int8.litertlm` | 2026-09-04 |
| [Nemotron-3-Nano-4B](https://huggingface.co/litert-community/Nemotron-3-Nano-4B) | [nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16) | other (nvidia-nemotron-open-model-license) | 4B | `Nemotron-3-Nano-4B_int8.litertlm` | 2026-09-04 |
| [MiniCPM5-1B](https://huggingface.co/litert-community/MiniCPM5-1B) | [openbmb/MiniCPM5-1B](https://huggingface.co/openbmb/MiniCPM5-1B) | apache-2.0 | 1B | `MiniCPM5-1B_dynamic_wi8_afp32.litertlm`<br>`minicpm_wi4b32_wi8_afp32.litertlm`<br>`minicpm_wi4b32_wi8_afp32_gpu_opt.litertlm` | 2026-08-14 |
| [Polaris-4B-Preview](https://huggingface.co/litert-community/Polaris-4B-Preview) | [POLARIS-Project/Polaris-4B-Preview](https://huggingface.co/POLARIS-Project/Polaris-4B-Preview) | apache-2.0 | 4B | `model.litertlm` | 2026-09-04 |
| [Qwen2-0.5B-Instruct](https://huggingface.co/litert-community/Qwen2-0.5B-Instruct) | [Qwen/Qwen2-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2-0.5B-Instruct) | apache-2.0 | 0.5B | `Qwen2_0.5B_Instruct.litertlm` | 2026-09-01 |
| [Qwen2-1.5B-Instruct](https://huggingface.co/litert-community/Qwen2-1.5B-Instruct) | [Qwen/Qwen2-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2-1.5B-Instruct) | apache-2.0 | 1.5B | `Qwen2_1.5B_Instruct.litertlm` | 2026-06-26 |
| [Qwen2.5-1.5B-Instruct](https://huggingface.co/litert-community/Qwen2.5-1.5B-Instruct) | [Qwen/Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) | apache-2.0 | 1.5B | `Qwen2.5-1.5B-Instruct_multi-prefill-seq_f32_ekv4096.litertlm`<br>`Qwen2.5-1.5B-Instruct_multi-prefill-seq_q8_ekv4096.litertlm` | 2025-11-25 |
| [Qwen2.5-Coder-1.5B-Instruct](https://huggingface.co/litert-community/Qwen2.5-Coder-1.5B-Instruct) | [Qwen/Qwen2.5-Coder-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct) | apache-2.0 | 1.5B | `Qwen2.5-Coder-1.5B-Instruct_int4.litertlm` | 2026-09-05 |
| [Qwen3-0.6B](https://huggingface.co/litert-community/Qwen3-0.6B) | [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B) | apache-2.0 | 0.6B | `Qwen3-0.6B.litertlm`<br>`Qwen3-0.6B.mediatek.mt6993.litertlm`<br>`Qwen3-0.6B_dynamic_wi4b32_afp32.litertlm`<br>`qwen3_0_6b_mixed_int4.litertlm` | 2026-08-05 |
| [Qwen3-0.6B-int4](https://huggingface.co/litert-community/Qwen3-0.6B-int4) | [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B) | apache-2.0 | 0.6B | `qwen3_0.6b_nothink_q4_block32_ekv1280.litertlm`<br>`qwen3_0.6b_q4_block32_ekv1280.litertlm` | 2026-06-30 |
| [Qwen3-1.7B](https://huggingface.co/litert-community/Qwen3-1.7B) | [Qwen/Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B) | apache-2.0 | 1.7B | `Qwen3-1.7B_dynamic_wi4b32_afp32.litertlm`<br>`Qwen3_1.7B.litertlm` | 2026-08-31 |
| [Qwen3-14B](https://huggingface.co/litert-community/Qwen3-14B) | [Qwen/Qwen3-14B](https://huggingface.co/Qwen/Qwen3-14B) | apache-2.0 | 14B | `qwen3_14b_channelwise_int8_float32kv.litertlm`<br>`qwen3_14b_mixed_int4.litertlm` | 2026-06-05 |
| [Qwen3-4B](https://huggingface.co/litert-community/Qwen3-4B) | [Qwen/Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) | apache-2.0 | 4B | `qwen3_4b_channelwise_int8_float32kv.litertlm`<br>`qwen3_4b_mixed_int4.litertlm` | 2026-06-05 |
| [Qwen3-4B-Instruct-2507](https://huggingface.co/litert-community/Qwen3-4B-Instruct-2507) | [Qwen/Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) | apache-2.0 | 4B | `qwen3_4b_instruct_2507_mixed_int4.litertlm` | 2026-09-03 |
| [Qwen3-4B-Thinking-2507](https://huggingface.co/litert-community/Qwen3-4B-Thinking-2507) | [Qwen/Qwen3-4B-Thinking-2507](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507) | apache-2.0 | 4B | `Qwen3_4b_thinking_dynamic_wi4b32_afp32.litertlm`<br>`model.litertlm` | 2026-09-04 |
| [Qwen3-8B](https://huggingface.co/litert-community/Qwen3-8B) | [Qwen/Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B) | apache-2.0 | 8B | `qwen3_8b_channelwise_int8_float32kv.litertlm`<br>`qwen3_8b_mixed_int4.litertlm` | 2026-06-05 |
| [Qwen3.5-0.8B](https://huggingface.co/litert-community/Qwen3.5-0.8B) | [Qwen/Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B) | apache-2.0 | 0.8B | `Qwen3.5-0.8B-VL_int8.litertlm`<br>`Qwen3.5-0.8B_int8.litertlm` | 2026-09-05 |
| [Qwen3.5-2B](https://huggingface.co/litert-community/Qwen3.5-2B) | [Qwen/Qwen3.5-2B](https://huggingface.co/Qwen/Qwen3.5-2B) | apache-2.0 | 2B | `Qwen3.5-2B-VL_int8.litertlm`<br>`Qwen3.5-2B_int8.litertlm` | 2026-09-05 |
| [Qwen3.5-4B](https://huggingface.co/litert-community/Qwen3.5-4B) | [Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) | apache-2.0 | 4B | `Qwen3.5-4B_int8.litertlm`<br>`Qwen3.5-4B_mixed_int4.litertlm` | 2026-09-05 |
| [Qwen2.5-Coder-3B-Instruct](https://huggingface.co/litert-community/Qwen2.5-Coder-3B-Instruct) | Qwen2.5-Coder-3B-Instruct | apache-2.0 | 3B | `Qwen2.5_Coder_3B_It.litertlm` | 2026-09-01 |
| [TinySwallow-1.5B-Instruct](https://huggingface.co/litert-community/TinySwallow-1.5B-Instruct) | [SakanaAI/TinySwallow-1.5B-Instruct](https://huggingface.co/SakanaAI/TinySwallow-1.5B-Instruct) | apache-2.0 | 1.5B | `TinySwallow-1.5B-Instruct.litertlm` | 2026-06-01 |
| [sarashina2.2-0.5b-instruct-v0.1](https://huggingface.co/litert-community/sarashina2.2-0.5b-instruct-v0.1) | [sbintuitions/sarashina2.2-0.5b-instruct-v0.1](https://huggingface.co/sbintuitions/sarashina2.2-0.5b-instruct-v0.1) | mit | 0.5b | `sarashina2.2-0.5b-instruct-v0.1_int4.litertlm`<br>`sarashina2.2-0.5b-instruct-v0.1_int8.litertlm` | 2026-09-05 |
| [sarashina2.2-1b-instruct-v0.1](https://huggingface.co/litert-community/sarashina2.2-1b-instruct-v0.1) | [sbintuitions/sarashina2.2-1b-instruct-v0.1](https://huggingface.co/sbintuitions/sarashina2.2-1b-instruct-v0.1) | mit | 1b | `sarashina2.2-1b-instruct-v0.1_int4.litertlm`<br>`sarashina2.2-1b-instruct-v0.1_int8.litertlm` | 2026-09-05 |
| [Falcon-H1-0.5B-Instruct](https://huggingface.co/litert-community/Falcon-H1-0.5B-Instruct) | [tiiuae/Falcon-H1-0.5B-Instruct](https://huggingface.co/tiiuae/Falcon-H1-0.5B-Instruct) | other (falcon-llm-license) | 0.5B | `Falcon-H1-0.5B-Instruct_int8.litertlm` | 2026-09-05 |
| [Falcon-H1-1.5B-Deep-Instruct](https://huggingface.co/litert-community/Falcon-H1-1.5B-Deep-Instruct) | [tiiuae/Falcon-H1-1.5B-Deep-Instruct](https://huggingface.co/tiiuae/Falcon-H1-1.5B-Deep-Instruct) | other (falcon-llm-license) | 1.5B | `Falcon-H1-1.5B-Deep-Instruct_int8.litertlm` | 2026-09-05 |
| [Falcon-H1-1.5B-Instruct](https://huggingface.co/litert-community/Falcon-H1-1.5B-Instruct) | [tiiuae/Falcon-H1-1.5B-Instruct](https://huggingface.co/tiiuae/Falcon-H1-1.5B-Instruct) | other (falcon-llm-license) | 1.5B | `Falcon-H1-1.5B-Instruct_int8.litertlm` | 2026-09-05 |
| [Falcon-H1-3B-Instruct](https://huggingface.co/litert-community/Falcon-H1-3B-Instruct) | [tiiuae/Falcon-H1-3B-Instruct](https://huggingface.co/tiiuae/Falcon-H1-3B-Instruct) | other (falcon-llm-license) | 3B | `Falcon-H1-3B-Instruct_int8.litertlm` | 2026-09-04 |
| [Falcon-H1-Tiny-R-0.6B](https://huggingface.co/litert-community/Falcon-H1-Tiny-R-0.6B) | [tiiuae/Falcon-H1-Tiny-R-0.6B](https://huggingface.co/tiiuae/Falcon-H1-Tiny-R-0.6B) | other (falcon-llm-license) | 0.6B | `Falcon-H1-Tiny-R-0.6B_int8.litertlm` | 2026-09-05 |
| [VibeThinker-1.5B](https://huggingface.co/litert-community/VibeThinker-1.5B) | [WeiboAI/VibeThinker-1.5B](https://huggingface.co/WeiboAI/VibeThinker-1.5B) | mit | 1.5B | `VibeThinker-1.5B.litertlm` | 2026-05-27 |
| [VibeThinker-3B](https://huggingface.co/litert-community/VibeThinker-3B) | [WeiboAI/VibeThinker-3B](https://huggingface.co/WeiboAI/VibeThinker-3B) | mit | 3B | `model.litertlm` | 2026-09-04 |
| [Zamba2-1.2B-instruct](https://huggingface.co/litert-community/Zamba2-1.2B-instruct) | [Zyphra/Zamba2-1.2B-instruct](https://huggingface.co/Zyphra/Zamba2-1.2B-instruct) | apache-2.0 | 1.2B | `Zamba2-1.2B-instruct_int8.litertlm` | 2026-09-05 |
| [Zamba2-2.7B-instruct](https://huggingface.co/litert-community/Zamba2-2.7B-instruct) | [Zyphra/Zamba2-2.7B-instruct](https://huggingface.co/Zyphra/Zamba2-2.7B-instruct) | apache-2.0 | 2.7B | `Zamba2-2.7B-instruct_int8.litertlm` | 2026-09-04 |

**Image and text to text (vision-language models)** (18)

| repository | base model | license | size in name | `.litertlm` files | last updated |
|---|---|---|---|---|---|
| [Ovis2.5-2B](https://huggingface.co/litert-community/Ovis2.5-2B) | [AIDC-AI/Ovis2.5-2B](https://huggingface.co/AIDC-AI/Ovis2.5-2B) | apache-2.0 | 2B | `Ovis2.5-2B.litertlm` | 2026-09-04 |
| [North-Micro-Vision-Instruct](https://huggingface.co/litert-community/North-Micro-Vision-Instruct) | [CohereLabs/North-Micro-Vision-Instruct](https://huggingface.co/CohereLabs/North-Micro-Vision-Instruct) | apache-2.0 |  | `North-Micro-Vision-Instruct_int4.litertlm`<br>`North-Micro-Vision-Instruct_wi8.litertlm` | 2026-09-04 |
| [SmolVLM2-2.2B](https://huggingface.co/litert-community/SmolVLM2-2.2B) | [HuggingFaceTB/SmolVLM2-2.2B-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM2-2.2B-Instruct) | apache-2.0 | 2.2B | `SmolVLM2-2.2B.litertlm` | 2026-09-04 |
| [SmolVLM2-500M](https://huggingface.co/litert-community/SmolVLM2-500M) | [HuggingFaceTB/SmolVLM2-500M-Video-Instruct](https://huggingface.co/HuggingFaceTB/SmolVLM2-500M-Video-Instruct) | apache-2.0 | 500M | `SmolVLM2-500M.litertlm` | 2026-09-05 |
| [granite-docling-258M](https://huggingface.co/litert-community/granite-docling-258M) | [ibm-granite/granite-docling-258M](https://huggingface.co/ibm-granite/granite-docling-258M) | apache-2.0 | 258M | `granite-docling-258M.litertlm` | 2026-09-05 |
| [LFM2.5-VL-1.6B](https://huggingface.co/litert-community/LFM2.5-VL-1.6B) | [LiquidAI/LFM2.5-VL-1.6B](https://huggingface.co/LiquidAI/LFM2.5-VL-1.6B) | other (lfm-open-license-v1.0) | 1.6B | `LFM2.5-VL-1.6B_int4.litertlm`<br>`LFM2.5-VL-1.6B_int8.litertlm` | 2026-09-05 |
| [LFM2.5-VL-3B](https://huggingface.co/litert-community/LFM2.5-VL-3B) | [LiquidAI/LFM2.5-VL-3B](https://huggingface.co/LiquidAI/LFM2.5-VL-3B) | other (lfm-open-license-v1.0) | 3B | `LFM2.5-VL-3B_int4.litertlm`<br>`LFM2.5-VL-3B_int8.litertlm` | 2026-09-04 |
| [LFM2.5-VL-450M](https://huggingface.co/litert-community/LFM2.5-VL-450M) | [LiquidAI/LFM2.5-VL-450M](https://huggingface.co/LiquidAI/LFM2.5-VL-450M) | other (lfm-open-license-v1.0) | 450M | `LFM2.5-VL-450M_int4.litertlm`<br>`LFM2.5-VL-450M_int8.litertlm` | 2026-09-05 |
| [LLaVA-OneVision-0.5B](https://huggingface.co/litert-community/LLaVA-OneVision-0.5B) | [llava-hf/llava-onevision-qwen2-0.5b-ov-hf](https://huggingface.co/llava-hf/llava-onevision-qwen2-0.5b-ov-hf) | apache-2.0 | 0.5B | `LLaVA-OneVision-0.5B.litertlm` | 2026-09-05 |
| [Mage-VL](https://huggingface.co/litert-community/Mage-VL) | [microsoft/Mage-VL](https://huggingface.co/microsoft/Mage-VL) | apache-2.0 |  | `Mage-VL.litertlm` | 2026-09-04 |
| [MiniCPM-V-4](https://huggingface.co/litert-community/MiniCPM-V-4) | [openbmb/MiniCPM-V-4](https://huggingface.co/openbmb/MiniCPM-V-4) | apache-2.0 |  | `MiniCPM-V-4-int8.litertlm` | 2026-08-01 |
| [InternVL3-1B](https://huggingface.co/litert-community/InternVL3-1B) | [OpenGVLab/InternVL3-1B](https://huggingface.co/OpenGVLab/InternVL3-1B) | apache-2.0 | 1B | `InternVL3-1B.litertlm` | 2026-09-05 |
| [InternVL3-2B](https://huggingface.co/litert-community/InternVL3-2B) | [OpenGVLab/InternVL3-2B](https://huggingface.co/OpenGVLab/InternVL3-2B) | apache-2.0 | 2B | `InternVL3-2B.litertlm` | 2026-09-05 |
| [InternVL3_5-1B](https://huggingface.co/litert-community/InternVL3_5-1B) | [OpenGVLab/InternVL3_5-1B](https://huggingface.co/OpenGVLab/InternVL3_5-1B) | apache-2.0 | 1B | `model.litertlm` | 2026-09-05 |
| [InternVL3_5-2B](https://huggingface.co/litert-community/InternVL3_5-2B) | [OpenGVLab/InternVL3_5-2B](https://huggingface.co/OpenGVLab/InternVL3_5-2B) | apache-2.0 | 2B | `model.litertlm` | 2026-09-04 |
| [InternVL3_5-4B](https://huggingface.co/litert-community/InternVL3_5-4B) | [OpenGVLab/InternVL3_5-4B](https://huggingface.co/OpenGVLab/InternVL3_5-4B) | apache-2.0 | 4B | `model.litertlm` | 2026-09-04 |
| [PaddleOCR-VL-1.6](https://huggingface.co/litert-community/PaddleOCR-VL-1.6) | [PaddlePaddle/PaddleOCR-VL-1.6](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6) | apache-2.0 |  | `PaddleOCR-VL-1.6.litertlm` | 2026-09-05 |
| [Qwen2-VL-2B](https://huggingface.co/litert-community/Qwen2-VL-2B) | [Qwen/Qwen2-VL-2B-Instruct](https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct) | apache-2.0 | 2B | `Qwen2-VL-2B.litertlm` | 2026-09-05 |

**Speech recognition** (2)

| repository | base model | license | size in name | `.litertlm` files | last updated |
|---|---|---|---|---|---|
| [VibeVoice-ASR-BitNet](https://huggingface.co/litert-community/VibeVoice-ASR-BitNet) | [microsoft/VibeVoice-ASR-BitNet](https://huggingface.co/microsoft/VibeVoice-ASR-BitNet) | mit |  | `VibeVoice-ASR-BitNet.litertlm` | 2026-09-04 |
| [Qwen3-ASR-0.6B](https://huggingface.co/litert-community/Qwen3-ASR-0.6B) | [Qwen/Qwen3-ASR-0.6B](https://huggingface.co/Qwen/Qwen3-ASR-0.6B) | apache-2.0 | 0.6B | `qwen3_asr_0.6b_5s_i8.litertlm` | 2026-09-03 |

**Translation** (1)

| repository | base model | license | size in name | `.litertlm` files | last updated |
|---|---|---|---|---|---|
| [Hy-MT2-1.8B](https://huggingface.co/litert-community/Hy-MT2-1.8B) | [tencent/Hy-MT2-1.8B](https://huggingface.co/tencent/Hy-MT2-1.8B) | apache-2.0 | 1.8B | `Hy-MT2-1.8B_int8.litertlm` | 2026-09-05 |

**No pipeline tag on the card** (1)

| repository | base model | license | size in name | `.litertlm` files | last updated |
|---|---|---|---|---|---|
| [Shieldstral-1.0-3B](https://huggingface.co/litert-community/Shieldstral-1.0-3B) | [mistralai/Shieldstral-1.0-3B](https://huggingface.co/mistralai/Shieldstral-1.0-3B) | apache-2.0 | 3B | `Shieldstral-1.0-3B-vision_int4.litertlm`<br>`Shieldstral-1.0-3B-vision_int4_gpu.litertlm`<br>`Shieldstral-1.0-3B_int4.litertlm`<br>`Shieldstral-1.0-3B_int8.litertlm` | 2026-09-04 |
<!-- gen:ungated-litertlm-list:end -->

## Decision table

| you have | route | why |
|---|---|---|
| a model on the list above, an Android app | LiteRT-LM Kotlin API, Recipe 2 below | the bundle carries the tokenizer and the chat template; the recipe adds two Gradle lines, two files, cancel and release |
| a model on the list above, an iOS or macOS app | LiteRT-LM through [swift-litert-lm](https://github.com/john-rocky/swift-litert-lm) | same bundle file; the Swift path is on [the next page](fine-tuned-hf-model-on-iphone.md) |
| your own fine-tune of a listed family | [hf-to-litertlm](https://github.com/john-rocky/hf-to-litertlm), then the recipe for your platform | one command from the Hugging Face repo to a `.litertlm`, with an 8-question gate |
| a gated model (Gemma, Llama 3.2, MedGemma) | LiteRT-LM after accepting the license on Hugging Face | the bundle download then needs a token; Recipe 2's downloader sends none |
| a model the converter refuses (mixture-of-experts, repo-local code, pre-quantized weights) | another runtime, see "When not to use" | LiteRT-LM has no bundle for it and hf-to-litertlm refuses it at the entry gate |

## Quick start

Recipe 2 adds Qwen2.5-1.5B-Instruct as an offline chat to an app that already exists:
[android-llm-chat/INTEGRATION.md](https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/INTEGRATION.md).

<!-- gen:recipe-answer:android-llm-chat:start -->
**Add a chat that needs no network, using Qwen2.5-1.5B-Instruct, to an existing Android app.** Model: [litert-community/Qwen2.5-1.5B-Instruct](https://huggingface.co/litert-community/Qwen2.5-1.5B-Instruct) `Qwen2.5-1.5B-Instruct_multi-prefill-seq_q8_ekv4096.litertlm` (1,597,931,520 bytes, apache-2.0, from [Qwen/Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct)). Runtime: LiteRT-LM 0.16.1 (`com.google.ai.edge.litertlm:litertlm-android`), cpu. Verified: Pixel 8a, Android 16, build CP1A.260505.005 (SDK 36), 2026-09-05: CPU: 10.48 tokens/s decode, 55.4 tokens/s prefill, 0.67 s to the first token; GPU: 13.8 tokens/s decode, 71.5 tokens/s prefill, 0.5 s to the first token. Status: verified. Guide: https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/INTEGRATION.md; machine-readable: https://raw.githubusercontent.com/john-rocky/on-device-recipes/main/android-llm-chat/recipe.json.
<!-- gen:recipe-answer:android-llm-chat:end -->

Add the two dependency lines (generated below, with the pins), copy `ChatEngine.kt` and `ModelProvisioner.kt` from the recipe, then:

```kotlin
val modelFile = ModelProvisioner.provision(context, MODEL_URL, MODEL_SHA256, MODEL_BYTES) { status -> }
val engine = ChatEngine(modelFile.absolutePath, cacheDir = context.cacheDir.path)
engine.initialize()                                           // seconds; Dispatchers.IO inside
engine.send("Hello").collect { chunk -> transcript.append(chunk) }
engine.cancel()   // Stop: ends the reply being generated; the next send() continues the chat
engine.close()    // Release: frees the model; initialize() loads it again with the chat kept
```

The model file, the dependency pins, the manifest lines and the verify command, from `recipe.json`:

<!-- gen:recipe-conditions:android-llm-chat:start -->
| | |
|---|---|
| model repository | [litert-community/Qwen2.5-1.5B-Instruct](https://huggingface.co/litert-community/Qwen2.5-1.5B-Instruct) |
| model file | `Qwen2.5-1.5B-Instruct_multi-prefill-seq_q8_ekv4096.litertlm` |
| download URL | <https://huggingface.co/litert-community/Qwen2.5-1.5B-Instruct/resolve/main/Qwen2.5-1.5B-Instruct_multi-prefill-seq_q8_ekv4096.litertlm> |
| sha256 | `faa60663b333290c1496c499828b21d3e3254a788cacd8cce917ce0f761a2dc9` |
| size, bytes | 1,597,931,520 |
| license | apache-2.0 |
| base model | [Qwen/Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) |
| variant | q8 weights, KV cache 4096 tokens (the f32 file in the same repo is 6.2 GB) |
| published by | litert-community (Google AI Edge); not gated |
| runtime | LiteRT-LM |
| runtime version | 0.16.1 |
| Maven artifact | `com.google.ai.edge.litertlm:litertlm-android` |
| accelerator | cpu |
| converter | none |
| conversion note | The bundle is published as-is by litert-community; this recipe converts nothing. A fine-tune of the same base converts with https://github.com/john-rocky/hf-to-litertlm. |
| minimum Android SDK | 24 |
| ABI | arm64-v8a |
| toolchain | AGP 9.3.1, Gradle 9.7.0, compileSdk 36, JDK 17 |
<!-- gen:recipe-conditions:android-llm-chat:end -->

<!-- gen:recipe-steps:android-llm-chat:start -->
1. Dependency lines, exactly as they go into the build file:

   ```
   implementation("com.google.ai.edge.litertlm:litertlm-android:0.16.1")
   implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.11.0")
   ```

   minSdk 24. pins `org.jetbrains.kotlinx:kotlinx-coroutines-android` 1.11.0, `androidx.test:runner` 1.7.0, `androidx.test.ext:junit` 1.3.0, `junit:junit` 4.13.2. Gradle: No org.jetbrains.kotlin.android plugin: AGP 9 has Kotlin built in and rejects the standalone plugin; testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner". manifest: <uses-permission android:name="android.permission.INTERNET" /> (download on first launch only; inference is offline); <uses-native-library android:name="libvndksupport.so" android:required="false" /> and <uses-native-library android:name="libOpenCL.so" android:required="false" /> inside <application> (GPU backend; harmless on CPU).

2. Files to copy into the app:
   - [`ChatEngine.kt`](https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/app/src/main/kotlin/io/github/johnrocky/llmchat/ChatEngine.kt)
   - [`ModelProvisioner.kt`](https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/app/src/main/kotlin/io/github/johnrocky/llmchat/ModelProvisioner.kt)

3. Model delivery: downloaded at first launch into filesDir/models/<file>, sha256 verified while streaming into a .part file (ModelProvisioner). Developer shortcut: after the app is installed, adb push the file directly into /sdcard/Android/data/<applicationId>/files/ (no subdirectory: a shell-made subdirectory is not readable by the app) and the provisioner uses it in place after a size check.

4. Verify:

   ```sh
   ./gradlew :app:connectedDebugAndroidTest -Pandroid.injected.androidTest.leaveApksInstalledAfterRun=true   # first run downloads the 1.6 GB model on the device (about 3 min on Wi-Fi); or, after one install, adb push <file> /sdcard/Android/data/io.github.johnrocky.llmchat/files/ first
   ```

   Expected, from the run recorded in recipe.json: BUILD SUCCESSFUL; run finished: 5 tests, 0 failed. logcat (tag recipe), Pixel 8a, CPU backend, LiteRT-LM 0.16.1, 2026-09-05: PROVISION via=pushed ms=9 bytes=1597931520 | RESULT check=turn load_ms=8794 chunks=7 chars=31 first_chunk_ms=909 prefill_tok_s=55.45 decode_tok_s=8.90 ttft_s=0.67 reply="The capital of France is Paris." second_turn_chars=31 | RESULT check=throughput prompt="Explain in five sentences why the sky is blue." runs=3 decode_tokens=113/113/122 decode_tok_s=10.48/10.54/10.26 decode_tok_s_median=10.48 prefill_tok_s=60.29/55.28/50.75 thermal_status=1->1 | RESULT check=cancel_collector chunks_before_cancel=10 cpu_ms_generating=2020/502ms cpu_ms_after_cancel=80/1507ms next_turn_first_chunk_ms=1578 turns=4 intro_reply="Hello Alice! How can I help you today?" next_turn_reply=Alice | RESULT check=cancel_explicit chunks=6 flow_completed_ms=2219 cpu_ms_after_cancel=10/1506ms next_turn_first_chunk_ms=1099 turns=2 partial="1, 2, " next_turn_head=OK. | RESULT check=release load1_ms=1381 pss_loaded_kb=1975121 pss_released_kb=91633 load2_ms=1442 reply_chars_after_reload=31 turns_after_reload=4 | RESULT check=close_during_generation chunks_at_close=6 close_ms=535 cpu_ms_after_close=30/1509ms reload_ms=1154 next_turn_head=OK. Asserted: non-blank streamed replies; no chunk after the cancel and process CPU time under 400 ms over the next 1.5 s; the turn before the cancel is still known ('Alice'); an explicit cancel() ends the flow at chunk 5-8 and the next prompt gets a fresh short answer; close() then initialize() answers again with the history kept; close() during a reply returns in under 10 s and the process is idle afterwards. Latency, tokens/s, memory and load times are logged conditions, not assertions.

   Test files: [`ChatIntegrationTest.kt`](https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/app/src/androidTest/kotlin/io/github/johnrocky/llmchat/ChatIntegrationTest.kt)
<!-- gen:recipe-steps:android-llm-chat:end -->

To try a bundle on a Mac or Linux box before touching the app: `pip install litert-lm`, then
`litert-lm run --from-huggingface-repo litert-community/Qwen2.5-1.5B-Instruct Qwen2.5-1.5B-Instruct_multi-prefill-seq_q8_ekv4096.litertlm --prompt "In one sentence, what is the capital of France?"`.

## Real-device measurements

Recipe 2's instrumented test on a Pixel 8a (Tensor G3, Android 16), phone idle, 2026-09-05. Tokens/s are the runtime's own numbers, median of three turns of the same prompt. The third row is a re-gate run on litertlm-android 0.17.0, which the recipe does not pin yet (its Kotlin 2.4 metadata is refused by the Kotlin built into AGP 9.3.1; the row was taken with the metadata check skipped).

<!-- gen:recipe-measurements:android-llm-chat:start -->
| device | OS | backend | runtime | load ms | reload ms | decode tokens/s | decode tokens/s per run | decode tokens per run | prefill tokens/s | first token s | PSS loaded kB | PSS after release kB | CPU ms in the 1.5 s after a cancel | close() during a reply ms | thermal status | date |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Pixel 8a | Android 16, build CP1A.260505.005 (SDK 36) | cpu | 0.16.1 | 8,794 | 1,442 | 10.48 | 10.48/10.54/10.26 | 113/113/122 | 55.4 | 0.67 | 1,975,121 | 91,633 | 80 | 535 | 1 -> 1 | 2026-09-05 |
| Pixel 8a | Android 16, build CP1A.260505.005 (SDK 36) | gpu | 0.16.1 | 6,691 | 5,483 | 13.8 | 13.28/13.81/13.80 | 30/37/39 | 71.5 | 0.5 | 2,647,531 | 492,268 | 60 | 696 | 1 -> 1 | 2026-09-05 |
| Pixel 8a | Android 16, build CP1A.260505.005 (SDK 36) | cpu | 0.17.0 (compiled with -Xskip-metadata-version-check, see regate) | 13,272 | 1,614 | 10.2 | 10.20/10.32/10.18 | 92/110/110 | 42.9 | 0.6 | 1,973,407 | 90,063 | 10 | 597 | 1 -> 1 | 2026-09-05 |

Conditions:

- Pixel 8a, cpu, 2026-09-05: SoC Tensor G3. USB power, screen on, nothing else running on the phone (checked with top), thermal status 1 before and after, MemAvailable about 4 GB; tok/s are the runtime's own BenchmarkInfo, median of 3 turns of the same prompt after a warm-up turn; load_ms is the first Engine.initialize() of the run (runtime cache from an earlier run present), load_ms_warm the reload inside the release check. model provisioned via pushed. Source: this recipe's verify command, run on 2026-09-05 (RESULT lines quoted in INTEGRATION.md section 6).
- Pixel 8a, gpu, 2026-09-05: SoC Tensor G3. USB power, screen on, nothing else running on the phone (checked with top), thermal status 1 before and after, MemAvailable about 4 GB; tok/s are the runtime's own BenchmarkInfo, median of 3 turns of the same prompt after a warm-up turn; load_ms is the first Engine.initialize() of the run (runtime cache from an earlier run present), load_ms_warm the reload inside the release check; replies were shorter on the GPU backend for the same prompts (30-39 vs 113-122 decode tokens), not investigated; the first-ever GPU load on this phone (OpenCL kernel build) took 62-67 s in two earlier runs. model provisioned via pushed. Source: this recipe's verify command with -Pandroid.testInstrumentationRunnerArguments.backend=gpu, run on 2026-09-05.
- Pixel 8a, cpu, 2026-09-05: SoC Tensor G3. USB power, screen on, nothing else running on the phone (checked with top), thermal status 1 before and after, MemAvailable about 4 GB; tok/s are the runtime's own BenchmarkInfo, median of 3 turns of the same prompt after a warm-up turn; load_ms is the first Engine.initialize() of the run (runtime cache from an earlier run present), load_ms_warm the reload inside the release check. model provisioned via cached. Source: re-gate run on 2026-09-05 with -PlitertlmVersion=0.17.0 -PskipKotlinMetadataCheck=true; not the pinned configuration.
<!-- gen:recipe-measurements:android-llm-chat:end -->

Full lines and conditions: [INTEGRATION.md section 7](https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/INTEGRATION.md#7-verified--unverified). The same bundle through the litert-lm CLI on a Mac and a Galaxy S26, with a different harness: [litertlm-qwen2.5-1.5b-mac-galaxy-s26.md](https://github.com/john-rocky/apple-silicon-llm-bench/blob/main/results/android/litertlm-qwen2.5-1.5b-mac-galaxy-s26.md).

## When to use, when not to use, alternatives

Use LiteRT-LM when one bundle file has to run on Android and iOS from the same runtime, when you want the tokenizer and the chat template inside the model file, or when the model you need is already on the list above. Recipe 2 is the Android form; the Swift form is on the next page.

Not the better choice when:

- **The model is not on the list and the converter refuses it.** hf-to-litertlm refuses mixture-of-experts models, architectures that live in repository code (`auto_map`), pre-quantized weights (GPTQ, AWQ, bitsandbytes) and gated repositories at its entry gate. For those, llama.cpp (GGUF) has the wider architecture coverage on Android and desktop, and MLX has it on Apple silicon.
- **You need a GGUF or MLX file you already have.** LiteRT-LM reads `.litertlm` only; there is no converter from GGUF or MLX weights, so a model you have only in those formats stays on llama.cpp or MLX.
- **You need Apple's own on-device model, not yours.** On iOS 26 and later, Apple's Foundation Models framework runs the system model with no file to ship; swift-litert-lm carries a Foundation Models-compatible adapter for the case where you need your own weights (not exercised by Recipe 2 or 3).
- **The phone has no room for the file.** Recipe 2's q8 bundle is 1.6 GB on disk and 1,975,121 kB in the process while loaded on the Pixel 8a; a smaller bundle from the list (SmolLM2-135M, LFM2.5-230M, Qwen3-0.6B) is the first thing to try, before another runtime.

Not verified here: any runtime other than LiteRT-LM on the Pixel 8a. This page quotes no speed for llama.cpp, MLX or ExecuTorch, because none was measured with this recipe's harness.

## Limits

<!-- gen:recipe-limits:android-llm-chat:start -->
Not verified as of 2026-09-05:

- Android emulator: not run (CPU backend may work there, GPU will not)
- any device other than the Pixel 8a below (Samsung Galaxy / Adreno, MediaTek, other Pixels)
- Android versions other than 16
- the f32 bundle in the same repo (6.2 GB); only the q8 file was used
- tool calling, images, audio, thinking mode, LoRA: not touched by this recipe
- conversations longer than the 4096-token KV cache of this bundle
- download over a metered or interrupted connection: the sha256 check rejects a truncated file, resuming is not implemented
- Galaxy S26 rows exist for the same bundle through the litert-lm CLI (apple-silicon-llm-bench), taken with a different harness, not with this test

Re-gate notes:

- litertlm_android_0_17_0: On Google Maven since 2026-09-04 (no GitHub release on 2026-09-05). Its Kotlin metadata is 2.4.0; the Kotlin built into AGP 9.3.1 (2.2) refuses it: 'Module was compiled with an incompatible version of Kotlin. The binary version of its metadata is 2.4.0, expected version is 2.2.0'. Compiled with -Xskip-metadata-version-check it passed all five checks on the CPU backend (devices[2]). The recipe stays on 0.16.1 until a toolchain with Kotlin 2.4 support is verified.
- model_delivery: The download path ran in the first run after install (PROVISION via=download, 180871 ms for 1597931520 bytes on Wi-Fi, sha256 verified). The pushed copy is used only when it sits directly in the app's external files dir (PROVISION via=pushed); a copy under a shell-created subdirectory is unreadable to the app and the provisioner downloads instead.
<!-- gen:recipe-limits:android-llm-chat:end -->

## Implementation links

- Recipe 2: [android-llm-chat/INTEGRATION.md](https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/INTEGRATION.md), machine-readable [recipe.json](https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/recipe.json), agent skill [litert-android-llm-chat](https://github.com/john-rocky/on-device-recipes/blob/main/skills/litert-android-llm-chat/SKILL.md).
- LiteRT-LM: https://github.com/google-ai-edge/LiteRT-LM
- hf-to-litertlm (fine-tunes to `.litertlm`): https://github.com/john-rocky/hf-to-litertlm
- swift-litert-lm (the same bundles on iOS and macOS): https://github.com/john-rocky/swift-litert-lm

## Model links

- [litert-community/Qwen2.5-1.5B-Instruct](https://huggingface.co/litert-community/Qwen2.5-1.5B-Instruct): the bundle Recipe 2 uses (q8, 4096-token KV cache, 1,597,931,520 bytes, Apache-2.0).
- [litert-community](https://huggingface.co/litert-community): the organization the list above is read from.

## FAQ

**Does the bundle need a Hugging Face token?** Not for the ungated ones listed above. Recipe 2's downloader sends no token; a gated bundle (Gemma, Llama 3.2, MedGemma) needs the license accepted on Hugging Face and a token in the download.

**Is Gemma faster or better supported than the others?** Not measured here. This page compares nothing across families; every number on it is Qwen2.5-1.5B-Instruct on one Pixel 8a.

**Can I keep the chat after Stop?** Yes. LiteRT-LM 0.16 does not reuse a session after `cancelProcess()`; Recipe 2's `ChatEngine` keeps the history itself and rebuilds the runtime conversation on the next `send()`, at the cost of one prefill of the chat so far (1,578 ms to the first chunk of the next turn on the CPU backend in the recipe's test).

**Which litertlm-android version?** 0.16.1, the version Recipe 2 pins and was verified with. 0.17.0 is on Google Maven since 2026-09-04 but ships Kotlin 2.4 metadata that the Kotlin built into AGP 9.3.1 refuses; the re-gate row above was taken with that check skipped.

**Which files in a repository are for phones?** Names with `q8`, `q4`, `int8` or `int4` are the quantized bundles; `f32`, `fp16` and `fp32act` are the reference-precision ones (6.2 GB for Qwen2.5-1.5B f32); names with a SoC (`sm8750`, `mt6989`, `Tensor_G5`) are compiled for that NPU; `_gpu` and `_web` are backend-specific builds. Recipe 2 uses the `q8_ekv4096` file (`ekv4096` = 4096-token KV cache).

## Related

- [Can I run a PyTorch model on Android without going through ONNX?](pytorch-model-on-android-without-onnx.md)
- [How do I run a fine-tuned Hugging Face model on iPhone?](fine-tuned-hf-model-on-iphone.md)

## Provenance

<!-- gen:provenance:android-llm-chat:start -->
- Converted and verified by: litert-community (Google AI Edge) published the bundle; integration and verification by john-rocky
- Recipe: https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/INTEGRATION.md
- Measurements: https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/INTEGRATION.md#7-verified--unverified
- Commit: john-rocky/on-device-recipes@086a791 (086a791 adds the recipe, the drop-in files, the test and the device rows above; this field is set in the follow-up commit)
- Maintained at: https://github.com/john-rocky/on-device-recipes/issues
<!-- gen:provenance:android-llm-chat:end -->

This page is the canonical text. Article copies (dev.to, Zenn, Medium) are snapshots that link back here and are not edited after publishing; corrections land here first. The bundle list is regenerated by `tools/render.py --fetch`; the date above it is the date it was read.
