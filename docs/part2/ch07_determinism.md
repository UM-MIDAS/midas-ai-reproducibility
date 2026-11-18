# Chapter 7: Randomness, Determinism, and Hardware

:::{admonition} What You Will Learn
:class: tip

- Where randomness enters model training and inference
- How to seed Python, NumPy, scikit-learn, PyTorch, TensorFlow, and JAX
- Why GPUs can give different answers from run to run, and what to do about it
- How to report results accurately when exact reproduction is impossible
- Special considerations for hosted large language models
:::

## Same Code, Same Data, Different Answer

You train a model, get 87.3% accuracy, and write it down. A week later you rerun the exact same script on the exact same data, with the exact same environment, and get 86.1%. Nothing changed. What happened?

Almost certainly, randomness. Machine learning is full of it: weights are initialized randomly, training data are shuffled, dropout switches off random neurons, data augmentation applies random transformations, and train-test splits are drawn at random. Each of these is controlled by a pseudo-random number generator, and if you do not set its starting point (the seed), you get a different sequence every time.

Randomness is not a flaw. It is part of how these methods work. But it has two consequences for reproducibility. First, you need to control it so that your own results are repeatable. Second, you need to measure it, because a single run tells you very little about how good a method really is.

## Sources of Randomness

It helps to list them explicitly, since each needs its own control.

**Data splitting.** Train, validation, and test splits, and cross-validation folds.

**Initialization.** The starting values of model weights.

**Data order.** Shuffling at each epoch, and the order in which parallel data loader workers deliver batches.

**Stochastic layers.** Dropout and some normalization layers.

**Augmentation.** Random crops, flips, rotations, and noise.

**Sampling at inference.** Text generation with temperature above zero, or Monte Carlo dropout.

**Hardware and parallelism.** Some GPU operations use parallel algorithms that add floating point numbers in a different order each time. Because floating point addition is not perfectly associative, the results differ in the last few digits, and in a deep network those tiny differences can compound.

The first six are controlled by seeds. The last one requires additional settings, and sometimes cannot be fully controlled.

## Seeding Properly

Each library has its own random number generator, so you need to seed all of them. A common pattern is a single utility function called at the start of every script:

```python
import os, random
import numpy as np

def set_seed(seed: int = 42, deterministic: bool = False):
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch
        torch.manual_seed(seed)            # seeds CPU and all GPUs
        if deterministic:
            os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
            torch.use_deterministic_algorithms(True)
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass
    try:
        import tensorflow as tf
        tf.keras.utils.set_random_seed(seed)  # seeds Python, NumPy, and TF
        if deterministic:
            tf.config.experimental.enable_op_determinism()
    except ImportError:
        pass
```

A few library-specific notes.

**scikit-learn** does not use a global seed reliably. Pass `random_state=` explicitly to every function and estimator that accepts it: `train_test_split`, `KFold`, `RandomForestClassifier`, and so on.

**PyTorch data loaders** with multiple workers need extra care. Pass a seeded generator and a worker initialization function so each worker gets a predictable seed:

```python
g = torch.Generator()
g.manual_seed(42)

def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)

loader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=4,
                    worker_init_fn=seed_worker, generator=g)
```

**JAX** handles randomness differently: there is no global state. You create a key with `jax.random.PRNGKey(seed)` and explicitly split and pass keys to every random operation. This makes JAX code more verbose but much easier to reason about.

**R** uses `set.seed()`. Note that the default random number algorithm changed in R 3.6.0, so results with the same seed can differ between old and new R versions. Record your R version.

Save the seed with your results (Chapter 8). A seed that is set but not recorded is almost as bad as no seed.

### Hands-On: See Seed Variation for Yourself

This example uses scikit-learn and a small dataset that ships with it, so it runs in seconds on any laptop or in Colab. It trains the same small neural network several times, first with the same seed, then with different model seeds, then with different train-test splits.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)

def run(model_seed, split_seed=0):
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.3, random_state=split_seed, stratify=y)
    clf = make_pipeline(
        StandardScaler(),
        MLPClassifier(hidden_layer_sizes=(16,), max_iter=300, random_state=model_seed))
    clf.fit(X_tr, y_tr)
    return clf.score(X_te, y_te)

# Same seed twice: identical results
print(run(model_seed=1), run(model_seed=1))

# Different seeds, same data split
for seed in range(5):
    print(f"model seed {seed}: accuracy = {run(model_seed=seed):.4f}")

# Different data splits, same model seed
for split in range(5):
    print(f"split seed {split}: accuracy = {run(model_seed=0, split_seed=split):.4f}")
