# Chapter 10: Documenting Models: READMEs, Model Cards, and Citation

:::{admonition} What You Will Learn
:class: tip

- What a README needs so a stranger can use your model in fifteen minutes
- How to write a model card that explains what a model is for and where it fails
- Which reporting checklists apply to ML-based research
- How to make your model and code citable with `CITATION.cff` and DOIs
- When documentation outgrows a README
:::

## Documentation Is Part of the Artifact

A trained model without documentation is a file of numbers. Nobody can tell what it predicts, what data it was trained on, how well it works, or where it should not be used. Even the person who trained it will forget most of this within a year.

Documentation is often treated as a chore to finish after the real work is done. It is better to think of it as part of the artifact itself, as essential as the weights. This chapter covers three layers: the README, which tells people how to use your model; the model card, which tells them whether they should; and the citation, which lets them give you credit.

## The Fifteen-Minute README

A good test for a README is whether a competent researcher who has never seen your project can install it, run an example, and understand the output within about fifteen minutes. That requires these sections, in roughly this order.

**What it is.** One or two sentences, in plain language, describing what the model does. "Classifies street-level photos of houses into four roof condition categories" is better than "A ResNet-based classifier for urban imagery."

**Quickstart.** The shortest possible path from nothing to a prediction. Installation commands, then a code snippet of five to ten lines that loads the model and runs it on an example input that ships with the repository. Show the expected output.

```python
from my_model import load_model
model = load_model("your-lab/roof-condition", revision="v1.0")
print(model.predict("examples/house_01.jpg"))
# {'label': 'minor_damage', 'score': 0.87}
```

**Requirements.** Python or R version, the lockfile or container to use (Chapters 5 and 6), and hardware needs: does it require a GPU, and how much memory?

**Data.** What the model was trained on, where that data lives, and how to get it. Link to the dataset's own documentation (Chapter 17).

**Reproducing the results.** The exact commands to retrain the model and regenerate the paper's figures and tables, ideally a single pipeline command (Chapter 9).

**Limitations.** A short summary of what the model does not do well. Point to the model card for details.

**Citation and license.** How to cite the work, and under what license it can be used.

**Contact and support.** Who maintains it, and how to report problems (usually GitHub Issues).

Write the quickstart first and test it on a clean machine (Chapter 11). If the quickstart does not work, nothing else in the README matters.

### Hands-On: Make the README Quickstart a Test

READMEs go stale silently: the code changes, and the example in the README no longer runs. Python's built-in `doctest` format lets you turn the quickstart into a test that runs automatically. Write the example as an interactive session, with `>>>` before each line of code and the expected output underneath:

````markdown
## Quickstart

```python
>>> from my_model import load_model
>>> model = load_model("your-lab/sentiment-model", revision="v1.0")
>>> model.predict("The new bus route saved me 20 minutes a day.")
{'label': 'positive', 'score': 0.91}

```
````

Then run it with pytest:

```bash
pytest --doctest-glob="README.md"
```

If the output ever changes, pytest reports exactly what was expected and what it got:

```text
Expected:
    {'label': 'positive', 'score': 0.91}
Got:
    {'label': 'positive', 'score': 0.95}
```

Two details matter. Leave a blank line before the closing code fence, or doctest will treat the fence as part of the expected output. And round any floating point numbers in the output, since tiny numerical differences across machines (Chapter 7) will otherwise fail the test. Add this command to your CI workflow (Chapter 9) and your README can never silently fall out of date.

## Model Cards

A model card is a short document that accompanies a trained model and describes its intended use, performance, and limitations. The concept was introduced in 2019 {footcite}`mitchell2019` and has become a standard, particularly on Hugging Face, where every model repository has a model card as its `README.md`.

A model card answers the questions a potential user should ask before relying on a model. The standard sections are:

**Model details.** Who developed it, when, what version, what architecture, and under what license.

**Intended use.** The primary uses the model was designed for, the intended users, and uses that are out of scope. Be specific. "Research on roof condition assessment in Midwestern U.S. cities" is more useful than "urban analysis." Explicitly listing out-of-scope uses (for example, "not validated for insurance or lending decisions") helps prevent misuse.

