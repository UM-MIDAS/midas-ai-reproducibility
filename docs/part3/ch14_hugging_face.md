# Chapter 14: Sharing on Hugging Face

:::{admonition} What You Will Learn
:class: tip

- What the Hugging Face Hub offers for sharing models, datasets, and demos
- How to publish a model with a model card and safe weight format
- How to publish a dataset that loads in one line and works with the dataset viewer
- How to version, tag, and cite specific revisions, including with a DOI
- When to use private and gated repositories
- The Hub's limits, and why you should still archive elsewhere
:::

## Why Hugging Face

The Hugging Face Hub has become the default place to share machine learning models and many ML datasets. Its main advantage is usability. A model on the Hub can be loaded with one line of code by anyone using the `transformers`, `diffusers`, `sentence-transformers`, `timm`, or many other libraries. A dataset on the Hub can be loaded with `datasets.load_dataset()` and browsed in a web viewer without downloading anything. Researchers searching for a model for their task look there first.

Two existing Model Zoo entries, the color- and shape-prediction image classifiers, are hosted on Hugging Face and are good examples of what a simple model repository looks like.

## What the Hub Offers

Every item on the Hub lives in a **repository**, which is a Git repository with large-file support built in. There are three types.

**Model repositories** hold weights, configuration files, and a model card (`README.md`).

**Dataset repositories** hold data files and a dataset card. The Hub automatically generates a dataset viewer, statistics, and machine-readable Croissant metadata for supported formats.

**Spaces** host interactive demos built with Gradio, Streamlit, Docker, or static HTML (Chapter 22).

Repositories belong to a user or an **organization**. For research groups, an organization account is strongly recommended: it keeps artifacts together, allows multiple maintainers, and means the repository does not disappear when one student graduates and abandons their personal account. MIDAS and many U-M labs can use organization accounts for this reason.

Each repository page shows download counts, linked papers, the datasets a model was trained on, and the models trained on a dataset. These links help others discover your work and help you see how it is being used.

## Publishing a Model

### Save Weights Safely

Save weights in the **safetensors** format rather than PyTorch's default pickle-based `.bin` or `.pt` files. Pickle files can execute arbitrary code when loaded, which is a security risk for anyone downloading your model. Safetensors files contain only tensors, load faster, and are the Hub's recommended format. Most Hugging Face libraries save in safetensors by default. For a plain PyTorch model:

```python
from safetensors.torch import save_file
save_file(model.state_dict(), "model.safetensors")
```

### Upload

First, create an account and an access token at huggingface.co, then log in from your terminal or notebook:

```python
from huggingface_hub import login
login()   # paste a token with write access
```

If your model is built with `transformers`, pushing is one line:

```python
model.push_to_hub("your-lab/roof-condition-classifier")
tokenizer.push_to_hub("your-lab/roof-condition-classifier")
```

For other models, upload a folder containing the weights, config, model card, and any code needed to load the model:

```python
from huggingface_hub import HfApi
api = HfApi()
api.create_repo("your-lab/roof-condition-classifier", repo_type="model", exist_ok=True)
api.upload_folder(
    folder_path="release/",
    repo_id="your-lab/roof-condition-classifier",
    commit_message="Release v1.0: model as reported in paper",
)
```

The same upload works from the command line with the `hf` tool that comes with `huggingface_hub`:

```bash
hf auth login
hf upload your-lab/roof-condition-classifier ./release . --commit-message "Release v1.0"
```

### Hands-On: Share a Custom PyTorch Model with the Hub Mixin

The `huggingface_hub` library provides a `PyTorchModelHubMixin` class that adds `save_pretrained`, `push_to_hub`, and `from_pretrained` methods to any PyTorch model class, which makes custom models as easy to share as `transformers` models. You add it to your class definition, and it takes care of saving the weights as safetensors and the constructor arguments as a `config.json`, so the model can be rebuilt exactly:

```python
import torch.nn as nn
from huggingface_hub import PyTorchModelHubMixin

class RoofClassifier(
    nn.Module,
    PyTorchModelHubMixin,
    repo_url="https://github.com/your-lab/roof-condition",   # these fill the model card
    license="apache-2.0",
    tags=["image-classification", "urban-planning"],
):
    def __init__(self, num_classes: int = 4, hidden: int = 256):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2), nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1), nn.Flatten())
        self.head = nn.Sequential(nn.Linear(64, hidden), nn.ReLU(), nn.Linear(hidden, num_classes))

    def forward(self, x):
        return self.head(self.features(x))

model = RoofClassifier(num_classes=4)
# ... train the model ...
model.save_pretrained("release/")            # model.safetensors + config.json + README.md
model.push_to_hub("your-lab/roof-condition-classifier")

# Anyone can now rebuild it, with the same constructor arguments, in one line
reloaded = RoofClassifier.from_pretrained("your-lab/roof-condition-classifier", revision="v1.0")
```

