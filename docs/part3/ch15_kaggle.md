# Chapter 15: Sharing on Kaggle

:::{admonition} What You Will Learn
:class: tip

- What Kaggle Datasets, Models, and Notebooks are good for in research
- How to publish a dataset with a high usability rating
- How pairing a dataset or model with a notebook lets people use it immediately
- How to host a community competition or benchmark
- When Kaggle is and is not the right fit
:::

## Why Kaggle

Kaggle, owned by Google, is best known for machine learning competitions, but it is also one of the largest platforms for sharing datasets and notebooks. Its audience is broad: students learning data science, practitioners looking for data to practice on, instructors building course materials, and researchers exploring new domains. A well-documented research dataset on Kaggle can reach many more people than the same dataset in an institutional repository alone.

Kaggle's distinctive strength is that datasets, models, and code live side by side. Anyone can open a free, browser-based notebook attached to your dataset, with the data already loaded and a GPU available, and start analyzing it within seconds. Others can publish their own notebooks using your data, which creates a visible record of how your work is being used and often surfaces analyses you would not have thought of.

This makes Kaggle particularly good for:

- Datasets you want to be used for teaching or practice.
- Benchmarks you want the community to compete on.
- Reaching a data science audience outside your discipline.
- Providing a zero-setup way to explore your data.

## Publishing a Dataset

You can create a dataset through the web interface (upload files, fill in the fields) or with the Kaggle command-line tool, which is better for reproducibility because the metadata lives in a file you can version control.

```bash
pip install kaggle
# Put your API token (from kaggle.com > Settings > API) in ~/.kaggle/kaggle.json

kaggle datasets init -p release/        # creates release/dataset-metadata.json
# edit dataset-metadata.json: title, id, licenses, description, column descriptions
kaggle datasets create -p release/      # first upload

# later, publish a new version
kaggle datasets version -p release/ -m "v1.1: corrected 42 mislabeled rows"
```

Kaggle keeps every version of a dataset, and users can refer to a specific version number. Write a meaningful message for each version so users know what changed.

### Hands-On: Generate Kaggle Metadata from Your Data Dictionary

The `dataset-metadata.json` file is where column descriptions go, and it is tedious to fill in by hand. If you already have a data dictionary (Chapter 17), you can generate the metadata from it, which also guarantees that the two never disagree. This script refuses to continue if any column is undocumented:

```python
# scripts/make_kaggle_metadata.py
import json
import pandas as pd

df = pd.read_csv("release/labels.csv")
docs = pd.read_csv("data_dictionary.csv").set_index("variable")["description"]

kaggle_types = {"int64": "integer", "float64": "number", "bool": "boolean"}
fields = [{"name": col,
           "description": docs.get(col, ""),
           "type": kaggle_types.get(str(df[col].dtype), "string")}
          for col in df.columns]

missing = [f["name"] for f in fields if not f["description"]]
if missing:
    raise SystemExit(f"Add descriptions to the data dictionary for: {missing}")

metadata = {
    "title": "Roof Condition Images (Midwest)",
    "subtitle": "Street-level house photos labeled by roof condition",
    "id": "your-username/roof-condition-images",
    "licenses": [{"name": "CC0-1.0"}],
    "keywords": ["computer vision", "housing", "urban planning"],
    "description": open("README.md").read(),     # the datasheet, in Markdown
    "resources": [{"path": "labels.csv",
                   "description": "One row per image with its label and label source.",
                   "schema": {"fields": fields}}],
}
json.dump(metadata, open("release/dataset-metadata.json", "w"), indent=2)
```

The resulting file looks like this (shortened):

```json
{
  "title": "Roof Condition Images (Midwest)",
  "id": "your-username/roof-condition-images",
  "licenses": [{"name": "CC0-1.0"}],
  "resources": [{
    "path": "labels.csv",
    "description": "One row per image with its label and label source.",
    "schema": {"fields": [
      {"name": "image_id", "description": "Unique image identifier; matches the file name in images/", "type": "string"},
      {"name": "city", "description": "City where the photo was taken", "type": "string"},
      {"name": "label", "description": "Roof condition: intact, minor_damage, major_damage, or missing", "type": "string"}
    ]}
  }]
}
```

If a column is missing from the data dictionary, the script stops with a message such as `Add descriptions to the data dictionary for: ['image_id']`. Kaggle accepts a fixed list of license names in this file; check the Kaggle API documentation for the current list and use the one matching the license you chose (Chapter 18).

Kaggle supports datasets of up to about 200 GB each, with limits on private storage per account. Check Kaggle's current documentation, as these limits have increased over time.

### The Usability Rating

Each Kaggle dataset has a **usability rating** from 0 to 10, displayed prominently on its page and used in search ranking. It is calculated from how complete the dataset's documentation is. The rating broadly rewards:

**Completeness.** A subtitle, tags, a cover image, and a substantive description.

**Credibility.** Information about provenance (where the data came from and how they were collected), a public notebook that demonstrates the data, and an expected update frequency.

**Compatibility.** A license, open file formats, file descriptions, and column descriptions.

Aiming for a rating of 10 is a reasonable goal, and in practice it amounts to a good datasheet (Chapter 17) spread across Kaggle's fields. Column descriptions are the most commonly skipped item, and the most useful to users.

### DOIs and Citation

Kaggle can assign a DOI to a public dataset, which makes it easier to cite. Include a citation in the description that credits the original paper and, if the data are archived elsewhere, the archival DOI (Chapter 13). Because Kaggle is a community hub rather than an archive, the archival copy should remain your primary citation for the version used in a paper.

## Kaggle Models and Notebooks

**Kaggle Models** is a repository of pretrained models, organized by framework (for example PyTorch, TensorFlow, JAX, or Keras) and variations (such as different sizes). Models can be loaded directly in Kaggle notebooks or anywhere using the `kagglehub` library:

```python
import kagglehub
path = kagglehub.model_download("your-lab/roof-condition/pyTorch/v1")
data_path = kagglehub.dataset_download("your-lab/roof-images")
```

Pin the version in downloads, just as you would pin a Hugging Face revision. Both the Python library and the command-line tool accept a version number:

```python
import kagglehub
path = kagglehub.dataset_download("your-lab/roof-images/versions/2")   # exactly version 2
```

```bash
kaggle datasets download your-lab/roof-images --unzip -p data/raw/
kaggle datasets files your-lab/roof-images     # list files before downloading
```

Hugging Face is the larger hub for models, so many researchers publish models there first. Publishing on Kaggle as well makes sense if your target audience is already on Kaggle, or if you want to pair the model with example notebooks and a dataset in the same place.

**Notebooks** are where Kaggle's real value for sharing lies. After publishing a dataset or model, create at least one public "starter" notebook that:

- Loads the data or model.
- Shows basic exploration or a prediction.
- Reproduces one key result from your paper, if it is feasible within Kaggle's compute limits.
- Explains, in text cells, what the data are and how they should and should not be used.

Kaggle notebooks run in a free cloud environment with CPUs and, with a verified account, a weekly GPU quota. This makes them a practical way to offer low-resource access to your work (Chapter 21). Pin package versions at the top of the notebook, since Kaggle's default environment is updated periodically.

## Competitions and Benchmarks for Research

Kaggle hosts two kinds of competitions. **Featured competitions** are large, sponsored, and often carry prize money. **Community competitions** can be set up by anyone at no cost, and are widely used for classes, workshops, and research benchmarks.

A community competition can be a powerful way to make a research problem accessible. You provide training data and a hidden test set, choose an evaluation metric, and let participants submit predictions. The public leaderboard shows how different approaches compare. For a research group, this can surface strong methods, engage students, and establish a benchmark around your dataset.

If you run one, think carefully about leakage: participants are very good at finding and exploiting any shortcut in your data split. Also consider what happens to the test set after the competition ends, and document the benchmark with the same care as any other dataset.

## Caveats

**Kaggle is not an archive.** Like Hugging Face, Kaggle makes no formal long-term preservation commitment. Keep an archival copy with a DOI in Deep Blue Data, Zenodo, or a discipline repository.

**Terms of service apply.** Uploading to Kaggle means agreeing to Google's and Kaggle's terms. Make sure you have the rights to redistribute the data and that nothing in it is sensitive.

**Licenses must be chosen deliberately.** Kaggle offers a menu of licenses. Choose one that matches the rest of your release (Chapter 18); if the data came from somewhere else, you cannot grant a more permissive license than you received.

**Audience expectations differ.** Kaggle users often use data in ways researchers did not anticipate, including in commercial projects if the license permits. Be explicit about intended and out-of-scope uses in the description.

## Try This

Pick a dataset you have already shared elsewhere, or a cleaned subset of one. Publish it on Kaggle using the command-line tool, and fill in every field needed to reach a usability rating of 10. Then write a starter notebook that loads the data and reproduces one figure from your paper. Link the Kaggle page from your archival repository record and the Model Zoo entry.

## Further Reading

Kaggle's documentation covers datasets, models, notebooks, and the API. The `kagglehub` library documentation explains downloading datasets and models outside Kaggle.

## Related Chapters

- [Chapter 13: Choosing Where to Share](ch13_where_to_share.md)
- [Chapter 16: Institutional and Archival Repositories](ch16_archival_repositories.md)
- [Chapter 21: AI on Modest Hardware](../part4/ch21_low_resource.md)

---

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