```

Output:

```text
0.9532163742690059 0.9532163742690059
model seed 0: accuracy = 0.9532
model seed 1: accuracy = 0.9532
model seed 2: accuracy = 0.9591
model seed 3: accuracy = 0.9591
model seed 4: accuracy = 0.9474
split seed 0: accuracy = 0.9532
split seed 1: accuracy = 0.9708
split seed 2: accuracy = 0.9708
split seed 3: accuracy = 0.9766
split seed 4: accuracy = 0.9649
```

Three lessons are visible here. With the same seed, results are identical, which is what makes a run repeatable. Different model seeds move accuracy by about one percentage point. And different data splits move it by nearly three points, more than the model seed. On small datasets, which test examples you happen to draw often matters more than anything else, which is why the next section recommends varying both.

Your exact numbers may differ slightly from these if you use different library versions, which is itself a small demonstration of Chapter 5.

### Hands-On: Checking PyTorch Determinism

For deep learning code, the most direct test is to train twice with the same seed and compare the resulting weights:

```python
import torch

def train_once(seed):
    set_seed(seed, deterministic=True)          # from the function above
    model = build_model()                       # your model
    train(model, make_loader(seed))             # your training loop and seeded DataLoader
    return {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

a, b = train_once(42), train_once(42)
mismatched = [k for k in a if not torch.equal(a[k], b[k])]
print("bit-identical" if not mismatched else f"{len(mismatched)} tensors differ, e.g. {mismatched[:3]}")
```

If tensors differ with `deterministic=True`, something is still unseeded, most often a data loader worker or a custom augmentation using Python's `random` module. If PyTorch raises an error naming an operation without a deterministic implementation, you can either replace that operation or accept the nondeterminism and document it.

## Hardware Nondeterminism

Seeding controls the random number generators. It does not control the order of floating point operations on a GPU. Some GPU operations, including certain convolution algorithms and operations that use atomic additions (such as scatter operations and some backward passes), produce slightly different results on each run even with identical seeds.

PyTorch's `torch.use_deterministic_algorithms(True)` and TensorFlow's `enable_op_determinism()` force deterministic implementations where they exist, and raise an error when an operation has no deterministic version. The cost is speed: deterministic algorithms can be noticeably slower. A reasonable approach is to turn determinism on while debugging and for final reported runs, and off during exploration.

Even with full determinism enabled, you should not expect bit-for-bit identical results across different hardware. A model trained on an NVIDIA A100 and one trained on a V100 or an Apple Silicon GPU will differ slightly, as will results from different CUDA or library versions. The practical goal is to make results **repeatable on the same setup** and **statistically consistent across setups**, not identical to the last decimal place everywhere. When you report results, state the hardware, and when you check reproducibility, compare against a tolerance rather than exact equality.

## Reporting Variability

Seeding makes a single run repeatable. It does not make a single run representative. Studies of ML benchmarks have shown that the variation from random seeds, data splits, and other sources can be as large as the improvements papers claim between methods {footcite}`bouthillier2021`. If you train once and report one number, a reader cannot tell whether your method is better or whether you got a lucky seed.

Good practice is to:

- Train with several seeds (five is a common minimum; more if runs are cheap).
- Report the mean and a measure of spread, such as the standard deviation or a confidence interval.
- Vary the data split as well as the model seed when the dataset is small.
- Report all runs, not just the best one. Choosing the best of many seeds and reporting it as "the" result is a form of overfitting to the test set.

When comparing two methods, use the same set of seeds for both, and consider a paired statistical test across seeds.

### Hands-On: A Multi-Seed Comparison

This example compares the small neural network from above with logistic regression across ten seeds, each controlling both the data split and the model, and reports a mean, standard deviation, and 95% confidence interval for each:

```python
import numpy as np
from scipy import stats
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)

def evaluate(make_model, seeds):
    """Train and score one model per seed; the seed controls both split and model."""
    scores = []
    for seed in seeds:
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.3, random_state=seed, stratify=y)
        model = make_pipeline(StandardScaler(), make_model(seed))
        scores.append(model.fit(X_tr, y_tr).score(X_te, y_te))
    return np.array(scores)

def summarize(name, scores):
    mean, sd = scores.mean(), scores.std(ddof=1)
    half = stats.t.ppf(0.975, len(scores) - 1) * sd / np.sqrt(len(scores))
    print(f"{name:8} mean={mean:.4f}  sd={sd:.4f}  95% CI=[{mean-half:.4f}, {mean+half:.4f}]")

seeds = range(10)
mlp = evaluate(lambda s: MLPClassifier((16,), max_iter=300, random_state=s), seeds)
logreg = evaluate(lambda s: LogisticRegression(max_iter=1000, random_state=s), seeds)

summarize("MLP", mlp)
summarize("LogReg", logreg)

