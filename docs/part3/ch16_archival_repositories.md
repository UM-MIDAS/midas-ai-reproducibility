# Chapter 16: Institutional and Archival Repositories

:::{admonition} What You Will Learn
:class: tip

- What archival repositories guarantee that community hubs do not
- How to deposit data in Deep Blue Data, U-M's research data repository
- How to archive every GitHub release automatically with Zenodo
- When to use ICPSR and discipline-specific repositories
- How DOIs, version DOIs, and other persistent identifiers work
:::

## What "Archival" Means

Chapter 13 distinguished community hubs, built for use, from archival repositories, built for preservation. This chapter covers the archival side in detail.

An archival repository makes several commitments that hubs generally do not:

**Persistent identifiers.** Each deposit gets a DOI that will always resolve to a landing page, even if the files move to new storage or the repository changes its website.

**Fixity.** Files are stored with checksums and checked regularly to make sure they have not been corrupted or altered. What you deposit is what people will get, bit for bit, years later.

**Immutability.** A published version cannot be quietly changed. Corrections are made by publishing a new version, and the old version remains available.

**Tombstones instead of deletions.** If a deposit must be removed (for example, because of a legal problem), the landing page remains with an explanation, so citations do not lead to a dead link.

**Long-term commitment.** The repository has an institutional backer, a succession plan, and a stated preservation policy.

These are the properties that make a DOI worth citing. When a journal asks for a "permanent, publicly accessible archive," this is what it means.

## Deep Blue Data

**Deep Blue Data** is the University of Michigan's research data repository, run by the U-M Library. It accepts research data from all disciplines generated in U-M-affiliated research and intended for reuse.

**Who can deposit.** Current U-M faculty, graduate students, and research staff; multi-institutional collaborations that include U-M participants; designated proxies; and undergraduates with faculty or staff permission.

**Cost.** There is currently no charge to deposit. Costs are covered by the U-M Library.

**Curation.** Every deposit is reviewed by a data curator, who works with you to make sure the dataset is well documented and follows FAIR principles (Chapter 3). This is a real advantage: curators often catch missing documentation, unclear file organization, or format issues that would frustrate future users. Plan for a short back-and-forth before publication.

**DOIs and preservation.** Each dataset receives a DOI. The Library is committed to maintaining access and preserving deposits for the long term.

**What to prepare.** A README describing the dataset (Chapter 17 has a template), files in open or widely used formats, a license (CC0 or CC BY 4.0 are common choices; Chapter 18), and author information with ORCIDs. For AI projects, Deep Blue Data is a good archival home for training data, evaluation data, the final model weights reported in a paper, and a saved container image (Chapter 6).

**Large datasets.** If your dataset is very large, contact the Deep Blue Data team before depositing to discuss options.

Deep Blue Data is especially valuable for U-M researchers because it is local: you can talk to the curators, and the institutional commitment is directly tied to your university. It also makes U-M's research output visible as a collection.

## Zenodo and the GitHub Integration

**Zenodo** is a general-purpose research repository operated by CERN and funded in part by the European Commission. Anyone can deposit, and it accepts any kind of research output: datasets, software, posters, presentations, and more. Deposits are free, with a standard limit of 50 GB per record (larger quotas can be requested). Zenodo commits to preserving content for the lifetime of the repository, backed by CERN's long-term infrastructure. Deposits can be open, embargoed, or restricted to approved users.

Zenodo's most useful feature for AI researchers is its **GitHub integration**, which archives your code automatically:

1. Log in to Zenodo with your GitHub account.
2. In Zenodo's GitHub settings, switch on archiving for your repository.
3. Create a Release on GitHub (Chapter 4).

Zenodo then downloads a snapshot of the repository at that release, creates a record, and assigns a DOI. Every future release gets its own DOI automatically. Zenodo reads your `CITATION.cff` file (Chapter 10) to fill in authors, title, and other metadata; alternatively, you can provide a `.zenodo.json` file for finer control.