Users still need your class definition, so put it in an installable package or a single `model.py` file in the repository, and show the import in the model card's quickstart.

### Write the Model Card

The repository's `README.md` is the model card. Use the structure from Chapter 10, starting with the YAML metadata block (license, tags, datasets, metrics, library name). The metadata is what makes your model appear in search filters and what links it to your dataset. Include a working code example that loads the model from the Hub and runs a prediction.

## Publishing a Dataset

For tabular and text data, **Parquet** is the recommended format: it is compressed, preserves column types, and loads quickly. CSV and JSON Lines also work. For images and audio, the Hub supports folders of files with a metadata CSV, or Parquet files with embedded media.

With the `datasets` library:

```python
from datasets import load_dataset
ds = load_dataset("csv", data_files={"train": "train.csv", "test": "test.csv"})
ds.push_to_hub("your-lab/roof-images")
```

To publish a specific version of a dataset, push privately first, check it in the viewer, then make it public and tag it:

```python
ds.push_to_hub("your-lab/roof-images", private=True)
# ...review the dataset viewer on the Hub, then make the repository public in its settings...
from huggingface_hub import HfApi
HfApi().create_tag("your-lab/roof-images", tag="v1.0", repo_type="dataset")

# Users load exactly that version
from datasets import load_dataset
ds = load_dataset("your-lab/roof-images", revision="v1.0")
```

Or upload Parquet files directly with `upload_folder`. Organize files by split (`train`, `validation`, `test`) and, for multiple subsets, by **configuration**. You can declare configurations and splits in the YAML header of the dataset card so the viewer and loader understand the structure.

```yaml
---
license: cc-by-4.0
task_categories: [image-classification]
pretty_name: Roof condition images
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/train-*.parquet
      - split: test
        path: data/test-*.parquet
  - config_name: detroit_only
    data_files:
      - split: test
        path: data/detroit/test-*.parquet
---
```

Users then choose a subset by name, for example `load_dataset("your-lab/roof-images", "detroit_only", revision="v1.0")`.

Once uploaded, the Hub generates a **dataset viewer** that lets anyone browse rows, and **Croissant** metadata (Chapter 17) that describes the dataset in a machine-readable format. The NeurIPS Evaluations and Datasets track lists Hugging Face among the platforms that satisfy its Croissant requirement. You should still add responsible AI information, such as limitations, biases, and sensitive content, to the dataset card.

Write a dataset card following the datasheet structure in Chapter 17: motivation, composition, collection process, preprocessing, uses, distribution, and maintenance.

## Versioning and Releases

Because every Hub repository is a Git repository, every change creates a new **revision** with a commit hash. Users can load an exact revision:

```python
from transformers import AutoModel
model = AutoModel.from_pretrained("your-lab/roof-condition-classifier", revision="v1.0")
```

Create a **tag** for each release, especially the version reported in a paper:

```python
api.create_tag("your-lab/roof-condition-classifier", tag="v1.0",
               tag_message="Version reported in Doe et al. 2026")
```

In your paper and code, always refer to a tag or commit hash, never just the repository name. If you later improve the model, users of the paper version can still load exactly what you reported.

### Hands-On: Pin, Inspect, and Download Exact Versions

Tags on the Hub can be moved or deleted by the repository owner, so for the strongest guarantee, record the full commit hash that a tag points to at release time:

```python
from huggingface_hub import HfApi
api = HfApi()

refs = api.list_repo_refs("your-lab/roof-condition-classifier")
for tag in refs.tags:
    print(tag.name, tag.target_commit)        # e.g. v1.0  3f8a1c...

info = api.model_info("your-lab/roof-condition-classifier", revision="v1.0")
print(info.sha)                               # the exact commit hash to cite
print([f.rfilename for f in info.siblings])   # files in that revision
```

To download files for a specific revision, use `hf_hub_download` for one file or `snapshot_download` for a whole repository:

```python
from huggingface_hub import hf_hub_download, snapshot_download

weights = hf_hub_download("your-lab/roof-condition-classifier",
                          filename="model.safetensors", revision="v1.0")

folder = snapshot_download("your-lab/roof-condition-classifier", revision="v1.0",
                           allow_patterns=["*.safetensors", "*.json"])   # skip large extras
```

