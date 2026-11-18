# Chapter 13: Choosing Where to Share

:::{admonition} What You Will Learn
:class: tip

- The difference between community hubs and archival repositories
- How to choose a home for data, models, and code based on type, size, sensitivity, and audience
- Why the best answer is often "two places, linked"
- Where not to share research outputs
:::

## Many Doors, Different Purposes

Once you have decided to share a dataset or model, the next question is where. The options can feel overwhelming: GitHub, Hugging Face, Kaggle, Zenodo, Deep Blue Data, ICPSR, Dryad, Dataverse, figshare, OSF, and many discipline-specific repositories. They overlap, and several of them could technically hold your files.

The key to choosing is to recognize that these platforms are built for different purposes. Some are optimized for **use**: making it easy for people to discover, download, and run your work today. Others are optimized for **preservation**: guaranteeing that a specific version will still exist, unchanged, decades from now, with a citable identifier. Very few do both well.

## Community Hubs vs. Archival Repositories

**Community hubs**, such as Hugging Face, Kaggle, and GitHub, are where practitioners go to find and use things. They have large active audiences, search and recommendation features, integration with popular libraries (loading a Hugging Face model or dataset is one line of code), and built-in tools like dataset viewers, notebooks, and demos. They support versioning through Git or version histories. But they are companies with their own business priorities. Their terms, storage limits, and features change. Content can be deleted by its owner at any time. They generally do not make formal long-term preservation commitments.

**Archival repositories**, such as Deep Blue Data, Zenodo, ICPSR, Dryad, and discipline repositories, are designed for the scholarly record. They assign DOIs, keep deposited files unchanged, check file integrity over time, and commit to preserving content for the long term. Many have curators who review deposits. If content must be removed, they keep a "tombstone" landing page so the DOI never leads nowhere. The TRUST principles (Transparency, Responsibility, User focus, Sustainability, and Technology) describe what makes such a repository trustworthy {footcite}`lin2020`. The trade-off is that they are less convenient to use: downloading a dataset from an archive usually means clicking a link or using a generic API, not calling a one-line loader, and they have much smaller audiences of practitioners.

**Code hosting platforms**, especially GitHub, sit in between. GitHub is where code is developed and discovered, but it is not an archive. Repositories can be deleted or made private, and accounts can be closed. For preservation, code should also be archived, which Zenodo's GitHub integration and Software Heritage make easy (Chapter 16).

## A Decision Table

The table below summarizes the main options covered in this handbook. Details change, so check each platform's current documentation.

| | Hugging Face | Kaggle | GitHub | Zenodo | Deep Blue Data | ICPSR |
|---|---|---|---|---|---|---|
| **Best for** | Models, ML datasets, demos | Datasets, notebooks, teaching | Code | Code releases, datasets, any research output | U-M research datasets | Social and behavioral science data |
| **Audience** | ML practitioners | Data science learners and practitioners | Developers | Researchers | Researchers | Social science researchers |
| **DOI** | Yes, on request | Yes, for datasets | No (use Zenodo) | Yes, automatic | Yes, automatic | Yes |
| **Versioning** | Git revisions | Dataset versions | Git | Version DOIs | Versions | Versions |
| **Access control** | Public, private, gated | Public, private | Public, private | Open, embargoed, restricted | Open, embargoed | Public, restricted-use, enclave |
| **Curation review** | No | No | No | Light | Yes, by curators | Yes, extensive |
| **Preservation commitment** | Not formal | Not formal | Not formal | Long-term (CERN) | Long-term (U-M Library) | Long-term |
| **Size guidance** | Large (hundreds of GB per dataset) | Up to ~200 GB per dataset | Small files only | 50 GB per record (more on request) | Contact curators for large data | Varies |
| **Cost to deposit** | Free for public | Free | Free for public | Free | Free for U-M researchers | Varies by service |

A few additional repositories are worth knowing:

- **Harvard Dataverse** and other Dataverse installations: general-purpose, with strong support for social science data, and generate Croissant metadata for ML use.
- **Dryad**: curated repository for data underlying publications, widely used in ecology and evolutionary biology.
- **OSF** (Open Science Framework): project management and sharing, popular in psychology, with preregistration support.
- **figshare**: general repository, often integrated with journals.
- **OpenML**: datasets and ML benchmark results with standardized metadata.
- **Discipline repositories**: GenBank and SRA for sequences, OpenNeuro for neuroimaging, PANGAEA for earth and environmental data, and many others. If your field has an established repository, reviewers will expect you to use it. The registry **re3data.org** lists thousands of repositories searchable by discipline.

### Hands-On: Size Up Your Artifact

Size is often what rules a platform in or out. Before choosing, measure what you actually have:

```python
# size_up.py: will this folder fit where I want to share it?
import sys
from pathlib import Path

MB, GB = 1024**2, 1024**3
files = [p for p in Path(sys.argv[1]).rglob("*") if p.is_file()]
sizes = {p: p.stat().st_size for p in files}
total = sum(sizes.values())
largest = max(sizes, key=sizes.get)

print(f"{len(files)} files, {total / GB:.2f} GB total")
print(f"largest file: {largest} ({sizes[largest] / GB:.2f} GB)\n")

# Rough guidance as of late 2026; check each platform's current limits before uploading
limits = [  # (platform, applies to, limit in bytes, label)
    ("GitHub, without LFS",          "file",  100 * MB, "100 MB per file"),
    ("Zenodo, standard quota",       "total", 50 * GB,  "50 GB per record"),
    ("Kaggle",                       "total", 200 * GB, "about 200 GB per dataset"),
    ("Hugging Face, recommended",    "file",  200 * GB, "200 GB per file"),
]
for platform, kind, limit, label in limits:
    value = sizes[largest] if kind == "file" else total
    print(f"{'fits   ' if value <= limit else 'TOO BIG'}  {platform:28} ({label})")
if len(files) > 10_000:
    print("\nMany small files: bundle them (Parquet, WebDataset shards, or zip) before uploading.")
```

```bash
python size_up.py release/
```

```text
2 files, 0.14 GB total
largest file: release/model.safetensors (0.14 GB)

TOO BIG  GitHub, without LFS          (100 MB per file)
fits     Zenodo, standard quota       (50 GB per record)
fits     Kaggle                       (about 200 GB per dataset)
fits     Hugging Face, recommended    (200 GB per file)
```

Here a 140 MB model file is too big for a plain GitHub repository but fits comfortably everywhere else, which points toward Hugging Face for use and Zenodo or Deep Blue Data for the archive. File count matters too: tens of thousands of small image files upload slowly and strain every platform, so bundle them first.

## Choosing by Artifact Type

**Trained models.** Share on **Hugging Face** for usability; generate a DOI there, and deposit a copy of the final weights, model card, and code in **Zenodo** or **Deep Blue Data** for preservation, especially for models cited in papers. If the model is large, the archival copy might be limited to the final version reported in the paper.

**ML datasets** (for training and benchmarking). Share on **Hugging Face** or **Kaggle** for usability, and archive a versioned copy in **Deep Blue Data**, **Zenodo**, or **Dataverse**.

**Research datasets** (supporting a publication, not primarily for ML). Deposit in a **discipline repository** if one exists, otherwise **Deep Blue Data** or **Zenodo**. Mirror to a hub only if there is an ML audience.

**Sensitive or restricted data.** Use a repository with controlled access, such as **ICPSR** (restricted-use and virtual data enclave), **dbGaP** for genomic data, or a gated Hugging Face repository for lower-risk cases. See Chapter 19.

**Code.** Develop on **GitHub** and archive each release with **Zenodo**. Software Heritage automatically archives public GitHub repositories and can be asked to archive yours on demand.

**Container images.** Publish on **GitHub Container Registry** or **Docker Hub** for use, and deposit a saved image file in **Zenodo** or **Deep Blue Data** for preservation (Chapter 6).

**Demos and web apps.** Host on **Hugging Face Spaces** or an institutional server (Chapter 22), and archive the code.

## The Two-Home Pattern

For most AI research outputs, the best answer is two homes, linked in both directions:

1. **An archival copy** of the exact version used in the paper, with a DOI, in Deep Blue Data, Zenodo, or a discipline repository. This is what you cite.
2. **A usable copy** on Hugging Face, Kaggle, or GitHub, where people discover and use the work, and where you can publish updates.

Link them: the archival landing page links to the hub, and the hub README or model card includes the archival DOI in its citation section. If the hub copy is ever deleted or changed, the archival copy still exists. If someone finds the hub copy, they know how to cite it and where the permanent version lives.

This sounds like extra work, but it is mostly a one-time setup. The Zenodo GitHub integration archives code automatically, and uploading a finished dataset to a second location takes minutes compared with the months spent creating it.

## What Not to Use

Some places are commonly used to share research outputs but are not suitable.

**Personal cloud storage links** (Google Drive, Dropbox, OneDrive). Links break when files are moved, when accounts are closed at graduation, or when sharing settings change. There is no versioning, no DOI, and no metadata.

**Lab or personal websites.** These go stale and disappear when servers are retired or people move.

**"Available on request."** As discussed in Chapter 12, this fails often and is increasingly not accepted by funders or journals.

**Supplementary material files** attached to journal articles. These are better than nothing, but are often limited in size and format, may be behind a paywall, and are hard to find and version. Deposit in a repository and cite it instead.

## Try This

Take one dataset, model, or code base from your recent work. Using the decision table, choose an archival home and a usable home. Check whether your field has a discipline repository by searching re3data.org. Then draft the data availability statement you would put in a paper, citing both locations.

## Further Reading

The TRUST principles paper {footcite}`lin2020` explains what to look for in a trustworthy repository. re3data.org and FAIRsharing.org are searchable registries of repositories and standards. The U-M Library's research data services pages include guidance on choosing a repository.

## In the Model Zoo

The Model Zoo links to wherever your artifact lives. For the proposed "Reproducible" tier, entries should include at least one archival copy with a DOI.

## Related Chapters

- [Chapter 14: Sharing on Hugging Face](ch14_hugging_face.md)
- [Chapter 15: Sharing on Kaggle](ch15_kaggle.md)
- [Chapter 16: Institutional and Archival Repositories](ch16_archival_repositories.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
