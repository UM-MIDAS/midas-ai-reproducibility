# Chapter 3: FAIR, FAIR4RS, and CARE

:::{admonition} What You Will Learn
:class: tip

- What the FAIR principles mean in practice for data, models, and software
- Why FAIR is not the same as "open"
- What the CARE principles add when data come from or affect communities
- How to run a quick FAIR self-assessment on your own work
:::

## Why Principles at All

Most of this handbook is practical: which command to run, which file to write, which repository to choose. This chapter is the exception. It covers two sets of principles that shape the rest of the book, and that funders, journals, and repositories increasingly use as a yardstick. You will see the word "FAIR" in grant guidance, repository policies, and data management plan templates. Knowing what it actually asks for makes those requirements much less mysterious.

## FAIR in Plain Language

The FAIR principles were published in 2016 by a group of researchers, funders, and publishers who wanted a shared definition of well-managed research data {footcite}`wilkinson2016`. The four letters stand for Findable, Accessible, Interoperable, and Reusable. An important feature of FAIR is that it was written with machines in mind as well as people: the goal is for software to be able to find and use data with minimal human help.

**Findable** means that the data and its metadata have a globally unique, persistent identifier (such as a DOI) and are described with rich metadata in a searchable resource. In practice: your dataset has a DOI from a repository like Deep Blue Data or Zenodo, not just a URL on a lab page, and its description includes keywords, a clear title, and the names of its creators.

**Accessible** means that the data can be retrieved by its identifier using a standard, open protocol (such as HTTPS), with authentication where needed, and that the metadata stay available even if the data themselves are removed. In practice: someone who has the DOI can get to a landing page, and if the data are restricted, that page explains how to request access. If the data are ever withdrawn, the landing page remains and says so.

**Interoperable** means that data use formal, shared vocabularies and formats so they can be combined with other data and processed by common tools. In practice: CSV or Parquet rather than a proprietary format, standard units, column names documented in a data dictionary, and controlled vocabularies (such as standard species names or geographic codes) where your field has them.

**Reusable** means data have a clear license, detailed provenance, and meet the standards of the relevant community. In practice: a license like CC BY 4.0 is attached, the README explains how the data were collected and processed, and the documentation follows whatever conventions your field expects.

A useful way to remember the difference between the letters: F and A are mostly about where you put things and how you label them, which is largely decided by your choice of repository. I and R are mostly about what is inside, which is decided by you.

## FAIR for Research Software and Models

The original FAIR principles were written for data. Software is different: it has dependencies, it executes, and it changes through versions. In 2022 the FAIR for Research Software working group published an adapted set of principles, known as FAIR4RS {footcite}`barker2022`.

The adaptations are intuitive once you think about what makes software reusable. Each version of the software should have its own identifier, not just the project as a whole. The software should describe its dependencies in a machine-readable way (a lockfile or `environment.yml`, as in Chapter 5). It should read and write data in community-standard formats. And it should have a license and a citation file.

Trained machine learning models sit somewhere between data and software. The weights are data: a large array of numbers. But they are only useful with code that defines the architecture and runs inference, and they depend on the training data and procedure that produced them. In practice, a FAIR model has a persistent identifier for a specific version of the weights, a model card that describes what it is (Chapter 10), a pointer to the exact code and environment needed to run it, a license that covers the weights (which may differ from the code license, as discussed in Chapter 18), and a reference to the training data.

## FAIR Is Not the Same as Open

A common misunderstanding is that FAIR means publicly available. It does not. FAIR requires that access conditions be clear and that metadata be public. The data themselves can be restricted.

This matters a great deal for research involving human participants, proprietary data, or information about vulnerable communities. A dataset of clinical records held in a controlled-access repository, with a public landing page that describes the variables and explains the application process, can be fully FAIR. The same dataset sitting unlabeled on a hard drive "available on request" is not FAIR even if the researcher would happily share it.

The phrase often used is "as open as possible, as closed as necessary." Chapter 19 covers how to share sensitive data in ways that respect this.

## CARE: People and Purpose

The FAIR principles focus on data as a technical object. They say nothing about who the data are about, who benefits from their use, or who gets to decide. For data involving Indigenous peoples, the Global Indigenous Data Alliance developed the CARE principles as a complement to FAIR {footcite}`carroll2020`:

**Collective benefit.** Data ecosystems should be designed so that the communities the data come from benefit from their use.

**Authority to control.** Communities have the right to govern data about themselves, their lands, and their resources.

**Responsibility.** Those working with the data have a responsibility to share how the data are used to support the communities' self-determination and benefit.

**Ethics.** The rights and wellbeing of the communities should be the primary concern at every stage of the data life cycle.

CARE was written specifically for Indigenous data sovereignty, and it should be applied as written in that context. Its questions are also useful for other community-engaged research. Consider a dataset built from property records, code violations, and resident surveys in a single city neighborhood. Publishing it openly may be FAIR. But it may also enable uses the residents never agreed to, such as speculative investment targeting or surveillance. Asking who benefits, who has a say, and what the community was told at the outset is part of responsible sharing, and those questions are best asked at the design stage, not at publication.

