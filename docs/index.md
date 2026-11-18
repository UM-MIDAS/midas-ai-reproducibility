# MIDAS Handbook: Reproducible and Accessible AI

```{image} _static/MIDAS_ai_logo.png
:alt: MIDAS logo
:width: 800px
:align: center
:target: https://midas.umich.edu
```

**Authors:** Nathan Fox, AI Scientist, Michigan Institute for Data and AI in Society (MIDAS), University of Michigan — *[add co-authors]*

**Companion to:** [MIDAS Handbook: Applying AI in Research](https://midas-ai-in-research.readthedocs.io/en/main/)

**Supported by:** *[Schmidt Sciences Model Zoo award — add award name and number]*

```{admonition} Draft for review
:class: warning

Version 0.3 is a complete draft of all 27 chapters, with hands-on code examples throughout. It is under review by MIDAS staff and contributors. Policies, platform limits, and computing programs change quickly; time-sensitive details were checked in September 2026 and are marked where they should be re-verified.
```

```{admonition} Not sure where to start?
:class: tip

**By goal:**
- **I'm about to publish a model or dataset** — Ch. 10, 11, 13, 14, 16
- **My funder requires a data sharing plan** — Ch. 12, 13, 16, 19
- **I can't get someone else's model to run** — Ch. 5, 6, 7
- **My data is sensitive** — Ch. 3, 19
- **I want people without big GPUs to use my work** — Ch. 21, 22
- **I want my outputs to be usable by everyone** — Ch. 23, 24
- **I want to contribute to the Model Zoo** — Ch. 2, 25
```

## Why a Second Handbook

The [AI in Research Handbook](https://midas-ai-in-research.readthedocs.io/en/main/) walks through using AI across the research lifecycle. This companion picks up where that one ends: once you have a model, a dataset, or a tool, how do you make sure someone else can find it, run it, trust it, and use it — next month and ten years from now?

It is organized around three questions:

- **Can someone reproduce it?** Environments, containers, determinism, tracking, and documentation (Part II).
- **Can someone get it?** Funder mandates, where to share (Hugging Face, Kaggle, Deep Blue Data, Zenodo, ICPSR), licensing, sensitive data, and keeping shared artifacts alive (Part III).
- **Can someone use it?** Running models on modest hardware, interactive demos, and disability accessibility for figures, notebooks, docs, and apps (Part IV).

## The MIDAS Model Zoo

This handbook is developed alongside the [MIDAS Model Zoo](https://github.com/UM-MIDAS/model-zoo), a central collection of AI tools, models, datasets, tutorials, and web applications built by researchers affiliated with MIDAS. Each chapter ends with how its practices apply to Model Zoo entries, and Chapter 25 collects them into a submission checklist.

## How the Handbook Is Organized

**Part I: Foundations** (Chapters 1–3) defines reproducibility and accessibility, introduces the Model Zoo, and covers the FAIR and CARE principles.

**Part II: Building Reproducible Models** (Chapters 4–11) covers project structure, environments, containers, randomness, experiment tracking, pipelines and CI, model documentation, and testing reproducibility before you share.

**Part III: Sharing Data and Models** (Chapters 12–20) covers funder mandates, choosing where to share, Hugging Face, Kaggle, archival repositories, dataset documentation, licensing, sensitive data, and making sure shared work stays available.

**Part IV: Accessible AI** (Chapters 21–24) covers running AI on modest hardware, interactive demos, disability accessibility, and accessible documentation.

**Part V: Resources & Reference** (Chapters 25–27) provides checklists and templates, U-M resources, and a glossary.

```{toctree}
:maxdepth: 2
:caption: Part I — Foundations
:hidden:

part1/ch01_why_it_matters
part1/ch02_model_zoo
part1/ch03_fair_principles
```
```{toctree}
:maxdepth: 2
:caption: Part II — Building Reproducible Models
:hidden:

part2/ch04_project_structure
part2/ch05_environments
part2/ch06_containers
part2/ch07_determinism
part2/ch08_experiment_tracking
part2/ch09_workflows
part2/ch10_documenting_models
part2/ch11_testing_reproducibility
```
```{toctree}
:maxdepth: 2
:caption: Part III — Sharing Data and Models
:hidden:

part3/ch12_mandates
part3/ch13_where_to_share
part3/ch14_hugging_face
part3/ch15_kaggle
part3/ch16_archival_repositories
part3/ch17_documenting_datasets
part3/ch18_licensing
part3/ch19_sensitive_data
part3/ch20_persistence
```
```{toctree}
:maxdepth: 2
:caption: Part IV — Accessible AI
:hidden:

part4/ch21_low_resource
part4/ch22_demos
part4/ch23_disability_access
part4/ch24_accessible_docs
```
```{toctree}
:maxdepth: 2
:caption: Part V — Resources & Reference
:hidden:

part5/ch25_checklists_templates
part5/ch26_um_resources
part5/ch27_glossary
```

---

## Citation and Reuse

This handbook is published under a [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) license. Suggested citation:

> Fox, N., et al. (2026). *MIDAS Handbook: Reproducible and Accessible AI*. Michigan Institute for Data and AI in Society, University of Michigan. Retrieved from *[Read the Docs URL]*

---

## How This Handbook Was Written

This handbook was drafted with AI-assisted tools, and we want to be transparent about how.

**Purpose of AI use:** The authors defined the scope, audience, and chapter structure, drawing on MIDAS's work with the Model Zoo and on research consultations. Claude (Anthropic) was used to draft chapter text from that outline and to check time-sensitive facts such as funder policies, platform limits, and computing programs against current sources.

**Human oversight:** Every chapter is being reviewed and revised by the authors and MIDAS staff before release. Framing decisions, recommendations, and final wording are the authors' responsibility. *[Update this section to describe the actual review process and any other tools used before publishing.]*

**Limitations and feedback:** AI-assisted content can contain errors, and policies and platforms described here change quickly. If you find something wrong or out of date, please tell us through the feedback link on each page.

---

## Version History

**v0.3.0** — November 2026 — Hands-on examples throughout. More than 60 new code examples across all chapters, most tested while writing, with real outputs shown. New scripts index in Chapter 25. Accessibility fixes to the site theme so that every page passes automated WCAG 2.1 AA checks (Chapter 23).

**v0.2.0** — September 2026 — Complete first draft of all 27 chapters for internal review.

**v0.1.0** — September 2026 — Outline release. Structure, chapter goals, and section plans for 27 chapters.