Or from the command line:

```bash
hf download your-lab/roof-condition-classifier --revision v1.0 --local-dir models/roof-v1.0
```

Downloads are cached, by default in `~/.cache/huggingface`. On Great Lakes, home directories have limited space, so point the cache at scratch or Turbo before downloading large models. If your compute jobs run somewhere without internet access, download first and then tell the libraries not to try the network:

```bash
export HF_HOME=/scratch/your_account/$USER/hf_cache   # cache location
hf download your-lab/roof-condition-classifier --revision v1.0
export HF_HUB_OFFLINE=1                                # later jobs use only the cache
```

### DOIs on Hugging Face

The Hub can issue DOIs for model and dataset repositories through DataCite. In the repository settings, choose "Generate DOI." Each DOI refers to a specific revision, and you can generate a new DOI for each new version. Once a repository has a DOI, it is locked: you cannot delete, rename, or change its visibility without contacting Hugging Face support. This protects the DOI, but it also means you should only generate one when you are ready for the repository to be permanent.

## Private and Gated Repositories

**Private repositories** are visible only to you and your organization. Use them while preparing a release or for internal collaboration. Free accounts have a private storage limit (100 GB at the time of writing).

**Gated repositories** are public, but users must accept conditions and, optionally, provide information (such as name, affiliation, and intended use) before they can download files. You can approve requests automatically or review them manually. Gating is useful when:

- The license has specific terms, such as responsible-use restrictions, that you want users to acknowledge.
- You want to know who is using your model or data, for impact reporting or to notify users of problems.
- The data are low-risk but you want an extra layer of accountability, such as research-only use.

Users of a gated repository authenticate with their own token, after which downloads work as normal. If you review requests manually, you can manage them from Python as well as the web interface:

```python
from huggingface_hub import HfApi
api = HfApi()
for req in api.list_pending_access_requests("your-lab/roof-images", repo_type="dataset"):
    print(req.username, req.fields)           # answers to the questions you asked
    # api.accept_access_request("your-lab/roof-images", req.username, repo_type="dataset")
```

Gating is not a substitute for proper controlled access to sensitive data. It does not verify identities or enforce data use agreements the way ICPSR or dbGaP do (Chapter 19).

## Spaces for Demos

A Space turns your model into a web app that anyone can try in a browser. Linking a Space from your model card greatly increases the number of people who engage with your work. Chapter 22 covers how to build one, and current hosting options and costs.

## Limits and Caveats

**The Hub is not an archive.** Hugging Face is a company, and while it has been a reliable host, it makes no formal long-term preservation commitment comparable to Zenodo or Deep Blue Data. Owners can delete repositories that do not have DOIs, and storage policies can change. Follow the two-home pattern from Chapter 13: archive the paper version in an archival repository and link it from the model card.

**Storage limits apply.** Public storage for free accounts is provided on a best-effort basis for content that is useful to the community, and very large repositories should follow Hugging Face's recommendations on file sizes and counts. Paid plans provide more storage. Check the current storage limits page before uploading very large datasets.

**Licenses matter.** The Hub makes it easy to fine-tune and redistribute models. Check that your base model's license permits redistribution of derivatives, and that your training data's license permits the model to be shared (Chapter 18).

**Sensitive content.** Do not upload data containing personal information, protected health information, or data you do not have the right to redistribute. Remember that model weights trained on sensitive data can leak it (Chapter 19).

## Try This

Create a free Hugging Face account (or ask to join your lab's organization). Take a small model you have trained, save it as safetensors, and upload it to a private repository with a model card and a working code example. Tag the upload as `v0.1`. Then, from a clean Colab session, load it using the tag and run a prediction. When you are satisfied, make it public and add it to the Model Zoo.

## Further Reading

The Hugging Face Hub documentation covers model cards, dataset cards, gated repositories, DOIs, and storage limits in detail. The `huggingface_hub` library documentation explains upload and download options.

## In the Model Zoo

Hugging Face is the most common home for Model Zoo model entries. Link to a tagged revision, include the DOI if you have one, and make sure the model card has a working quickstart.

## Related Chapters

- [Chapter 10: Documenting Models](../part2/ch10_documenting_models.md)
- [Chapter 13: Choosing Where to Share](ch13_where_to_share.md)
- [Chapter 17: Documenting Datasets](ch17_documenting_datasets.md)
- [Chapter 22: Interactive Demos and Web Apps](../part4/ch22_demos.md)

---

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
