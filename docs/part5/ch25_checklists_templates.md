# Chapter 25: Checklists and Templates

:::{admonition} What You Will Learn
:class: tip

- Copy-ready checklists and templates for the practices described in this handbook
:::

This chapter collects checklists and templates from across the handbook in one place. Copy them into your own projects and adapt them as needed. Each item links back to the chapter that explains it.

## Hands-On Scripts in This Handbook

Many chapters include short scripts you can copy into your own projects. This table lists them in one place. Unless noted, each runs with standard Python packages and was tested while writing this handbook; outputs shown in the chapters come from those test runs.

| Script or snippet | What it does | Chapter |
|---|---|---|
| `repro_audit.py` | Checks a project folder for README, license, lockfile, tests, CI, hard-coded paths, and notebook outputs | 1 |
| Model Zoo link check | Confirms submission links work for logged-out users | 2 |
| `fair_check.py` | Reads DataCite metadata for a DOI and reports FAIR-relevant fields | 3 |
| `paths.py`, `.gitignore`, pre-commit config | Portable paths and guardrails against large files, secrets, and notebook outputs | 4 |
| `compare_environments.py` | Compares two environment reports to explain different results | 5 |
| Dockerfile, `predict.py`, Slurm script | Containerized model, run with Docker or with Apptainer on Great Lakes | 6 |
| Seed variation and multi-seed comparison | Shows seed and split variability; reports mean, SD, CI, and a paired test | 7 |
| `logged_call()` | Logs every LLM call, with full prompt and parameters, to JSON Lines | 7 |
| `config_utils.py`, `collect_runs.py`, MLflow example | Config overrides, a table of all runs, and MLflow tracking with SQLite | 8 |
| `data_manifest.py` | One checksum per file plus a combined fingerprint for a data folder | 8 |
| Snakefile, pandera tests | Multi-seed pipeline and data validation in pytest | 9 |
| README doctest, `make_model_card.py`, `cffconvert` | Tested quickstart, generated model card, validated citation file | 10 |
| `check_reproduction.py` | Compares reproduced metrics with the paper, with stated tolerances | 11 |
| `availability_statement.py` | Drafts availability statements and progress-report status from a sharing inventory | 12 |
| `size_up.py` | Checks a release folder against common platform size limits | 13 |
| Hub mixin, revision pinning, downloads | Share and load exact versions of models on Hugging Face | 14 |
| `make_kaggle_metadata.py` | Builds Kaggle metadata from a data dictionary | 15 |
| `deposit_zenodo.py` | Creates a Zenodo draft deposit through the API (test on the Sandbox first) | 16 |
| `draft_data_dictionary.py`, label agreement, Croissant validation | Documents datasets and AI-assigned labels | 17 |
| `check_provenance.py`, `pip-licenses` | Flags license constraints in sources and dependencies | 18 |
| *k*-anonymity check, membership signal, synthetic data | Measures identifiability and leakage risk | 19 |
| `checksums.py`, `check_inventory.py`, tombstone README | Verifies downloads and monitors shared artifacts | 20 |
| Memory estimator, ONNX export, QLoRA setup | Runs and adapts models on modest hardware | 21 |
| Accessible Gradio Blocks demo, client health check | A demo with text summaries, labeled examples, and a testable API | 22 |
| Contrast calculator, accessible figure, color-vision simulation, `axe_check.py` | Checks figures and web pages against WCAG | 23 |
| Setup cell, `nbmake`, papermill, plain-language report | Tutorials that run anywhere and stay working | 24 |

## Model Zoo Submission Checklist

Use this checklist when preparing a Model Zoo entry. The tiers are cumulative: an entry at the "Reproducible" tier meets all "Listed" and "Documented" items too. The tiers are proposals under discussion with the Model Zoo team (Chapter 2).

### Listed

- [ ] Name and a one- or two-sentence plain-language description
- [ ] Category (software, tutorial, dataset, web application, or model) and domain
- [ ] Link to a stable location (not a personal cloud drive) that works when logged out (Chapter 20)
- [ ] Creator name and MIDAS affiliation, with contact information
- [ ] License stated (Chapter 18)

### Documented

