# Chapter 21: AI on Modest Hardware

:::{admonition} What You Will Learn
:class: tip

- How to estimate the memory a model needs, and why that decides what hardware you can use
- How quantization, distillation, and small models make AI usable without large GPUs
- Tools for running models on laptops and CPUs
- How parameter-efficient fine-tuning lets you adapt large models on a single GPU
- Free and low-cost compute options for researchers, students, and U-M users
- How to design your releases for users with limited resources
:::

## Open Is Not the Same as Usable

A model can be fully open, with public weights, a permissive license, and excellent documentation, and still be out of reach for most people who might use it. If running it requires several high-end data center GPUs, then in practice only well-funded labs and companies can use it. Students, researchers at smaller institutions, community organizations, researchers in lower-income countries, and many U-M researchers without dedicated GPU allocations are left out.

This chapter is about the second meaning of accessible from Chapter 1: can I run it? It covers how to estimate what hardware a model needs, how to make models smaller and faster, and where to find free or low-cost compute. It is useful whether you are trying to use someone else's model on limited hardware or trying to make your own model usable by more people.

## Estimating What You Need

The most common limit is memory: a model's weights must fit in the memory of the device running it (GPU memory for GPU inference, system RAM for CPU inference), with room to spare for inputs and intermediate calculations.

A simple estimate for the weights alone is:

> **memory ≈ number of parameters × bytes per parameter**

The bytes per parameter depend on the numerical precision:

| Precision | Bytes per parameter | 7 billion parameter model |
|---|---|---|
| FP32 (32-bit float) | 4 | ~28 GB |
| FP16 / BF16 (16-bit) | 2 | ~14 GB |
| INT8 (8-bit) | 1 | ~7 GB |
| 4-bit | 0.5 | ~3.5 GB |

Add some overhead, commonly 10–20% or more, for activations and, for language models, the cache that grows with the length of the input and output. A 7-billion-parameter language model at 16-bit precision will not fit on a 12 GB consumer GPU, but at 4-bit precision it runs comfortably on a laptop with 8–16 GB of memory.

**Training needs much more memory than inference.** In addition to the weights, training stores gradients and optimizer states. With the common Adam optimizer, full training can need roughly four times the memory of the weights alone, or more. This is why the techniques in the "Efficient Fine-Tuning" section below matter.

### Hands-On: A Memory Calculator

The same arithmetic as a small function, so you can check any model before downloading it:

```python
def estimate_memory_gb(n_params, bits=16, overhead=0.2, training=False):
    """Rough memory needed to run (or train) a model.

    n_params: number of parameters, e.g. 7e9 for a 7B model
    bits:     precision of the weights: 32, 16, 8, or 4
    overhead: extra fraction for activations, caches, and framework buffers
    training: full training with Adam in mixed precision needs roughly
              16 bytes per parameter for weights, gradients, and optimizer states
    """
    weights_gb = n_params * bits / 8 / 1e9
    if training:
        weights_gb = n_params * 16 / 1e9          # ~16 bytes per parameter (mixed precision + Adam)
    return round(weights_gb * (1 + overhead), 2)

for name, n in [("BERT-base", 110e6), ("7B LLM", 7e9), ("70B LLM", 70e9)]:
    row = {f"{b}-bit": estimate_memory_gb(n, b) for b in (32, 16, 8, 4)}
    print(f"{name:10} inference GB {row}   full training ~{estimate_memory_gb(n, training=True)} GB")
```

```text
BERT-base  inference GB {'32-bit': 0.53, '16-bit': 0.26, '8-bit': 0.13, '4-bit': 0.07}   full training ~2.11 GB
7B LLM     inference GB {'32-bit': 33.6, '16-bit': 16.8, '8-bit': 8.4, '4-bit': 4.2}   full training ~134.4 GB
70B LLM    inference GB {'32-bit': 336.0, '16-bit': 168.0, '8-bit': 84.0, '4-bit': 42.0}   full training ~1344.0 GB
```

Read the table against your hardware. A laptop with 16 GB of memory can run a 7B model at 8-bit or 4-bit precision, but not at 16-bit. A single 80 GB data center GPU can run a 70B model only at 4-bit or 8-bit, and could not fully train even the 7B model, which is why the parameter-efficient methods below matter. To find a model's parameter count, check its model card, or load it and run `sum(p.numel() for p in model.parameters())`.

