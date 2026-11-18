# Chapter 8: Experiment Tracking and Provenance

:::{admonition} What You Will Learn
:class: tip

- How to answer "which code, data, and settings produced this number?" for any result
- How to move settings out of code and into configuration files
- Lightweight tracking with plain files, and when to adopt MLflow or Weights & Biases
- How to version the data a model was trained on
- How to link each figure and table in a paper to the run that produced it
:::

## The Provenance Question

Six months after submission, a reviewer asks: "The accuracy in Table 2 is 0.91, but the supplementary figure suggests 0.89. Which is correct?" To answer, you need to know which code version, which dataset version, which hyperparameters, which seed, and which environment produced each number. If you have to reconstruct that from memory and old folders, you are in trouble.

**Provenance** is the record of where a result came from. For computational work, it means the chain of code, data, configuration, and environment that produced an output. Chapter 4 set up version control for code, and Chapter 5 set up lockfiles for environments. This chapter ties them together with the other two ingredients, configuration and data, and records all four for every run.

The goal is simple to state: for any number in your paper, you should be able to point to a run ID, and that run ID should tell you everything needed to reproduce it.

## Configuration as Data

The first step is to stop hard-coding settings. Learning rates, batch sizes, model sizes, file paths, and seeds scattered through a script are hard to track and easy to change by accident. Move them into a configuration file:

```yaml
# configs/baseline.yaml
seed: 42
data:
  path: data/processed/train.parquet
  version: v2.1
  test_size: 0.2
model:
  name: resnet18
  pretrained: true
training:
  epochs: 20
  batch_size: 64
  learning_rate: 0.001
```

Your script reads this file, and you save a copy of it with every run's outputs. To try a different learning rate, you create a new config (or override a single value from the command line) rather than editing code. The config file becomes a complete, human-readable description of what the run did.

### Hands-On: Configs with Command-Line Overrides

For simpler projects, reading a YAML file with PyYAML is enough. This helper also lets you override single values from the command line, and refuses unknown keys, so a typo such as `learnin_rate` fails immediately instead of being silently ignored:

```python
# src/my_project/config_utils.py
import yaml

def load_config(path, overrides=()):
    """Load a YAML config and apply overrides like 'training.learning_rate=0.01'."""
    with open(path) as f:
        cfg = yaml.safe_load(f)
    for item in overrides:
        key, value = item.split("=", 1)
        node = cfg
        *parents, leaf = key.split(".")
        for part in parents:
            node = node[part]
        if leaf not in node:
            raise KeyError(f"Unknown config key: {key}")   # catch typos early
        node[leaf] = yaml.safe_load(value)                  # "0.01" -> 0.01, "true" -> True
    return cfg
```

```python
# scripts/train.py (excerpt)
import argparse
from my_project.config_utils import load_config

parser = argparse.ArgumentParser()
parser.add_argument("--config", default="configs/baseline.yaml")
parser.add_argument("overrides", nargs="*", help="e.g. training.learning_rate=0.01 seed=1")
args = parser.parse_args()
cfg = load_config(args.config, args.overrides)
```

```bash
python scripts/train.py training.learning_rate=0.01 seed=1
python scripts/train.py training.learnin_rate=0.01
# KeyError: 'Unknown config key: training.learnin_rate'
```

Libraries such as **Hydra** (Python) take this further by combining configs, launching sweeps, and automatically saving the resolved configuration for each run:

```python
# scripts/train.py with Hydra
import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(config_path="../configs", config_name="baseline", version_base=None)
def main(cfg: DictConfig):
    print(OmegaConf.to_yaml(cfg))    # Hydra also saves this in the run's output folder
    # ... train using cfg.training.learning_rate, cfg.seed, etc.

if __name__ == "__main__":
    main()
```

```bash
python scripts/train.py training.learning_rate=0.01
python scripts/train.py --multirun seed=0,1,2,3,4    # five runs, one per seed
```

Each Hydra run gets its own output folder containing a `.hydra/config.yaml` file with the exact settings used.

## A Minimal Tracking Setup

You do not need a special tool to track experiments well. A disciplined folder structure does most of the work:

```python
# scripts/train.py (excerpt)
import json, shutil, subprocess, time, uuid
from pathlib import Path
import yaml

config_path = "configs/baseline.yaml"
cfg = yaml.safe_load(open(config_path))

run_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
run_dir = Path("runs") / run_id
run_dir.mkdir(parents=True)

# Record provenance before training starts
shutil.copy(config_path, run_dir / "config.yaml")
commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
dirty = subprocess.call(["git", "diff", "--quiet"]) != 0
(run_dir / "git.json").write_text(json.dumps({"commit": commit, "uncommitted_changes": dirty}))
subprocess.run(["python", "scripts/environment_report.py"],
               stdout=open(run_dir / "environment.json", "w"))

# ... train the model, then save metrics and weights into run_dir ...
(run_dir / "metrics.json").write_text(json.dumps({"test_accuracy": 0.912}))
```