**Training data.** What data were used, how they were collected and labeled, and known gaps. Link to the dataset's datasheet.

**Evaluation.** What data the model was tested on, what metrics were used, and the results. Report variability across seeds (Chapter 7).

**Disaggregated performance.** How performance differs across relevant subgroups: geographic regions, demographic groups, image sources, time periods, or whatever dimensions matter for your application. Aggregate accuracy can hide large failures on specific groups. This was one of the central motivations for model cards.

**Ethical considerations and limitations.** Risks, known biases, failure modes, and conditions under which the model should not be trusted.

**How to get started.** A code snippet, as in the README.

**Compute and environmental impact.** Hardware used, training time, and optionally estimated energy use or carbon emissions.

On Hugging Face, the model card begins with a YAML metadata block that makes the model searchable and enables features such as the license badge, linked datasets, and evaluation results:

```yaml
---
license: apache-2.0
language: en
library_name: pytorch
tags:
  - image-classification
  - urban-planning
datasets:
  - your-lab/roof-images
metrics:
  - accuracy
  - f1
---
# Roof Condition Classifier
...
```

Hugging Face provides a model card template and a guide describing each section. Chapter 25 includes a template adapted for Model Zoo submissions.

### Hands-On: Generate a Model Card from Code

The `huggingface_hub` library can fill Hugging Face's official template for you. This is useful when you release many models, or want the card's numbers to come straight from your evaluation results instead of being typed by hand:

```python
# scripts/make_model_card.py
from huggingface_hub import ModelCard, ModelCardData

card_data = ModelCardData(
    language="en",
    license="apache-2.0",
    library_name="pytorch",
    tags=["image-classification", "urban-planning"],
    datasets=["your-lab/roof-images"],
    metrics=["accuracy", "f1"],
)

card = ModelCard.from_template(
    card_data,
    model_id="roof-condition-classifier",
    model_summary="Classifies street-level photos of houses into four roof condition categories.",
    developers="Jane Doe (University of Michigan)",
    license="apache-2.0",
    direct_use="Research on housing conditions in Midwestern U.S. cities.",
    out_of_scope_use="Not validated for insurance, lending, or enforcement decisions.",
    bias_risks_limitations="Trained on images from three cities; winter images are underrepresented.",
)
card.save("README.md")
```

The saved `README.md` contains the YAML metadata block and every standard section heading. Fields you did not supply are marked "[More Information Needed]", which works as a to-do list: search the file for that phrase before publishing. Once the card is complete, `card.push_to_hub("your-lab/roof-condition-classifier")` uploads it to the model repository.

You can also pass in evaluation results programmatically, for example by reading the `metrics.json` from the run you are releasing (Chapter 8) and formatting a results table into the `results` argument. Numbers that are copied by hand into documentation are one of the easiest places for errors to creep in.

## Reporting Checklists

Many fields have developed checklists for reporting research that uses machine learning. They are useful even if a journal does not require them, because they list the details that reviewers and readers will want.

**NeurIPS Paper Checklist.** Developed from the NeurIPS reproducibility program {footcite}`pineau2021`, it asks authors to confirm they have described models, data, training details, compute, and statistical significance, and whether code and data are released.

**REFORMS.** A consensus checklist for ML-based science across disciplines {footcite}`kapoor2024`, developed partly in response to the leakage problems described in Chapter 1. It covers study goals, data provenance, preprocessing, modeling, leakage, metrics, and generalizability. If you are using ML as a tool in a non-CS field, this is the checklist to start with.

**Health and clinical research** has several: TRIPOD+AI for prediction models, CLAIM for medical imaging AI, and CONSORT-AI and SPIRIT-AI for clinical trials involving AI. Many medical journals require these.

**Natural language processing** has data statements {footcite}`bender2018`, which document the language varieties, speakers, and annotators behind a text dataset, and the ACL Responsible NLP checklist.

Check your target journal or conference guidelines, and look at the EQUATOR Network website for health research reporting guidelines.

## Making Work Citable

Researchers are used to citing papers. Citing software, models, and datasets directly is less common, but it is increasingly expected, and it is how the people who build these tools get credit {footcite}`smith2016`.

### CITATION.cff