- [ ] README with a working quickstart and expected output (Chapter 10)
- [ ] Model card (for models) or datasheet/dataset card (for datasets) (Chapters 10, 17)
- [ ] Citation: paper and/or `CITATION.cff` (Chapter 10)
- [ ] Limitations and out-of-scope uses stated

### Reproducible

- [ ] Lockfile or container image, documented in the README (Chapters 5, 6)
- [ ] Archived version with a DOI (Chapter 16)
- [ ] Pinned version, tag, or revision referenced in the entry (Chapters 4, 14)
- [ ] Checksums for downloadable files (Chapter 20)
- [ ] A reviewer has run the quickstart successfully on a clean machine (Chapter 11)

### Accessible

- [ ] Runs on a CPU or free cloud notebook, or has a hosted demo (Chapters 21, 22)
- [ ] Minimum hardware requirements stated (Chapter 21)
- [ ] Documentation images have alt text; figures use colorblind-safe palettes (Chapter 23)
- [ ] Demo and documentation pass an automated accessibility check (Chapter 23)
- [ ] Tutorial videos, if any, have reviewed captions (Chapter 23)

## Reproducibility Pre-Share Checklist

Use before submitting a paper or releasing a model (Chapter 11).

**Code**
- [ ] All code needed to produce reported results is committed and pushed
- [ ] A release is tagged and archived with a DOI
- [ ] No hard-coded local paths; no secrets in the repository
- [ ] Random seeds set and recorded (Chapter 7)

**Environment**
- [ ] Lockfile or container committed and documented
- [ ] Hardware, OS, and CUDA versions recorded (Chapter 5)

**Data and models**
- [ ] Data and weights deposited with DOIs, or access process documented
- [ ] Checksums provided

**Provenance**
- [ ] Each reported result is linked to a run, config, and commit (Chapter 8)
- [ ] Results report variability across seeds (Chapter 7)

**Verification**
- [ ] Clean-room rerun succeeded without improvisation (Chapter 11)
- [ ] CI smoke test passes (Chapter 9)

## Model Card Template

Adapted from the Hugging Face model card template and Mitchell et al. (Chapter 10). Save as `README.md` in a Hugging Face model repository.

````markdown
---
license: apache-2.0
library_name: pytorch
tags: [image-classification]
datasets: [your-org/your-dataset]
metrics: [accuracy, f1]
---

# Model Name

One-sentence plain-language description of what the model does.

## Model Details
- **Developed by:** Names (ORCID), University of Michigan
- **Version:** v1.0 (revision/tag: `v1.0`)
- **Model type / architecture:**
- **Base model (if fine-tuned):** name and revision
- **License:**
- **Paper:** citation and DOI
- **Archived copy:** DOI
- **Contact:**

## Intended Use
- **Primary uses:**
- **Intended users:**
- **Out-of-scope uses:** uses the model was not designed or validated for

## How to Get Started
```python
# minimal code to load the model and run one prediction
```
Expected output:

## Training Data
Description, source, size, time period, and link to datasheet.

## Evaluation
- **Test data:**
- **Metrics:**
- **Results:** mean ± SD across N seeds

### Performance by Subgroup
Results broken down by relevant groups (region, source, demographic group, etc.).

## Limitations and Ethical Considerations
Known failure modes, biases, risks, and conditions where the model should not be trusted.

## Hardware Requirements
- Inference memory at FP16 / INT8 / 4-bit:
- Runs on CPU: yes/no; typical time per example:
- Training hardware and time:

## Citation
BibTeX
````

## Dataset README Template

For Deep Blue Data, Zenodo, and other repositories (Chapter 17).

```markdown
# Dataset Title

## Summary
One or two sentences describing the dataset.

## Citation
Dataset: Authors (Year). Title (Version). Repository. DOI
Associated paper: citation

## Creators and Contact
Names, ORCIDs, affiliations. Contact for questions and problem reports.

## License
e.g., CC BY 4.0

## Files
| File | Description | Format | Size | SHA-256 |
|---|---|---|---|---|

## Data Dictionary
| Variable | Description | Type | Units / values | Missing values |
|---|---|---|---|---|

## Collection and Processing
How, when, and where data were collected. Processing steps and link to code (with DOI).

## Known Issues and Limitations

## Intended and Out-of-Scope Uses

## Ethics and Consent
IRB approval, consent terms, de-identification applied.

## Versions
- v1.0 (date): initial release
```

