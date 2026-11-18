# MIDAS Handbook: Reproducible and Accessible AI

A practical, open handbook on building reproducible AI models, sharing data and models so they stay available, and making AI research outputs accessible — on modest hardware and to people with disabilities. Developed by the [Michigan Institute for Data and AI in Society (MIDAS)](https://midas.umich.edu) alongside the [MIDAS Model Zoo](https://github.com/UM-MIDAS/model-zoo).

Companion to the [MIDAS Handbook: Applying AI in Research](https://midas-ai-in-research.readthedocs.io/en/main/).

**Status:** v0.3 draft of all 27 chapters with hands-on code examples, for internal review. See Chapter 25 for an index of the scripts.

## Structure

| Part | Chapters |
|---|---|
| I — Foundations | 1 Why it matters · 2 The Model Zoo · 3 FAIR, FAIR4RS, CARE |
| II — Building Reproducible Models | 4 Project structure & Git · 5 Environments · 6 Containers · 7 Determinism · 8 Experiment tracking · 9 Pipelines & CI · 10 Model docs & citation · 11 Testing reproducibility |
| III — Sharing Data and Models | 12 Funder mandates & DMPs · 13 Where to share · 14 Hugging Face · 15 Kaggle · 16 Archival repositories · 17 Documenting datasets · 18 Licensing · 19 Sensitive data · 20 Making sure it stays shared |
| IV — Accessible AI | 21 Modest hardware · 22 Demos & web apps · 23 Disability accessibility · 24 Accessible docs & teaching |
| V — Resources | 25 Checklists & templates · 26 U-M resources · 27 Glossary |

## Build locally

```bash
pip install -r requirements.txt
sphinx-build -b html docs docs/_build/html
```

## Launch TODO

- [ ] Create the GitHub repo (placeholder links assume `UM-MIDAS/midas-ai-reproducibility`) and import it on Read the Docs
- [ ] Replace `_static/MIDAS_ai_logo.png` (currently the AI in Research logo)
- [ ] Add co-authors, Schmidt Sciences award details, and AI-use disclosure in `docs/index.md`
- [ ] Set up the feedback form, giscus, and analytics in `docs/_templates/layout.html`
- [ ] Confirm Model Zoo tier names (Ch. 2) with the Model Zoo team

## License

[CC BY 4.0](LICENSE)
