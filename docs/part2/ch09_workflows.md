# Chapter 9: Pipelines, Automation, and Continuous Integration

:::{admonition} What You Will Learn
:class: tip

- How workflow managers turn a sequence of scripts into a rerunnable pipeline
- How to choose between Make, Snakemake, Nextflow, and R's targets
- How to use GitHub Actions to check automatically that your code still runs
- Simple tests that catch broken models and bad data
- How scheduled checks catch problems before your readers do
:::

## Which Scripts, in Which Order?

A typical AI project has several steps: download data, clean it, split it, extract features, train, evaluate, and make figures. Early on, you run these by hand. Months later, the README says "run the scripts in order," but nobody remembers that `clean.py` has to be run twice, or that `features.py` needs a folder that only `split.py` creates.

A **pipeline** writes down the steps and their dependencies as code, so the whole analysis can be rerun with one command. Pipelines also know which steps are already up to date. If you change only the plotting script, they rerun only the plotting step, not the three-hour training job.

**Continuous integration** (CI) goes one step further: every time you push code, a server rebuilds your environment from scratch and runs your pipeline (or a small version of it). If something breaks, you find out in minutes, not months.

## From Scripts to Pipelines

### Make

`make` is the oldest and simplest option. It is available on almost every Linux and Mac system. You write a `Makefile` listing each output, its inputs, and the command that produces it:

```makefile
data/processed/train.parquet: data/raw/survey.csv scripts/clean.py
	python scripts/clean.py

models/model.pt: data/processed/train.parquet configs/baseline.yaml scripts/train.py
	python scripts/train.py --config configs/baseline.yaml

results/figures/fig2.png: models/model.pt scripts/plot.py
	python scripts/plot.py

all: results/figures/fig2.png
```

Running `make all` runs only the steps whose inputs have changed since the output was last built. Make is a good choice for small projects with a handful of steps.

### Snakemake and Nextflow

**Snakemake** is a Python-based workflow manager widely used in bioinformatics and increasingly elsewhere. It uses a Make-like rule syntax with Python, handles wildcards (for example, running the same step for every sample or every seed), integrates with Conda and containers per step, and can submit jobs to Slurm clusters like Great Lakes.

**Nextflow** is popular for large genomics and data processing pipelines. It emphasizes portability across laptops, clusters, and clouds, and has a large library of community pipelines through nf-core.

Both are worth learning if your pipeline has many steps, many samples, or needs to run on a cluster.

### Hands-On: A Snakemake Pipeline with Multiple Seeds

This Snakefile cleans the data once, trains the model with five seeds (Chapter 7), summarizes the results, and makes a figure. The `{seed}` wildcard turns one rule into five jobs:

```python
# Snakefile
SEEDS = [0, 1, 2, 3, 4]

rule all:
    input:
        "results/tables/seed_summary.csv",
        "results/figures/accuracy_by_seed.png"

rule clean:
    input: "data/raw/survey.csv", "scripts/clean.py"
    output: "data/processed/train.parquet"
    shell: "python scripts/clean.py {input[0]} {output}"

rule train:
    input: "data/processed/train.parquet", "configs/baseline.yaml"
    output: "runs/seed{seed}/metrics.json"
    shell: "python scripts/train.py --config {input[1]} seed={wildcards.seed} --out runs/seed{wildcards.seed}"

rule summarize:
    input: expand("runs/seed{seed}/metrics.json", seed=SEEDS)
    output: "results/tables/seed_summary.csv"
    shell: "python scripts/summarize.py {input} > {output}"

rule plot:
    input: "results/tables/seed_summary.csv"
    output: "results/figures/accuracy_by_seed.png"
    shell: "python scripts/plot.py {input} {output}"
```

```bash
pip install snakemake
snakemake -n --cores 1          # dry run: list what would run, without running it
snakemake --cores 4             # run up to four jobs in parallel
snakemake --dag | dot -Tpng > pipeline.png   # draw the pipeline (needs Graphviz)
```

The dry run prints a summary like this, which is a useful sanity check before a long run:

```text
Job stats:
job          count
---------  -------
clean            1
train            5
summarize        1
plot             1
all              1
total            9
```

If you then edit only `scripts/plot.py`, rerunning Snakemake regenerates only the figure. If you edit `configs/baseline.yaml`, it reruns all five training jobs and everything downstream. Snakemake can also submit each job to Slurm on Great Lakes through its executor plugins, so the same Snakefile runs on a laptop and a cluster.

