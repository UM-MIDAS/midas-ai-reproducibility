# Chapter 12: Planning for Sharing: Funder Mandates and Data Management Plans

:::{admonition} What You Will Learn
:class: tip

- What U.S. federal funders currently require for sharing publications and data
- What journals and conferences expect in data and code availability statements
- How to write a data management and sharing plan you can actually follow
- How to budget time and money for sharing
- Where trained models and code fit into sharing plans
:::

:::{admonition} Check current requirements
:class: warning

Funder policies changed substantially in 2025 and 2026 and continue to evolve. This chapter reflects policies as of September 2026. Always check the current funding opportunity and your agency's policy pages, and consult U-M's Office of Research and Sponsored Projects (ORSP) and the U-M Library before submitting.
:::

## Sharing Is No Longer Optional

For a long time, data sharing was encouraged but rarely enforced. A paper might say "data available on request," and nobody checked. That era is over for federally funded research in the United States. Over the past few years, federal agencies have moved to require that publications be freely available immediately on publication and that the data underlying them be shared. Funders are also asking for written plans at the proposal stage, and for reports on whether those plans were followed.

"Available on request" has a poor track record. When researchers systematically requested data and code from authors of computational papers in *Science*, a journal that already had a sharing policy, they obtained materials for fewer than half of the articles {footcite}`stodden2018`. Requests go to old email addresses, students graduate, and hard drives fail. Mandates are, in part, a response to this.

The good news is that the practices in this handbook, such as depositing data in a repository with a DOI, documenting it well, and choosing a license, are the same practices that satisfy funders. If you plan for them from the start, compliance is mostly a matter of writing down what you were going to do anyway.

## The Federal Policy Landscape

### The 2022 OSTP Memo

In August 2022, the White House Office of Science and Technology Policy (OSTP) directed all federal agencies to update their public access policies. The memo, "Ensuring Free, Immediate, and Equitable Access to Federally Funded Research," asked agencies to make peer-reviewed publications from federally funded research freely available at the time of publication, with no embargo, and to make the scientific data underlying those publications available at the same time, subject to legal, privacy, and security limits. Agencies were given until the end of 2025 to have their policies in effect. Most agencies' updated policies now apply.

### NIH

NIH has two separate policies that together cover publications and data.

The **NIH Public Access Policy**, revised to align with the OSTP memo, took effect on July 1, 2025. It requires that author-accepted manuscripts from NIH-funded research be submitted to PubMed Central and made publicly available without embargo on the official date of publication.

The **NIH Data Management and Sharing (DMS) Policy** has applied since January 2023 to all NIH-funded research that generates scientific data. It requires a Data Management and Sharing Plan with the application, and expects data to be shared no later than the time of an associated publication or the end of the award period, whichever comes first. Data should go to an established repository, and NIH encourages researchers to maximize appropriate sharing.

In 2026, NIH updated how DMS Plans are submitted and reported (notice NOT-OD-26-100). Competing applications submitted on or after May 25, 2026 must use a new, standardized DMS Plan format. Beginning October 1, 2026, investigators no longer need prior approval to modify an approved DMS Plan; instead, they report changes and sharing progress in the annual progress report (RPPR). NIH described this as an administrative update, not a policy change: the expectation to share remains.

Some NIH programs have additional requirements, such as the Genomic Data Sharing Policy for large-scale genomic data, which typically requires deposit in controlled-access repositories like dbGaP.

### NSF

NSF has long required a two-page data management plan with every proposal, with directorate-specific guidance on what to include. Under the Proposal and Award Policies and Procedures Guide (PAPPG) 24-1, Supplement 2, effective January 22, 2026, NSF eliminated its 12-month publication embargo: author-accepted manuscripts must be deposited in the NSF Public Access Repository (NSF-PAR) at the time of publication. Check your directorate's guidance for current expectations about the data management and sharing plan.

### The 2025 "Gold Standard Science" Executive Order

In May 2025, Executive Order 14303, "Restoring Gold Standard Science," set out principles for federal science including that it be reproducible, transparent, and communicative of error and uncertainty. It directs agencies to make publicly available the data, analyses, and model code behind scientific information that substantially affects public policy. The order applies directly to federal agencies, but its principles flow downstream through funding announcements and reporting requirements. Researchers whose work informs policy should expect increasing attention to whether analyses, including AI models, can be reproduced.