## Datasheet Questions

The full set of datasheet questions is in Gebru et al. (Chapter 17). A condensed version:

- **Motivation:** Why was it created? By whom? Who funded it?
- **Composition:** What does each instance represent? How many? Sample of what population? Labels? Missing data? Sensitive information? Subpopulations identified?
- **Collection:** How and when was it collected? By whom? Consent? Ethical review?
- **Preprocessing and labeling:** What was done? Is raw data kept? Is code available? If AI-labeled, which model, and how validated?
- **Uses:** Past uses? Other possible uses? Uses to avoid?
- **Distribution:** Where, when, under what license?
- **Maintenance:** Who maintains it? How will updates and errata be communicated?

## CITATION.cff Template

```yaml
cff-version: 1.2.0
message: "If you use this software or model, please cite it as below."
title: "Title"
version: 1.0.0
doi: 10.5281/zenodo.0000000
date-released: 2026-01-01
authors:
  - family-names: Last
    given-names: First
    orcid: https://orcid.org/0000-0000-0000-0000
    affiliation: University of Michigan
license: MIT
repository-code: https://github.com/your-org/your-repo
```

## Data Management and Sharing Plan Snippets

Adapt this language to your project and your funder's current template (Chapter 12). Do not promise what you cannot deliver.

**Data types**
> This project will generate (1) [raw/processed data description, format, estimated size]; (2) trained machine learning model weights and associated configuration files; (3) source code for data processing, model training, and evaluation; and (4) documentation including a datasheet, model card, and data dictionary.

**Related tools, software, and code**
> All code will be released under an open-source license (MIT or Apache 2.0) on GitHub and archived with a DOI on Zenodo at each release. The computational environment will be captured in a lockfile and a container image, deposited alongside the code.

**Standards**
> Datasets will be documented using datasheets and machine-readable metadata (DataCite; Croissant where applicable). Models will be documented with model cards. Tabular data will be shared in open formats (CSV or Parquet) with a data dictionary.

**Preservation, access, and timelines**
> Data and model weights will be deposited in Deep Blue Data, the University of Michigan's curated research data repository, which assigns DOIs and provides long-term preservation, no later than the time of publication or the end of the award period. To support reuse, models and ML-ready datasets will also be made available on the Hugging Face Hub, and resources will be listed in the MIDAS Model Zoo.

**Access, distribution, and reuse considerations**
> [If applicable] Participant-level data cannot be shared publicly under the terms of informed consent. De-identified data will be deposited with ICPSR as restricted-use files available to qualified researchers under a data use agreement. Synthetic data with the same structure, and all code, will be shared openly.

**Oversight**
> The PI will oversee compliance with this plan, with support from [role]. Sharing progress will be reported annually.

## Accessibility Checklist

For figures, notebooks, documentation, and demos (Chapter 23).

**Figures**
- [ ] Meaningful alt text conveying the key message; long description or data table for complex figures
- [ ] Colorblind-safe palette; information not conveyed by color alone
- [ ] Sufficient contrast (4.5:1 for text; 3:1 for graphical elements)
- [ ] Legible text at the size the figure will be displayed

**Notebooks and documentation**
- [ ] Headings in order, used for structure
- [ ] Descriptive link text
- [ ] Alt text on all informative images
- [ ] Key results described in text, not only shown in plots
- [ ] Math rendered as MathML/MathJax, not images

**Demos and web pages**
- [ ] All controls labeled
- [ ] Fully usable with keyboard only; visible focus
- [ ] Passes axe or WAVE with no serious errors
- [ ] Works at 200% zoom

**Video**
- [ ] Reviewed captions
- [ ] Transcript available
- [ ] Actions described verbally

## Related Chapters

- [Chapter 2: The MIDAS Model Zoo](../part1/ch02_model_zoo.md)
- [Chapter 11: Testing Reproducibility Before You Share](../part2/ch11_testing_reproducibility.md)
- [Chapter 23: Disability Accessibility for Research Outputs](../part4/ch23_disability_access.md)

---

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