Each run gets its own folder containing the config, the Git commit (with a warning flag if there were uncommitted changes), the environment report from Chapter 5, the metrics, and the model weights. This takes about twenty lines of code and answers the provenance question completely.

Once you have a handful of runs, a short script turns the `runs/` folder into a table you can sort, filter, and summarize:

```python
# scripts/collect_runs.py
import json
from pathlib import Path
import pandas as pd
import yaml

def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flatten(v, f"{prefix}{k}."))
        else:
            out[f"{prefix}{k}"] = v
    return out

rows = []
for run in sorted(Path("runs").iterdir()):
    row = {"run_id": run.name}
    row.update(flatten(yaml.safe_load(open(run / "config.yaml"))))
    row.update(json.load(open(run / "git.json")))
    row.update(json.load(open(run / "metrics.json")))
    rows.append(row)

runs = pd.DataFrame(rows)
cols = ["run_id", "seed", "training.learning_rate", "commit", "uncommitted_changes", "test_accuracy"]
print(runs[cols].to_string(index=False))
print()
print(runs.groupby("training.learning_rate")["test_accuracy"].agg(["mean", "std", "count"]))
```

Output:

```text
            run_id  seed  training.learning_rate  commit  uncommitted_changes  test_accuracy
20260910-1200-abc0     0                   0.001 a1b2c3d                False         0.9084
20260911-1200-abc1     1                   0.001 a1b2c3d                False         0.9076
20260912-1200-abc2     0                   0.010 a1b2c3d                False         0.8842
20260913-1200-abc3     1                   0.010 a1b2c3d                 True         0.8826

                          mean       std  count
training.learning_rate                         
0.001                   0.9080  0.000566      2
0.010                   0.8834  0.001131      2
```

The last run in the table was made with uncommitted changes, so its commit ID does not fully describe its code. That is exactly the kind of run you would want to rerun before reporting.

The `uncommitted_changes` flag deserves attention. If it is `true`, the recorded commit does not fully describe the code that ran. Make it a habit to commit before any run whose results you might report.

## Tracking Tools

As projects grow to dozens or hundreds of runs, a dedicated tracking tool becomes worthwhile. These tools log parameters, metrics, and files automatically and provide a dashboard for comparing runs.

**MLflow** is open source and can run entirely on your own machine or a university server. It stores runs in a local database, has a web interface for browsing and comparing them, and includes a model registry for managing versions of trained models. Because it is self-hosted, your data and results stay under your control.

Recent versions of MLflow expect a database backend rather than a plain folder; a local SQLite file works well and needs no server. Here is a complete example you can run as-is:

```python
import mlflow

mlflow.set_tracking_uri("sqlite:///mlflow.db")   # a local file; no server needed
mlflow.set_experiment("land-cover-classifier")

for lr in [0.001, 0.01]:
    for seed in [0, 1]:
        with mlflow.start_run(run_name=f"lr{lr}-seed{seed}"):
            mlflow.log_params({"learning_rate": lr, "seed": seed, "git_commit": "a1b2c3d"})
            for epoch in range(3):
                mlflow.log_metric("val_accuracy", 0.80 + 0.03 * epoch - 2 * lr, step=epoch)
            mlflow.log_metric("test_accuracy", 0.86 - 2 * lr + 0.001 * seed)
```

Then query the runs as a pandas table:

```python
import mlflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
runs = mlflow.search_runs(experiment_names=["land-cover-classifier"],
                          order_by=["metrics.test_accuracy DESC"])
print(runs[["tags.mlflow.runName", "params.learning_rate", "params.git_commit",
            "metrics.test_accuracy"]].to_string(index=False))
```

```text
tags.mlflow.runName params.learning_rate params.git_commit  metrics.test_accuracy
      lr0.001-seed1                0.001           a1b2c3d                  0.859
      lr0.001-seed0                0.001           a1b2c3d                  0.858
       lr0.01-seed1                 0.01           a1b2c3d                  0.841
       lr0.01-seed0                 0.01           a1b2c3d                  0.840
```

To browse runs and plot training curves in a web interface, run `mlflow ui --backend-store-uri sqlite:///mlflow.db` and open the address it prints. In a real training script, the logging calls go inside your training loop:

```python
import mlflow

mlflow.set_experiment("land-cover-classifier")
with mlflow.start_run():
    mlflow.log_params(cfg["training"])
    mlflow.log_param("git_commit", commit)
    # ... training loop ...
    mlflow.log_metric("val_accuracy", val_acc, step=epoch)
    mlflow.log_artifact(str(run_dir / "environment.json"))
```