### targets for R

The **targets** package brings pipeline management to R. You define targets as R function calls in a `_targets.R` file, and `tar_make()` runs only what is out of date. It integrates well with `renv` (Chapter 5) and Quarto reports.

```r
# _targets.R
library(targets)
tar_option_set(packages = c("readr", "dplyr", "ranger"))
source("R/functions.R")          # clean_data(), fit_model(), summarize_fit()

list(
  tar_target(raw_file, "data/raw/survey.csv", format = "file"),   # tracks file contents
  tar_target(clean, clean_data(raw_file)),
  tar_target(seed, 0:4),
  tar_target(fit, fit_model(clean, seed), pattern = map(seed)),   # one fit per seed
  tar_target(summary, summarize_fit(fit))
)
```

Run `targets::tar_make()` to build everything, `targets::tar_visnetwork()` to see the pipeline, and `targets::tar_outdated()` to see what would rerun.

Choose the tool that fits your language and your field's conventions. The important step is moving from "run these in order" to a file that encodes the order.

## Continuous Integration for Research Code

GitHub Actions is a CI service built into GitHub. It is free for public repositories on standard runners, and includes monthly free minutes for private repositories. You describe what should happen in a YAML file in `.github/workflows/`.

Here is a workflow that rebuilds your environment from the lockfile and runs a smoke test on every push:

```yaml
# .github/workflows/smoke-test.yml
name: smoke-test
on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - name: Install exact environment
        run: uv sync --frozen
      - name: Run tests
        run: uv run pytest tests/
      - name: Smoke-test the pipeline on a tiny sample
        run: uv run python scripts/train.py --config configs/smoke.yaml
```

The key idea is the **smoke test**: a run of your real pipeline on a tiny sample of data, with very few epochs, that finishes in a minute or two. It does not check that the model is good. It checks that the code runs end to end in a fresh environment built only from what is in the repository. That alone catches most reproducibility failures: a missing dependency, a hard-coded path to your laptop, a file you forgot to commit.

To make this work, commit a small sample of data (or synthetic data with the same structure) to `tests/data/`, and create a `configs/smoke.yaml` that points to it with minimal training settings:

```yaml
# configs/smoke.yaml: same structure as baseline.yaml, tiny settings
seed: 0
data:
  path: tests/data/sample.parquet   # 50-200 rows committed to the repository
  version: smoke
  test_size: 0.5
model:
  name: resnet18
  pretrained: false                 # avoid downloading weights in CI
training:
  epochs: 1
  batch_size: 8
  learning_rate: 0.001
```

If you cannot commit even a sample of the real data, generate a synthetic sample with the same columns and types (Chapter 19). The goal is to exercise the code path, not to get a meaningful result.

If your project is in R, the same idea works with the `r-lib/actions` workflows:

```yaml
# .github/workflows/r-check.yml
name: r-check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: r-lib/actions/setup-r@v2
        with:
          r-version: "4.4.1"
      - uses: r-lib/actions/setup-renv@v2     # restores packages from renv.lock
      - run: Rscript -e 'targets::tar_make()'
        env:
          SMOKE_TEST: "true"                    # have your functions use the sample data
```

CI runners do not have GPUs by default. Write your code so that it falls back to CPU when no GPU is available, which also helps users on modest hardware (Chapter 21).

## Testing Models

Software engineers write extensive unit tests. Research code rarely needs that level of coverage, but a few targeted tests catch a surprising number of problems.

**Shape and range tests** check that a model produces outputs of the right shape and in a sensible range:

```python
# tests/test_model.py
import torch
from my_project.model import build_model

def test_output_shape_and_probabilities():
    model = build_model(num_classes=4)
    x = torch.randn(2, 3, 224, 224)
    probs = model(x).softmax(dim=-1)
    assert probs.shape == (2, 4)
    assert torch.allclose(probs.sum(dim=-1), torch.ones(2), atol=1e-5)
```

**Golden output tests** load your released model, run it on a fixed input, and compare against saved outputs with a tolerance. If a library update changes your model's predictions, this test fails:

```python
def test_released_model_matches_reference():
    model = load_released_model()
    x = torch.load("tests/data/reference_input.pt")
    expected = torch.load("tests/data/reference_output.pt")
    assert torch.allclose(model(x), expected, atol=1e-4)
```

Use a tolerance, not exact equality, for the hardware reasons discussed in Chapter 7. You create the reference files once, when you release the model, and commit them:

```python
# scripts/make_reference_outputs.py: run once per model release
import torch
torch.manual_seed(0)
model = load_released_model().eval()
x = torch.randn(4, 3, 224, 224)            # fixed random input; or a few real examples
with torch.no_grad():
    y = model(x)
torch.save(x, "tests/data/reference_input.pt")
torch.save(y, "tests/data/reference_output.pt")
```

**Data validation tests** check that input data have the expected columns, types, and value ranges. Libraries such as `pandera` (Python) and `pointblank` or `validate` (R) let you write these as schemas. A failing data check is much easier to debug than a model that silently trained on corrupted data.

Here is a pandera schema for the air quality data dictionary from Chapter 17, written as two pytest tests: one that checks the committed sample, and one that confirms the schema actually catches problems:

```python
# tests/test_data.py
import pandas as pd
import pandera.pandas as pa
import pytest

schema = pa.DataFrameSchema(
    {
        "site_id": pa.Column(str, pa.Check.str_matches(r"^DET-\d{3}$")),
        "year": pa.Column(int, pa.Check.in_range(2015, 2024)),
        "pm25": pa.Column(float, pa.Check.in_range(0, 500), nullable=True),
        "flag": pa.Column(int, pa.Check.isin([0, 1, 2])),
    },
    unique=["site_id", "year"],     # one row per site per year
    strict=True,                    # no unexpected columns
)

def test_processed_data_matches_schema():
    df = pd.read_csv("tests/data/sample.csv")
    schema.validate(df, lazy=True)  # lazy=True reports every problem, not just the first

def test_schema_catches_bad_rows():
    bad = pd.DataFrame({"site_id": ["DET-014", "DET-014"], "year": [2020, 2020],
                        "pm25": [8.1, -3.0], "flag": [0, 5]})
    with pytest.raises(pa.errors.SchemaErrors):
        schema.validate(bad, lazy=True)
```

```bash
pip install pandera pytest
pytest -q
```

When validation fails, pandera lists every problem it found:

```text
 column                      check failure_case
site_id multiple_fields_uniqueness      DET-014
site_id multiple_fields_uniqueness      DET-014
   year multiple_fields_uniqueness         2020
   year multiple_fields_uniqueness         2020
   pm25           in_range(0, 500)         -3.0
   flag            isin([0, 1, 2])            5
```

Call `schema.validate(df)` at the start of your training script as well, so that bad data stops the pipeline before any model is trained. The same schema then serves as executable documentation of what valid data looks like.

## Scheduled Rebuilds

Some things break even when you change nothing. A package you did not pin releases an incompatible version. A base image is updated. A dataset URL stops working. To catch these, run your CI workflow on a schedule as well as on every push:

```yaml
on:
  push:
  schedule:
    - cron: "0 6 * * 1"   # every Monday at 06:00 UTC
```

A scheduled job can also download your published artifacts (from Hugging Face, Zenodo, or Deep Blue Data), verify checksums, and run the golden output test. If anything fails, GitHub emails you. This turns "is my model still available and working?" from a question you never ask into one that is answered every week. Chapter 20 describes how the same approach can monitor Model Zoo entries.

## Building Containers Automatically

If you publish a container image (Chapter 6), CI can build and push it whenever you create a release, so the image always matches the tagged code. GitHub provides ready-made actions for logging in to GitHub Container Registry and building and pushing images. This removes the risk that the published image was built from uncommitted local changes.

## Try This

Add a smoke-test workflow to one of your repositories. Create a tiny data sample and a smoke config that runs your pipeline in under two minutes on a CPU. Push, and watch the workflow run in the Actions tab. The first run will probably fail. Fix each failure until it passes; each fix is a reproducibility problem you would otherwise have discovered much later.

## Further Reading

The Snakemake, Nextflow, and targets documentation each include tutorials. The GitHub Actions documentation has starter workflows for Python and R. Software Carpentry and The Turing Way {footcite}`TheturingwayTeam2022` both have chapters on testing research code.

## In the Model Zoo

Scheduled checks are a candidate feature for the Model Zoo itself: an automated job that periodically confirms each entry's links work and, for "Reproducible" tier entries, that the quickstart runs.

## Related Chapters

- [Chapter 6: Containers for Reproducible Models](ch06_containers.md)
- [Chapter 11: Testing Reproducibility Before You Share](ch11_testing_reproducibility.md)
- [Chapter 20: Making Sure It Stays Shared](../part3/ch20_persistence.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