[Chapter 31 of the AI in Research Handbook](https://midas-ai-in-research.readthedocs.io/en/main/part4/ch31_computing_fundamentals.html) explains precision, memory bandwidth, and how to estimate speed from GPU specifications in more detail.

## Smaller and Faster Models

### Start Small

The most effective technique is often to choose a smaller model in the first place. For many research tasks such as classification, extraction, and embedding, a model with a few hundred million parameters performs nearly as well as one with tens of billions, especially after fine-tuning on your task. Model families usually come in several sizes. Try the smallest one first, and move up only if it is not good enough.

### Quantization

**Quantization** stores model weights at lower precision, for example 8-bit or 4-bit integers instead of 16-bit floating point numbers. This reduces memory by two to four times and often speeds up inference, usually with a small loss in accuracy. For large language models, 4-bit quantization is widely used and often preserves most of the model's quality. Smaller models tend to be more sensitive to aggressive quantization, so always evaluate a quantized model on your own task.

Common approaches include:

- **bitsandbytes** integration in Hugging Face `transformers`, which loads models in 8-bit or 4-bit with a single argument.
- **GGUF** files, a format used by `llama.cpp` and related tools, available in many quantization levels for popular open models.
- **GPTQ and AWQ**, quantization methods that calibrate on sample data to preserve accuracy.

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
model = AutoModelForCausalLM.from_pretrained(
    "your-org/your-model",
    quantization_config=BitsAndBytesConfig(load_in_4bit=True),
    device_map="auto",
)
```

### Distillation and Pruning

**Knowledge distillation** trains a smaller "student" model to imitate a larger "teacher." The result can keep much of the teacher's accuracy at a fraction of the size. A well-known example is DistilBERT, which was 40% smaller and 60% faster than BERT while retaining about 97% of its language understanding performance on a benchmark suite {footcite}`sanh2019`. If you have trained a large model for a specific task, distilling it into a smaller one is a way to make it much more widely usable.

**Pruning** removes weights or entire components that contribute little to the output. It is less commonly used by researchers than quantization and distillation, but can be effective for specific architectures.

## CPU and Laptop Inference

Many models run well enough on a CPU for research use, especially for processing a moderate number of examples.

**ONNX Runtime** runs models exported to the ONNX format efficiently on CPUs (and GPUs), often much faster than running the original PyTorch or TensorFlow model on a CPU. Hugging Face's Optimum library can export many models to ONNX.

**llama.cpp** runs quantized language models (in GGUF format) efficiently on ordinary CPUs and Apple Silicon. **Ollama** wraps it in a simple tool for downloading and running models locally with one command. These tools make it practical to run capable language models on a laptop with no internet connection, which is also useful for privacy-sensitive work.

**Apple Silicon** Macs share memory between CPU and GPU, so a Mac with 32 GB or more of memory can run surprisingly large quantized models. PyTorch supports the Apple GPU through the `mps` device, and Apple's MLX framework is designed specifically for these machines.

Getting a quantized open-weight language model running locally with Ollama takes two commands, and Ollama also exposes a local API that your scripts can call:

```bash
ollama pull llama3.2:3b          # downloads a 4-bit quantized model (~2 GB)
ollama run llama3.2:3b "Summarize the FAIR principles in two sentences."
```

```python
import requests
r = requests.post("http://localhost:11434/api/generate",
                  json={"model": "llama3.2:3b", "prompt": "Define reproducibility in one sentence.",
                        "stream": False, "options": {"temperature": 0, "seed": 42}})
print(r.json()["response"])
```

Model names and sizes change frequently; browse the Ollama library for current options, and record the exact model tag you used (Chapter 7). Because everything runs on your own machine, this is also an option for text you cannot send to a hosted service.

### Hands-On: Export a Model to ONNX for Fast CPU Inference

ONNX is an open format for trained models that runs in ONNX Runtime on CPUs, GPUs, phones, and web browsers, without the original training library installed. This example uses a scikit-learn model so it runs anywhere; the export step for PyTorch is shown after it.

```python
import time
import numpy as np
import onnxruntime as ort
from skl2onnx import to_onnx
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier

X, y = make_classification(n_samples=20_000, n_features=30, random_state=0)
X = X.astype(np.float32)
model = RandomForestClassifier(n_estimators=200, random_state=0, n_jobs=1).fit(X, y)

# Convert once, save, and share the .onnx file alongside (or instead of) the pickle
onx = to_onnx(model, X[:1], options={"zipmap": False})   # plain arrays out, not dicts
with open("model.onnx", "wb") as f:
    f.write(onx.SerializeToString())

session = ort.InferenceSession("model.onnx", providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name

def timed(fn, repeats=5):
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter(); out = fn(); best = min(best, time.perf_counter() - start)
    return out, best

batch = X[:5000]
p_sk, t_sk = timed(lambda: model.predict_proba(batch))
p_ox, t_ox = timed(lambda: session.run(None, {input_name: batch})[1])

print(f"scikit-learn: {t_sk*1000:6.1f} ms   ONNX Runtime: {t_ox*1000:6.1f} ms")
print("max difference in probabilities:", float(np.abs(p_sk - p_ox).max()))

one = X[:1]                       # a single example, as in an interactive demo
_, t_sk1 = timed(lambda: model.predict_proba(one), repeats=50)
_, t_ox1 = timed(lambda: session.run(None, {input_name: one})[1], repeats=50)
print(f"single example -> scikit-learn: {t_sk1*1000:.2f} ms   ONNX Runtime: {t_ox1*1000:.2f} ms")
```

```text
scikit-learn:   99.4 ms   ONNX Runtime:  114.6 ms
max difference in probabilities: 7.748603820800781e-07
single example -> scikit-learn: 6.61 ms   ONNX Runtime: 0.01 ms
```

The results are instructive. On a large batch, ONNX Runtime was no faster for this model, so speed-ups are not guaranteed: always measure. On a single example, which is what an interactive demo does on every click, it was hundreds of times faster, because it avoids per-call overhead. The predictions agree to within one part in a million. And the `.onnx` file has advantages beyond speed: it does not depend on the scikit-learn version that trained it (pickled models often fail to load in other versions), and unlike a pickle it cannot execute code when loaded.

For PyTorch models, export with a sample input of the right shape:

```python
import torch
model.eval()
example = torch.randn(1, 3, 224, 224)
torch.onnx.export(model, example, "model.onnx",
                  input_names=["image"], output_names=["logits"],
                  dynamic_axes={"image": {0: "batch"}, "logits": {0: "batch"}})
```

For Hugging Face `transformers` models, the Optimum library handles export: `optimum-cli export onnx --model your-org/your-model onnx_model/`. Check that exported outputs match the original model within a small tolerance before sharing, as above.

Always write code that detects and falls back to available hardware:

```python
import torch
device = ("cuda" if torch.cuda.is_available()
          else "mps" if torch.backends.mps.is_available()
          else "cpu")
model.to(device)
```

## Efficient Fine-Tuning

Fine-tuning adapts a pretrained model to your task. Full fine-tuning updates every parameter and needs a lot of memory. **Parameter-efficient fine-tuning** (PEFT) methods update only a small number of added parameters and keep the original model frozen.

**LoRA** (Low-Rank Adaptation) adds small trainable matrices to certain layers. It typically trains well under 1% of the model's parameters, which greatly reduces memory needs, and produces a small "adapter" file that can be shared separately from the base model.

**QLoRA** combines LoRA with 4-bit quantization of the base model. Its authors showed it could fine-tune a 65-billion-parameter model on a single 48 GB GPU while matching the performance of 16-bit fine-tuning on their benchmarks {footcite}`dettmers2023`. Smaller models can be fine-tuned with QLoRA on a single consumer GPU or a free cloud GPU.

The Hugging Face PEFT library implements these methods, and the AI in Research Handbook includes a companion notebook on LoRA fine-tuning. Setting up QLoRA takes a few lines on top of the 4-bit loading shown earlier:

```python
import torch
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

base = AutoModelForCausalLM.from_pretrained(
    "your-org/base-model", revision="<pinned-commit>",
    quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                           bnb_4bit_compute_dtype=torch.bfloat16),
    device_map="auto")
base = prepare_model_for_kbit_training(base)

lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
                  target_modules=["q_proj", "v_proj"], task_type="CAUSAL_LM")