A `.zenodo.json` file in the repository root lets you control exactly how the record is described, including links to the paper and the dataset. When it is present, Zenodo uses it in place of `CITATION.cff`:

```json
{
  "title": "Roof Condition Classifier: training and evaluation code",
  "upload_type": "software",
  "description": "Code to reproduce all analyses in Doe et al. (2026).",
  "creators": [
    {"name": "Doe, Jane", "affiliation": "University of Michigan", "orcid": "0000-0000-0000-0000"}
  ],
  "license": "MIT",
  "keywords": ["computer vision", "housing", "reproducibility"],
  "related_identifiers": [
    {"identifier": "10.0000/journal.0000", "relation": "isSupplementTo", "resource_type": "publication-article"},
    {"identifier": "10.7302/xxxx-xxxx", "relation": "references", "resource_type": "dataset"}
  ]
}
```

The `related_identifiers` are what connect your code, data, and paper in the scholarly record (Chapter 3). Check that the file is valid JSON before you make a release, since an invalid file can cause the archive step to fail.

Add the Zenodo DOI badge to your README, and cite the DOI in your paper's code availability statement.

The GitHub integration archives only what is in the Git repository. Large model weights or data that live outside Git need to be uploaded to Zenodo (or elsewhere) separately.

### Hands-On: Deposit Files with the Zenodo API

For files outside Git, such as final model weights or a saved container image, you can use Zenodo's web form, or script the deposit with its REST API. Scripting is worth it when you deposit regularly, or want the upload to be part of a release pipeline. Practice on the **Zenodo Sandbox** (sandbox.zenodo.org), a separate test site whose DOIs are not real, and switch to the main site only when everything works. Create a personal access token in your account settings with the deposit scopes, and keep it in an environment variable, never in code.

```python
# scripts/deposit_zenodo.py
import os
from pathlib import Path
import requests

ZENODO = "https://sandbox.zenodo.org/api"     # change to https://zenodo.org/api when ready
params = {"access_token": os.environ["ZENODO_TOKEN"]}

# 1. Create an empty draft deposition
r = requests.post(f"{ZENODO}/deposit/depositions", params=params, json={})
r.raise_for_status()
dep = r.json()

# 2. Upload files to the draft's file bucket
for path in [Path("release/model.safetensors"), Path("release/README.md"),
             Path("release/SHA256SUMS.txt")]:
    with open(path, "rb") as f:
        requests.put(f"{dep['links']['bucket']}/{path.name}",
                     data=f, params=params).raise_for_status()

# 3. Describe it
metadata = {"metadata": {
    "title": "Roof Condition Classifier v1.0: trained weights",
    "upload_type": "dataset",
    "description": "Final model weights and model card for Doe et al. (2026).",
    "creators": [{"name": "Doe, Jane", "affiliation": "University of Michigan",
                  "orcid": "0000-0000-0000-0000"}],
    "license": "apache-2.0",
    "version": "1.0",
    "related_identifiers": [{"identifier": "https://huggingface.co/your-lab/roof-condition-classifier",
                             "relation": "isIdenticalTo", "resource_type": "dataset"}],
}}
requests.put(f"{ZENODO}/deposit/depositions/{dep['id']}",
             params=params, json=metadata).raise_for_status()

print("Draft ready for review:", dep["links"]["html"])
# 4. After checking the draft in your browser, publish it (this cannot be undone):
# requests.post(f"{ZENODO}/deposit/depositions/{dep['id']}/actions/publish", params=params)
```

Leaving the final publish step commented out is deliberate: review the draft in the web interface first, because a published record and its DOI are permanent. To add a new version later, call the `actions/newversion` endpoint on the published deposition, which creates a linked draft that shares the same concept DOI. Check Zenodo's developer documentation for the current API details.

## ICPSR