In AI research the stakes are higher because models trained on community data can be deployed at scale, far from the original context. A model card (Chapter 10) and a datasheet (Chapter 17) are good places to document the community agreements, intended uses, and uses the community did not consent to.

## A Five-Minute FAIR Check

Before you share any dataset, model, or software package, work through these questions. If you answer "no" to one, the chapter in parentheses explains how to fix it.

**Findable**
- Does it have a DOI or other persistent identifier, not just a URL? (Chapter 16)
- Does it have a descriptive title, keywords, and author names with ORCIDs? (Chapters 10, 17)
- Is it listed somewhere people in your field will search, such as a discipline repository, Hugging Face, or the Model Zoo? (Chapters 2, 13)

**Accessible**
- Can someone with the identifier reach it without emailing you? (Chapter 13)
- If access is restricted, does the landing page explain how to request it? (Chapter 19)
- Is the repository committed to keeping the metadata available for the long term? (Chapter 16)

**Interoperable**
- Is it in an open, widely used format? (Chapter 17)
- Are variables, units, and codes documented? (Chapter 17)
- For software and models, are dependencies recorded in a machine-readable file? (Chapter 5)

**Reusable**
- Does it have a license? (Chapter 18)
- Does its documentation explain how it was made, what it is for, and what its limitations are? (Chapters 10, 17)
- Does it follow your community's reporting standards? (Chapter 10)

### Hands-On: Read the Metadata Behind a DOI

Most of the "Findable" and "Accessible" criteria are about metadata, and for anything with a DataCite DOI (which includes Zenodo, Deep Blue Data, Dryad, and Hugging Face DOIs) that metadata is public and machine-readable. This script fetches it from the DataCite API and reports the fields that matter most for FAIR:

```python
# fair_check.py: inspect the public metadata behind a DOI
import sys
import requests

doi = sys.argv[1] if len(sys.argv) > 1 else "10.5281/zenodo.3514685"
r = requests.get(f"https://api.datacite.org/dois/{doi}", timeout=30)
r.raise_for_status()
a = r.json()["data"]["attributes"]

creators = a.get("creators", [])
with_orcid = [c for c in creators
              if any(n.get("nameIdentifierScheme") == "ORCID" for n in c.get("nameIdentifiers", []))]

checks = {
    "F  Title":                    bool(a.get("titles")),
    "F  Keywords/subjects":        bool(a.get("subjects")),
    "F  Creators with ORCID":      f"{len(with_orcid)} of {len(creators)}",
    "F  Description":              bool(a.get("descriptions")),
    "A  Landing page URL":         a.get("url"),
    "R  License (rightsList)":     [x.get("rights") for x in a.get("rightsList", [])] or False,
    "R  Linked to paper/code":     len(a.get("relatedIdentifiers", [])),
    "   Version":                  a.get("version"),
    "   Resource type":            a.get("types", {}).get("resourceTypeGeneral"),
}
print(f"DOI {doi}: {a['titles'][0]['title']}\n")
for name, value in checks.items():
    print(f"{name:28} {value}")
```

Running it on the AI-validated plant observations dataset listed in the Model Zoo gives:

```bash
python fair_check.py 10.5281/zenodo.3514685
```

```text
DOI 10.5281/zenodo.3514685: AI validated plant observations from social media: Flickr images from central London 2011-2019

F  Title                     True
F  Keywords/subjects         True
F  Creators with ORCID       1 of 9
F  Description               True
A  Landing page URL          https://zenodo.org/record/3514685
R  License (rightsList)      ['Creative Commons Attribution 1.0 Generic', 'Open Access']
R  Linked to paper/code      1
   Version                   1.1
   Resource type             Dataset
```

This is a well-described record: it has keywords, a description, a version, a license, and a link to a related work. The check also surfaces two easy improvements, which is typical of real datasets. Only one of nine creators has an ORCID attached, so the dataset may not appear automatically in the other authors' ORCID records. And the license is version 1.0 of CC BY; for new deposits, the current version, CC BY 4.0, is the usual choice (Chapter 18). Both can be fixed by publishing a new version of the record.

Run the script on your own DOIs. Anything reported as `False`, `None`, or `0` is a gap in your metadata that you can fix by editing the record in your repository.

Automated tools can also score your work. F-UJI, developed through the FAIRsFAIR project, assesses datasets by their DOI. The `howfairis` tool checks GitHub repositories against a simple software checklist. These tools are helpful as a first pass but only check what can be detected automatically, which leaves out most of the "Reusable" criteria.

## Try This

Pick a dataset you have shared, or one you use often, and run the five-minute check. Then paste its DOI into F-UJI (search "F-UJI FAIR assessment") and compare the tool's score with your own. Where do they disagree, and why?

## Further Reading

The original FAIR paper {footcite}`wilkinson2016` is short and readable. The FAIR4RS paper {footcite}`barker2022` explains the adaptations for software. The CARE principles paper {footcite}`carroll2020` and the Global Indigenous Data Alliance website provide guidance on applying CARE in practice.

## Related Chapters

- [Chapter 12: Planning for Sharing](../part3/ch12_mandates.md)
- [Chapter 17: Documenting Datasets](../part3/ch17_documenting_datasets.md)
- [Chapter 19: Sharing Sensitive and Restricted Data](../part3/ch19_sensitive_data.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