A `CITATION.cff` file is a small, machine-readable file in the root of your repository that tells people how to cite your work. GitHub reads it and adds a "Cite this repository" button that produces APA and BibTeX citations. Zenodo also reads it when archiving releases.

```yaml
cff-version: 1.2.0
message: "If you use this model, please cite it as below."
title: "Roof Condition Classifier"
version: 1.0.0
doi: 10.5281/zenodo.0000000
date-released: 2026-09-01
authors:
  - family-names: Doe
    given-names: Jane
    orcid: https://orcid.org/0000-0000-0000-0000
    affiliation: University of Michigan
license: Apache-2.0
repository-code: https://github.com/your-lab/roof-condition
preferred-citation:
  type: article
  title: "Assessing roof condition from street-level imagery"
  authors:
    - family-names: Doe
      given-names: Jane
  journal: "Journal Name"
  year: 2026
  doi: 10.0000/journal.0000
```

The `preferred-citation` section lets you point people to your paper while still identifying the software itself. You can generate these files with the online `cffinit` tool, and check and convert them from the command line:

```bash
pip install cffconvert
cffconvert --validate              # checks CITATION.cff against the schema
cffconvert -f bibtex               # prints a BibTeX entry
cffconvert -f apalike              # prints an APA-style citation
```

For the minimal example above (without the `preferred-citation` section), the output is:

```text
Citation metadata are valid according to schema version 1.2.0.

@misc{YourReferenceHere,
author = {Doe, Jane},
doi = {10.5281/zenodo.0000000},
month = {9},
title = {Roof Condition Classifier},
url = {https://github.com/your-lab/roof-condition},
year = {2026}
}

Doe J. (2026). Roof Condition Classifier (version 1.0.0). DOI: 10.5281/zenodo.0000000 URL: https://github.com/your-lab/roof-condition
```

Paste the BibTeX into your README, model card, and documentation so users can copy it directly. Add `cffconvert --validate` to your CI workflow so an invalid citation file is caught before a release.

### DOIs for Software and Models

A DOI gives a specific version of your code or model a permanent, citable identifier. For code on GitHub, the Zenodo integration (Chapter 16) creates a DOI for each release automatically. For models and datasets on Hugging Face, you can generate a DOI from the repository settings (Chapter 14). Cite the DOI in your paper's code and data availability statements.

### ORCID

An ORCID iD is a persistent identifier for you as a researcher. Include it in `CITATION.cff`, model cards, and repository deposits so that your work is linked to you even if your name, email, or institution changes.

## Documentation as a Site

For a single model, a README and model card are usually enough. For a software package with many functions, a multi-model project, or a tool with a tutorial series, you may need a documentation website. Common options are **Read the Docs** with Sphinx or MkDocs (this handbook is built with Sphinx and hosted on Read the Docs), **GitHub Pages**, and **pkgdown** for R packages. These tools can generate reference documentation from docstrings, so function documentation stays in sync with the code. Chapter 24 covers writing documentation that works for newcomers and for readers using assistive technology.

## Try This

Pick a model you have trained and write a model card for it using the Hugging Face template. Pay particular attention to the "out-of-scope uses" and "limitations" sections. Then ask a colleague outside your project to read only the model card and tell you what they think the model is for and where they would not trust it. Compare their answer with your intentions.

## Further Reading

The original model cards paper {footcite}`mitchell2019` is short and explains the reasoning behind each section. Hugging Face's model card guide gives practical examples. The REFORMS paper {footcite}`kapoor2024` includes the full checklist and explanations. The software citation principles {footcite}`smith2016` explain why software should be cited directly.

## In the Model Zoo

For the proposed "Documented" tier, a Model Zoo entry needs a README with a working quickstart, a model card (for models) or datasheet (for datasets), a license, and a citation.

## Related Chapters

- [Chapter 11: Testing Reproducibility Before You Share](ch11_testing_reproducibility.md)
- [Chapter 14: Sharing on Hugging Face](../part3/ch14_hugging_face.md)
- [Chapter 17: Documenting Datasets](../part3/ch17_documenting_datasets.md)
- [Chapter 25: Checklists and Templates](../part5/ch25_checklists_templates.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