The **Inter-university Consortium for Political and Social Research (ICPSR)**, headquartered at the University of Michigan, is one of the world's largest archives of social and behavioral science data. It is particularly important for research involving human participants because of its extensive support for restricted data.

ICPSR offers:

- **Curation** services that review, clean, and document datasets, and check for disclosure risk.
- **Public-use** files, which are freely downloadable after de-identification.
- **Restricted-use** files, available only to researchers who apply and sign a data use agreement.
- A **Virtual Data Enclave**, where approved researchers can analyze sensitive data in a secure remote environment without downloading it.
- **openICPSR**, a self-deposit option for researchers who want to share data quickly, with optional curation services.

Some ICPSR services have costs, and some funders and journals have arrangements with ICPSR. If your data involve human subjects, especially surveys, interviews, or administrative records, talk to ICPSR early. Chapter 19 covers restricted data in more detail.

## Discipline Repositories

Many fields have established repositories that reviewers and colleagues expect you to use. Examples include:

- **Dryad**: data underlying publications, especially in ecology and evolution.
- **Dataverse** (including Harvard Dataverse): general and social science data, with support for tabular data exploration and ML-ready Croissant metadata.
- **GenBank, SRA, and ENA**: nucleotide sequences and sequencing reads.
- **dbGaP**: genotype and phenotype data, with controlled access.
- **OpenNeuro**: neuroimaging data in the BIDS format.
- **PANGAEA**: earth and environmental science data.
- **OSF**: project materials and preregistrations, popular in psychology.
- **figshare**: general repository, often integrated with journals.

To find the repository for your field, search **re3data.org**, a registry of thousands of research data repositories, or check your target journal's recommended repositories list.

Discipline repositories often require specific formats and metadata standards. That extra work pays off because it makes your data interoperable with other datasets in the field.

## Software Heritage

**Software Heritage** is a nonprofit archive with the goal of preserving all publicly available source code. It automatically crawls public repositories on GitHub, GitLab, and other forges, and you can request that your repository be archived immediately. Each archived artifact gets a SWHID (Software Heritage identifier) that can be cited. Software Heritage is a useful backstop: even if you forget to archive your code on Zenodo, it may already have been preserved.

## Persistent Identifiers

Several kinds of persistent identifiers appear throughout this handbook.

**DOIs (Digital Object Identifiers)** identify research outputs: papers, datasets, software, and models. A DOI like `10.5281/zenodo.1234567` resolves through `https://doi.org/` to the current landing page, wherever it is. DOIs for data and software are usually issued through DataCite, which also maintains a searchable index of their metadata.

**Version DOIs and concept DOIs.** Zenodo and some other repositories issue two kinds of DOI. Each specific version gets its own **version DOI**. The record as a whole also gets a **concept DOI**, which always resolves to the latest version. In a paper, cite the version DOI so readers get exactly what you used. On a project website or README, you can link the concept DOI so visitors find the newest version.

**ORCID iDs** identify researchers (Chapter 10).

**ROR IDs** (Research Organization Registry) identify institutions, so affiliations can be linked unambiguously.

Using these identifiers consistently in your metadata links your datasets, software, papers, and funding into a connected record that search engines and funders can follow.

## Try This

Connect one of your GitHub repositories to Zenodo, add a `CITATION.cff` file if it does not have one, and create a release. Check that the Zenodo record has the right authors and a DOI. Then find the Deep Blue Data deposit form and review what information it asks for. If you have a dataset ready, start a deposit and contact the curators with any questions.

## Further Reading

The Deep Blue Data "About" pages describe deposit policies and the curation process. Zenodo's policies page explains its preservation commitment and limits. The TRUST principles {footcite}`lin2020` describe what to look for in any repository. ICPSR's website includes guides for data depositors.

## Related Chapters

- [Chapter 12: Planning for Sharing](ch12_mandates.md)
- [Chapter 13: Choosing Where to Share](ch13_where_to_share.md)
- [Chapter 20: Making Sure It Stays Shared](ch20_persistence.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