**Weights & Biases** (W&B) is a hosted service with a polished interface and strong collaboration features. It offers free plans for academic use. Because data are sent to an external service, check that this is compatible with your data agreements and U-M data policies before logging anything derived from sensitive data. Logging only metrics and hyperparameters, not data samples, is usually safe.

Other options include TensorBoard (good for visualizing training curves, limited as a tracking system), Aim, and DVC's experiment features. Choose based on whether you need self-hosting, how many collaborators you have, and what your lab already uses.

Whatever tool you choose, make sure that the Git commit, config, seed, and environment are logged with every run. Tracking tools make this easy, but they do not do it by default.

## Data Versioning

Code and configuration are only half of provenance. If your training data change (because you fixed a labeling error, added new samples, or changed a cleaning step), the same code will produce a different model. You need to know which version of the data each run used.

Three approaches, from lightest to heaviest:

**Checksums.** Compute a hash of your data files and log it with every run. If the hash changes, the data changed. This is cheap and catches accidental changes.

```python
import hashlib
def file_sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()
```

For a folder of many files, record one checksum per file plus a single combined checksum for the whole folder:

```python
# scripts/data_manifest.py
import hashlib, json, sys
from pathlib import Path

def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()

def manifest(folder):
    """Checksum every file under `folder`, plus one combined hash for the whole set."""
    files = {str(p.relative_to(folder)): sha256(p)
             for p in sorted(Path(folder).rglob("*")) if p.is_file()}
    combined = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    return {"folder": str(folder), "n_files": len(files), "combined_sha256": combined, "files": files}

if __name__ == "__main__":
    print(json.dumps(manifest(sys.argv[1]), indent=2))
```

```bash
python scripts/data_manifest.py data/processed > runs/<run_id>/data_manifest.json
```

The `combined_sha256` value is a convenient single fingerprint to log as a run parameter. If two runs have the same combined hash, they used identical data. If the hashes differ, the per-file list shows which files changed.

**DVC** (introduced in Chapter 4) versions large data files alongside your Git history. Each Git commit points to an exact version of the data, so checking out an old commit and running `dvc checkout` restores the matching data.

**Versioned releases in a repository.** For datasets you share, publish explicit versions on Hugging Face (with Git revisions) or Zenodo and Deep Blue Data (with version DOIs). Your config then refers to a specific version, such as `v2.1` or a revision hash, and anyone can download exactly that version.

## From Run to Figure

The final link in the chain is from the run to the paper. A simple approach is a **results manifest**: a small file that lists every figure and table in the paper and the run ID or script that produced it.

```yaml
# results/manifest.yaml
figure_2: {script: scripts/plot_learning_curves.py, runs: [20260812-1430-a1b2c3, 20260812-1502-d4e5f6]}
table_2:  {script: scripts/make_results_table.py, runs: [20260815-0910-778899]}
figure_s3: {script: scripts/plot_confusion.py, runs: [20260815-0910-778899]}
```

Better still, have your figure-generating scripts read the run IDs from this manifest, so that the manifest is not just documentation but the actual input:

```python
# scripts/make_results_table.py
import json
from pathlib import Path
import pandas as pd
import yaml

manifest = yaml.safe_load(open("results/manifest.yaml"))
rows = []
for run_id in manifest["table_2"]["runs"]:
    run = Path("runs") / run_id
    git = json.load(open(run / "git.json"))
    if git["uncommitted_changes"]:
        raise RuntimeError(f"{run_id} had uncommitted changes; rerun before reporting")
    rows.append({"run": run_id, "commit": git["commit"],
                 **json.load(open(run / "metrics.json"))})

pd.DataFrame(rows).to_csv("results/tables/table_2.csv", index=False)
```

The script refuses to build a paper table from a run whose code cannot be identified, which turns a good habit into an enforced one. When a reviewer asks about Table 2, you open the manifest, find the run, and have its full provenance in seconds.

## Try This

Add the minimal tracking setup above to one of your training scripts. Run it three times with different learning rates. Then, without looking at your code, use only the contents of the `runs/` folder to answer: which run had the best validation accuracy, which commit and config produced it, and what GPU was it trained on?

## Further Reading

The MLflow and Weights & Biases documentation each include quickstart guides. The REFORMS checklist {footcite}`kapoor2024` lists the provenance information that ML-based science papers should report, and is a useful target for what your tracking should capture.

## Related Chapters

- [Chapter 4: Project Structure and Version Control](ch04_project_structure.md)
- [Chapter 7: Randomness, Determinism, and Hardware](ch07_determinism.md)
- [Chapter 9: Pipelines, Automation, and Continuous Integration](ch09_workflows.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