# Same seeds for both models, so compare them pairwise
diff = mlp - logreg
t, p = stats.ttest_rel(mlp, logreg)
print(f"mean difference = {diff.mean():+.4f}, paired t-test p = {p:.3f}")
print(f"MLP better on {np.sum(diff > 0)} of {len(diff)} seeds, worse on {np.sum(diff < 0)}")
```

Output:

```text
MLP      mean=0.9690  sd=0.0123  95% CI=[0.9602, 0.9778]
LogReg   mean=0.9719  sd=0.0106  95% CI=[0.9643, 0.9795]
mean difference = -0.0029, paired t-test p = 0.273
MLP better on 3 of 10 seeds, worse on 5
```

Had you run each model once with seed 0, you might have reported that one was better. Across ten seeds, the confidence intervals overlap heavily, the paired difference is small and not statistically distinguishable from zero, and each model wins on some seeds. The defensible conclusion is that the two perform similarly on this dataset. Reporting results this way takes a few extra lines of code and protects you from publishing a lucky draw.

For repeated train-test splits, the samples are not fully independent, so treat the t-test as a rough guide rather than an exact p-value. Bouthillier and colleagues {footcite}`bouthillier2021` discuss more rigorous approaches.

## Large Language Models and Hosted APIs

Research that uses large language models, whether through a commercial API or a locally hosted open-weight model, has its own reproducibility challenges.

**Models change under the same name.** A model alias such as "the latest version" may point to different underlying models over time. Always use a dated or versioned model identifier when the provider offers one, and record it.

**Models get retired.** Providers deprecate older models, sometimes within a year or two. A study that depends on a hosted model may become impossible to rerun exactly. Open-weight models that you download and archive (with a pinned revision, as in Chapter 14) avoid this.

**Temperature zero is not fully deterministic.** Setting temperature to zero makes the model choose the most likely token at each step, which reduces variation a great deal. But hosted inference servers batch requests from many users together, and the numerical results of the underlying computations can depend on batch size. Researchers at Thinking Machines Lab showed that this lack of "batch invariance" is a main reason why identical prompts at temperature zero can still produce different outputs on typical inference servers {footcite}`he2025`. Some providers offer a `seed` parameter that improves consistency, but it is generally described as best-effort.

**Practical steps for LLM-based research:**

- Record the exact model identifier, provider, date, and all parameters (temperature, top-p, max tokens, system prompt).
- Log every prompt and every response in full. The logged outputs are your data; treat them as a dataset that you archive and share.
- Run each prompt more than once and report the variation.
- Where possible, use an open-weight model with a pinned version for the core analysis, and use hosted models for comparison.

### Hands-On: Log Every LLM Call

A small wrapper around whatever client you use makes complete logging automatic. It works with any provider, because you pass in the function that actually makes the call:

```python
import hashlib, json, time, uuid
from datetime import datetime, timezone

def logged_call(call_fn, *, model, messages, params, log_path="runs/llm_log.jsonl", **meta):
    """Call an LLM through `call_fn` and append a complete record to a JSONL log.

    call_fn: any function that takes (model, messages, **params) and returns text.
    meta: anything else worth recording, such as task or item IDs.
    """
    started = time.time()
    output = call_fn(model=model, messages=messages, **params)
    record = {
        "id": str(uuid.uuid4()),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": model,                       # use a dated/versioned model ID
        "params": params,                     # temperature, max tokens, seed, ...
        "messages": messages,                 # full prompt, including system prompt
        "prompt_sha256": hashlib.sha256(json.dumps(messages, sort_keys=True).encode()).hexdigest(),
        "output": output,
        "latency_s": round(time.time() - started, 3),
        **meta,
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return output
```

Use it in place of direct calls, repeating each prompt a few times:

```python
for repeat in range(3):
    label = logged_call(my_client_call, model="provider-model-2026-01-15",
                        messages=msgs, params={"temperature": 0, "max_tokens": 5},
                        item_id="doc_0042", repeat=repeat)
```

Because the log is a JSON Lines file, it loads directly into pandas, and you can check how often repeated calls disagree:

```python
import pandas as pd
log = pd.read_json("runs/llm_log.jsonl", lines=True)
agreement = log.groupby("prompt_sha256")["output"].nunique()
print(f"{(agreement > 1).mean():.1%} of prompts gave more than one distinct answer")
```

The log file is a research dataset in its own right. Archive it with your other data (Chapter 16), since it may be the only way anyone can check your results once the model is retired.

## Try This

Train a small model (for example, the tabular or text model from the AI in Research Handbook's companion notebooks) three times without setting a seed, and record the results. Then add `set_seed()` and train three more times. Finally, train with five different seeds and compute the mean and standard deviation. How large is the seed-to-seed variation compared with the differences you would normally consider meaningful?

## Further Reading

The PyTorch documentation has a page on reproducibility that lists which operations are nondeterministic. Bouthillier and colleagues {footcite}`bouthillier2021` quantify how much variance matters in ML benchmarks. The Thinking Machines post on LLM nondeterminism {footcite}`he2025` is a readable technical explanation of why temperature zero is not enough.

## Related Chapters

- [Chapter 5: Managing Software Environments](ch05_environments.md)
- [Chapter 8: Experiment Tracking and Provenance](ch08_experiment_tracking.md)
- [Chapter 10: Documenting Models](ch10_documenting_models.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
