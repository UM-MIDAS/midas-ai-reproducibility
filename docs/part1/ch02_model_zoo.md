# Chapter 2: The MIDAS Model Zoo

:::{admonition} What You Will Learn
:class: tip

- What the MIDAS Model Zoo is and what kinds of resources it collects
- What makes an entry "Zoo-ready," and how the practices in this handbook map to Zoo entries
- How to submit, update, or retire an entry
:::

:::{admonition} Working draft
:class: warning

The Model Zoo is under active development, and a public website is planned. The entry tiers and contribution workflow described in this chapter are proposals for discussion with the Model Zoo team and may change.
:::

## What the Model Zoo Is

The [MIDAS Model Zoo](https://github.com/UM-MIDAS/model-zoo) is a growing, open library of AI and data science resources developed by researchers affiliated with the Michigan Institute for Data and AI in Society. It collects things that other researchers, instructors, and practitioners can pick up and use: trained models, software packages, datasets, tutorials, and web applications.

The Zoo does not host most of these resources itself. A model might live on Hugging Face, a dataset on Zenodo or Deep Blue Data, a package on GitHub and CRAN, and a web application on a university server. The Zoo is the curated index that ties them together, tells you what each resource does and who made it, and links you to the place where it lives. Think of it less as a warehouse and more as a well-kept catalog.

The current collection is organized into five categories.

**Software.** Reusable libraries and packages, such as `PyStarshade` for starshade optics simulation, `isweep` for studying natural selection from identity-by-descent segments, `bifrost` for phylogenetic trait evolution, and `Urban-Worm` for assessing urban environments with vision-language models.

**Tutorials.** Teaching materials, such as a walkthrough of fitting PyTorch models.

**Datasets.** Curated data for training or evaluating models, such as a collection of AI-validated plant observations from social media, archived on Zenodo.

**Web applications.** Tools that run in a browser with no installation, such as the Clinical Trial Randomization Tool.

**Models.** Trained model weights with example usage, such as image classification models hosted on Hugging Face.

## Why a Curated Index

A reasonable question is why a separate catalog is needed when GitHub and Hugging Face are already searchable. There are four reasons.

**Discoverability across disciplines.** A researcher in public health may never search for an astronomy package, but the statistical methods inside it may be exactly what they need. The Zoo puts work from very different fields side by side, organized by task as well as by domain.

**Quality signals.** Anyone can post a repository. A Zoo entry signals that the resource has been reviewed for a baseline of documentation and usability, and (in the higher tiers described below) that someone has checked it actually runs.

**Credit for creators.** Each entry names its creator and links to associated papers. For graduate students and postdocs, a Zoo listing is a visible record of research software and data contributions that often go uncredited in traditional publication metrics.

**Stewardship after projects end.** Grants end, students graduate, and lab websites go stale. The Zoo gives resources an institutional home and a process for periodically checking that links still work (Chapter 20).

## Anatomy of an Entry

Every Zoo entry, regardless of category, needs a small set of core fields: a name, a one- or two-sentence description written for a non-specialist, a domain, a link to where the resource lives, the creator's name and MIDAS affiliation, and a license (Chapter 18). Most entries should also have a citation, either a paper or a DOI for the resource itself (Chapter 10).

Beyond the core fields, each category has its own expectations.

**Models** should link to a model card (Chapter 10) that describes the task, training data, evaluation, and limitations, and should include a minimal code example showing how to load the model and run a prediction. A listed minimum hardware requirement (Chapter 21) helps users know whether they can run it.

**Datasets** should link to a persistent, citable copy with a DOI (Chapter 16) and a datasheet or README describing how the data were collected and what they can and cannot be used for (Chapter 17).

**Software** should have installation instructions that work, a pinned environment or package release (Chapter 5), and ideally a test suite or at least a runnable example.

**Tutorials** should run end to end in a free environment such as Google Colab (Chapter 24).

**Web applications** should state who maintains them and should meet basic accessibility standards (Chapters 22 and 23).

## Proposed Zoo Tiers

Not every resource needs to meet every standard on day one. A tiered system lets researchers contribute early and improve over time, while telling users what to expect. The following four tiers are proposed.

| Tier | What it means | Key chapters |
|---|---|---|
| **Listed** | Core fields present, link works, license stated. | 2, 18 |
| **Documented** | README, model card or datasheet, and citation. Someone new could understand what the resource does and how to use it. | 10, 17 |
| **Reproducible** | Pinned environment or container, archived version with a DOI, and a reviewer has run the quickstart successfully on a clean machine. | 5, 6, 11, 16 |
| **Accessible** | Runs on modest hardware or has a hosted demo, and documentation and demos pass an accessibility check. | 21, 22, 23 |

The tiers build on each other, and each maps to a section of the checklist in Chapter 25. A resource can move up the tiers as its creator adds documentation or packaging.

## How to Contribute

The Model Zoo currently lives on GitHub, and contributions are made by editing the README table through a pull request. If you are not comfortable with pull requests, you can contact the MIDAS team, who will add the entry on your behalf.

A typical contribution goes like this. You make sure your resource lives somewhere stable (not a personal drive), with a license and a README. You open a pull request adding a row to the appropriate table, or send the details to the MIDAS team. A reviewer checks that the links work and the core fields are present, and may suggest improvements. Once merged, your entry appears in the Zoo, and later on the Zoo website.

### Hands-On: Submitting an Entry by Pull Request

If you have the GitHub command-line tool (`gh`) installed, the whole contribution takes a few commands. You can do the same steps in the GitHub web interface by clicking the pencil icon on the README.

```bash
gh repo fork UM-MIDAS/model-zoo --clone      # your own copy of the Zoo
cd model-zoo
git switch -c add-roof-condition-classifier
# edit README.md and add one row to the right table (see below)
git commit -am "Add roof condition classifier to Models"
git push -u origin add-roof-condition-classifier
gh pr create --title "Add roof condition classifier" \
    --body "Model card, license (Apache-2.0), and DOI included. Quickstart tested in Colab."
```

Each table in the README has its own columns. A new row in the Models table follows the same pattern as the existing entries:

```markdown
| **`roof-condition-classifier`** | Image Classification - classifies street-level photos of houses into four roof condition categories. | [Hugging Face Link](https://huggingface.co/your-lab/roof-condition-classifier) | Jane Doe (MIDAS Affiliate)
```

Before opening the pull request, check that every link you are adding works for someone who is not logged in. This short script does it for you:

```python
import requests
links = [
    "https://huggingface.co/your-lab/roof-condition-classifier",
    "https://doi.org/10.5281/zenodo.0000000",
]
for url in links:
    r = requests.get(url, timeout=30, allow_redirects=True)
    print(r.status_code, url)     # 200 means the page loads; 401/404 mean it does not
```

A private Hugging Face repository returns an error status here even though it opens fine in your own logged-in browser, which is exactly the problem this check is meant to catch.

When the Zoo website launches, entries may move from README rows to one small structured file per entry, which makes filtering and automated checks easier. A possible format, for discussion with the Model Zoo team:

```yaml
# entries/roof-condition-classifier.yaml (proposed format)
name: roof-condition-classifier
category: model
domain: Urban planning
task: Image classification
summary: Classifies street-level photos of houses into four roof condition categories.
links:
  primary: https://huggingface.co/your-lab/roof-condition-classifier
  archive_doi: https://doi.org/10.5281/zenodo.0000000
  paper: https://doi.org/10.0000/journal.0000
revision: v1.0
license: Apache-2.0
creator: {name: Jane Doe, affiliation: MIDAS Affiliate, orcid: 0000-0000-0000-0000}
min_hardware: CPU, 4 GB RAM
tier: reproducible
last_verified: 2026-11-01
```

If you want your entry to reach a higher tier, use the checklist in Chapter 25 before submitting. Reviewers will use the same checklist.

## Keeping Entries Alive

Listing a resource is the beginning of its life in the Zoo, not the end. Over time links break, dependencies change, and creators move on. The Zoo plans to run periodic checks (described in Chapter 20) that confirm each link resolves and, for higher-tier entries, that the quickstart still runs. When a check fails, the Zoo team contacts the creator. If a resource can no longer be maintained, the entry is marked as deprecated with a note explaining why, rather than silently removed. Where possible, it links to an archived copy or a successor.

As a creator, you can help by using an institutional or group account rather than a personal one where possible, by naming a backup contact, and by telling the Zoo team when you move institutions.

## The Model Zoo Website

A public website for the Model Zoo is in development. It will make the collection searchable and filterable by domain, task, category, and tier, and will give each entry its own page with its description, links, citation, and status. This handbook will be updated with details as the site launches.

## Try This

Look at one resource you have created, whether a script, a dataset, a trained model, or a tutorial, and check it against the "Listed" and "Documented" tiers above. What is missing? If it is only a license and a README, you can likely fix that in an hour and submit it to the Zoo this week.

## Related Chapters

- [Chapter 10: Documenting Models](../part2/ch10_documenting_models.md)
- [Chapter 20: Making Sure It Stays Shared](../part3/ch20_persistence.md)
- [Chapter 25: Checklists and Templates](../part5/ch25_checklists_templates.md)

---

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