### Other Funders

Private foundations increasingly have their own requirements, often stricter than federal ones. Some require open licenses (such as CC BY) for publications and data, some require code sharing, and some fund data curation directly. Read the grant agreement carefully, since foundation requirements are usually contractual. If your project is funded by a private foundation, check with the program officer whether the foundation has specific expectations for sharing models and code.

## Journal and Conference Requirements

Most major journals now require a **data availability statement** and many require a **code availability statement**. These say where the data and code can be found, under what conditions, and why if anything cannot be shared. Some journals, including those in the Nature and PLOS families, have detailed policies on what counts as acceptable. A bare GitHub link or "available on request" is increasingly rejected in favor of a repository DOI.

ML conferences have their own expectations. NeurIPS requires a paper checklist covering reproducibility (Chapter 10), and its Evaluations and Datasets track requires datasets to be hosted on a platform that provides machine-readable Croissant metadata, including responsible AI information (Chapter 17).

A good availability statement is specific:

> The data supporting this study are available in Deep Blue Data at https://doi.org/10.7302/xxxx under a CC BY 4.0 license. Code to reproduce all analyses is archived at https://doi.org/10.5281/zenodo.xxxx (version 1.1) and developed at https://github.com/your-lab/project. Trained model weights are available at https://huggingface.co/your-lab/model (revision v1.1). Participant-level survey responses cannot be shared publicly under the terms of IRB approval HUMxxxx; a de-identified extract is available to qualified researchers through ICPSR under a restricted-use agreement.

## Writing a Plan You Can Follow

A data management and sharing plan is a promise. With NIH's new reporting through the RPPR, you will be asked each year whether you are keeping it. Write a plan that describes what you will realistically do, not an aspirational one.

Most templates ask about the same core elements:

**Data types.** What data will you generate or collect? Include the expected volume and format. For AI projects, list trained models, code, and derived data (such as embeddings or labels) as well as raw data.

**Related tools, software, and code.** What is needed to use the data? This is where you describe your code, environment files, and containers (Chapters 5 and 6), and how they will be shared.

**Standards.** What metadata standards, formats, and documentation will you use? Mention datasheets and model cards (Chapters 10 and 17) and any community standards in your field.

**Preservation, access, and timelines.** Which repository or repositories, when data will be shared, and for how long. Name specific repositories. "Deep Blue Data" is better than "an appropriate repository."

**Access, distribution, and reuse considerations.** Any limits on sharing due to privacy, consent, intellectual property, or tribal sovereignty, and how you will handle them (Chapter 19). The license you will use (Chapter 18).

**Oversight.** Who is responsible for making sure the plan is followed. Name a role, such as "the PI, with support from the lab data manager," not just "the team."

The **DMPTool** (dmptool.org) is a free service with templates for NIH, NSF, and many other funders, and example plans. The U-M Library's research data services team can review drafts, and ICPSR can advise on social and behavioral science data. It is much easier to get this help before submission than to fix a plan after an award.

### Hands-On: Keep a Sharing Inventory

With NIH now asking for sharing progress in annual reports, it helps to keep a small machine-readable inventory of every research output and where it lives. Keep it in the project repository and update it as things are shared:

```yaml
# sharing_inventory.yaml: every research output and where it is shared
project: Roof condition assessment from street-level imagery
outputs:
  - name: Street-level image dataset (de-identified)
    type: data
    repository: Deep Blue Data
    doi: 10.7302/xxxx-xxxx
    license: CC BY 4.0
    status: shared
  - name: Analysis and training code
    type: code
    repository: Zenodo (GitHub release v1.1)
    doi: 10.5281/zenodo.0000000
    license: MIT
    status: shared
  - name: Trained classifier weights
    type: model
    repository: Hugging Face (revision v1.1)
    url: https://huggingface.co/your-lab/roof-condition-classifier
    license: Apache-2.0
    status: shared
  - name: Resident survey responses
    type: data
    repository: ICPSR (restricted use)
    license: Data use agreement
    status: in curation
    note: Participant-level responses cannot be shared publicly under IRB HUM00000000.
```

A few lines of Python then turn the inventory into a first draft of the availability statement for a paper, and a status list for progress reports:

```python
# scripts/availability_statement.py
import yaml

inv = yaml.safe_load(open("sharing_inventory.yaml"))

def where(o):
    link = f"https://doi.org/{o['doi']}" if o.get("doi") else o.get("url", "[link pending]")
    return f"{o['name']}: available from {o['repository']} at {link} ({o['license']})."

print("DATA AND CODE AVAILABILITY\n")
for o in inv["outputs"]:
    print(where(o) + (f" {o['note']}" if o.get("note") else ""))

print("\nSHARING STATUS (for progress reports)\n")
for o in inv["outputs"]:
    flag = "OK  " if o["status"] == "shared" and (o.get("doi") or o.get("url")) else "TODO"
    print(f"{flag} [{o['type']:5}] {o['name']}: {o['status']}")
```

```text
DATA AND CODE AVAILABILITY

Street-level image dataset (de-identified): available from Deep Blue Data at https://doi.org/10.7302/xxxx-xxxx (CC BY 4.0).
Analysis and training code: available from Zenodo (GitHub release v1.1) at https://doi.org/10.5281/zenodo.0000000 (MIT).
Trained classifier weights: available from Hugging Face (revision v1.1) at https://huggingface.co/your-lab/roof-condition-classifier (Apache-2.0).
Resident survey responses: available from ICPSR (restricted use) at [link pending] (Data use agreement). Participant-level responses cannot be shared publicly under IRB HUM00000000.

SHARING STATUS (for progress reports)

OK   [data ] Street-level image dataset (de-identified): shared
OK   [code ] Analysis and training code: shared
OK   [model] Trained classifier weights: shared
TODO [data ] Resident survey responses: in curation
```

The generated text is a starting point to edit, not final prose. Its real value is that the statement, the progress report, and the plan all come from the same source, so they cannot drift apart. The same inventory feeds the health checks in Chapter 20.

## Budgeting for Sharing

Sharing takes time and sometimes money. Most federal funders, including NIH, allow reasonable costs for data management and sharing to be included in the budget. These can include:

- Staff time for data curation, documentation, and de-identification.
- Repository fees (many repositories, including Deep Blue Data and Zenodo, are free to deposit; some discipline repositories and ICPSR services have costs).
- Storage during the project.
- Compute for building containers or hosting demos.

Budget realistically. A rule of thumb from experienced data managers is that preparing a dataset for sharing takes longer than people expect, often days or weeks of effort for a complex dataset, especially if it requires de-identification. That time is much easier to find if it is in the budget and the timeline.

## Models Are Research Outputs Too

Funder policies were mostly written with "data" in mind, and the word can be ambiguous for AI research. Are trained model weights data? Is code? Different agencies and program officers may answer differently. The safest approach is to treat all of them as research outputs and address each in your plan:

- **Raw and processed data**: where deposited, under what access conditions.
- **Code**: archived with a DOI (Zenodo), developed on GitHub.
- **Trained models**: weights deposited with a model card, on Hugging Face and/or an archival repository.
- **Derived artifacts**: such as generated labels, embeddings, or LLM outputs used as data (Chapter 7).

Being explicit about models also protects you: if a model cannot be shared because it was trained on restricted data and might leak it (Chapter 19), say so in the plan and describe what you will share instead.

## U-M Support

The **U-M Library** offers research data services, including DMP review, guidance on repositories, and the Deep Blue Data repository itself. **ICPSR**, based at U-M, offers data curation and restricted-data services, particularly for social and behavioral science. **ORSP** can advise on sponsor requirements. **MIDAS** can advise on sharing AI models and on listing resources in the Model Zoo. Chapter 26 has contact details.

## Try This

Take the data management plan from your most recent proposal. For each promise it makes, check whether it has actually happened or is on track. Then rewrite the plan's repository section to name specific repositories for each type of output (data, code, models), using Chapter 13 to choose them.

## Further Reading

SPARC maintains an up-to-date tracker of U.S. federal public access policies. NIH's Scientific Data Sharing website has the current DMS Policy, plan format, and FAQs. The DMPTool has templates and public example plans.

## Related Chapters

- [Chapter 13: Choosing Where to Share](ch13_where_to_share.md)
- [Chapter 16: Institutional and Archival Repositories](ch16_archival_repositories.md)
- [Chapter 19: Sharing Sensitive and Restricted Data](ch19_sensitive_data.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