model = get_peft_model(base, lora)
model.print_trainable_parameters()   # typically well under 1% of all parameters
# ... train with your usual Trainer or training loop ...
model.save_pretrained("adapter/")    # saves only the small adapter, not the base model
```

The `target_modules` names depend on the model architecture; check the model's layer names, or the PEFT documentation, for the model family you use. Save the training config with the adapter, including the base model's exact revision.

Sharing a LoRA adapter rather than full fine-tuned weights has another benefit: adapters are small (often megabytes rather than gigabytes), so they are easy to host, download, and archive. Remember to record exactly which base model and revision the adapter was trained on.

## Free and Low-Cost Compute

Several options provide free or low-cost access to GPUs and larger computers. Availability and limits change frequently, so check each provider's current terms.

**Google Colab** offers free notebooks with limited, variable access to GPUs, with paid tiers for more reliable access. It is the easiest way to share a runnable tutorial (Chapter 24).

**Kaggle Notebooks** offer free CPU sessions and, with a verified account, a weekly GPU quota (Chapter 15).

**Hugging Face Spaces** can host demos. Free personal accounts can run a limited number of Gradio Spaces on shared ZeroGPU hardware (Chapter 22).

**GitHub Codespaces** provides a monthly free allowance of cloud development environments (CPU only), with additional benefits for students and educators.

**U-M Research Computing Package (UMRCP).** Eligible U-M researchers can receive no-cost allocations that include up to 80,000 CPU hours on Great Lakes and/or Armis2, up to 10 TB of Turbo active storage, and up to 100 TB of Data Den archive storage. GPU access on Great Lakes is available through its GPU partitions under paid or unit-sponsored accounts; check with ARC and your department about options.

**NSF ACCESS** allocates time on national supercomputing resources, including GPUs, to U.S. researchers and educators. Smaller "Explore" allocations have a lightweight application process suitable for getting started.

**The National AI Research Resource (NAIRR) Pilot** provides U.S. researchers and educators with access to computing, data, models, and software from federal and industry partners, through research allocations and classroom awards. In September 2026, NSF announced the award for a NAIRR Operations Center to build on the pilot, and existing opportunities remain available through nairrpilot.org during the transition.

**Cloud research credits** are offered by major cloud providers to academic researchers through application programs.

## Designing for the Low-Resource User

If you are releasing a model, a few choices make it much more accessible.

**Release more than one size.** If you trained a large model, also release a smaller or distilled version, or at least a quantized version. Many users will prefer a slightly less accurate model that runs on their hardware.

**Report hardware requirements in the model card.** State the memory needed for inference at each precision, whether a GPU is required, and how long inference takes on typical hardware, including a CPU. This saves users from discovering the hard way that your model does not fit.

**Make CPU inference work.** Make sure your code runs on a CPU, even if slowly, and include a CPU example. This also makes CI testing possible (Chapter 9).

**Provide a hosted demo.** A demo (Chapter 22) lets people evaluate your model before investing in hardware or setup.

**Share adapters.** If your model is a fine-tuned version of a public base model, share the LoRA adapter so users can apply it to a quantized version of the base model.

## Try This

Pick a model you use or have trained. Calculate its memory requirement at 16-bit and 4-bit precision using the formula above. Load it in 4-bit with bitsandbytes (on a GPU) or convert it to ONNX or GGUF (for CPU), and compare its accuracy on a small test set with the full-precision version. Add the results, including the hardware and inference time, to the model card.

## Further Reading

The Hugging Face documentation on quantization and the PEFT library describe practical workflows. The DistilBERT {footcite}`sanh2019` and QLoRA {footcite}`dettmers2023` papers are accessible introductions to distillation and efficient fine-tuning. The NAIRR Pilot and ACCESS websites describe current allocation opportunities.

## In the Model Zoo

A proposed Model Zoo field is "minimum hardware": the smallest configuration on which the model has been tested. Entries that run on a CPU or free cloud notebook, or that have a hosted demo, meet one of the criteria for the proposed "Accessible" tier.

## Related Chapters

- [Chapter 6: Containers for Reproducible Models](../part2/ch06_containers.md)
- [Chapter 22: Interactive Demos and Web Apps](ch22_demos.md)
- [Chapter 24: Accessible Documentation and Teaching Materials](ch24_accessible_docs.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
