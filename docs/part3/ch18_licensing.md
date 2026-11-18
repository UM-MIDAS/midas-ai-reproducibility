# Chapter 18: Licensing Data, Code, and Models

:::{admonition} What You Will Learn
:class: tip

- Why every shared artifact needs a license
- How to choose licenses for code, data, and model weights
- What open, responsible-AI, and custom model licenses allow
- How upstream licenses on data and base models constrain what you can share
- Where to get help at U-M
:::

:::{admonition} Not legal advice
:class: warning

This chapter explains common licensing options and considerations for researchers. It is not legal advice. For questions about specific situations, especially involving commercial potential, third-party data, or contracts, contact the U-M Library Copyright Office or U-M Innovation Partnerships.
:::

## Why a License Is Required

Many researchers assume that posting something publicly means others can use it. Legally, the opposite is usually true. Under copyright law, creative works, including code and documentation and sometimes datasets, are automatically protected. Without a license granting permission, others technically cannot copy, modify, or redistribute your work, even if it is on a public GitHub page. Careful users, especially companies and other universities, will avoid unlicensed work entirely.

A license is a short statement that grants permissions in advance, so users do not need to ask. Choosing one is one of the simplest things you can do to make your work reusable, and it is a requirement for the "Listed" tier of the Model Zoo.

A large audit of AI datasets on popular hosting sites found that licenses were frequently missing or wrong: more than 70% of datasets lacked license information, and among those with licenses, many were miscategorized relative to the original source's terms {footcite}`longpre2024`. This creates real uncertainty for anyone building on those datasets. You can avoid adding to the problem by choosing licenses deliberately and documenting where your data came from.

## Code Licenses

For research code, three families of open source licenses cover most needs.

**Permissive licenses** (MIT, BSD, Apache 2.0) allow anyone to use, modify, and redistribute your code, including in commercial and closed-source products, as long as they keep your copyright notice. **MIT** is short and very widely used. **Apache 2.0** is slightly longer and adds an explicit patent license and protection against patent litigation, which makes it attractive for larger projects and for companies. Permissive licenses maximize reuse.

**Copyleft licenses** (GPL, LGPL, AGPL) allow the same uses but require that anyone who distributes modified versions release them under the same license. This keeps derivatives open. The trade-off is that some organizations avoid copyleft code, and combining GPL code with other licenses can be complicated.

**No license** means, as above, that nobody can legally reuse the code. Avoid this.

For most research code, MIT or Apache 2.0 is a sensible default. Add a `LICENSE` file to the root of your repository; GitHub offers templates when you create a repository, and choosealicense.com explains the options in plain language.

It is also good practice to put a one-line SPDX license identifier at the top of each source file. SPDX identifiers are standard short names that tools can read automatically, and they keep the license attached to a file even when someone copies it out of your repository:

```python
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Jane Doe, University of Michigan
```

### Hands-On: Check Your Dependencies' Licenses

Your code's license must be compatible with the libraries it depends on, especially if you plan to distribute a container image (Chapter 6) that bundles them. The `pip-licenses` tool lists the license of every installed package:

```bash
pip install pip-licenses
pip-licenses --format=markdown --order=license        # everything in the environment
pip-licenses --packages pandas scikit-learn numpy     # just these
```

```text
| Name         | Version | License                                            |
|--------------|---------|----------------------------------------------------|
| numpy        | 2.5.3   | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| pandas       | 3.0.5   | BSD License                                        |
| scikit-learn | 1.9.1   | BSD-3-Clause                                       |
```

Most of the scientific Python stack uses permissive licenses. Look out for GPL-licensed packages if you plan a permissive release of a bundled application, and for packages with no license listed. In R, `sessioninfo::package_info()` reports package sources, and each package's `DESCRIPTION` file lists its license.

**At U-M**, software created by university employees in the course of their work may be subject to the university's intellectual property policies, and U-M Innovation Partnerships handles open source licensing questions. For typical research code with no commercial plans, open source release is common and supported, but if your code might have commercial value, or if the work is under an industry contract, talk to Innovation Partnerships before releasing it.

## Data Licenses

Data licensing is more complicated than code licensing because copyright applies unevenly to data. In the United States, facts themselves are not copyrightable, but the selection and arrangement of a database, and creative content within it (text, images, recordings), can be. Other jurisdictions, including the European Union, have additional database rights. A license clarifies your intentions regardless of these complexities.

The most common choices for research data are:

**CC0 (public domain dedication).** You waive all rights to the extent possible. Anyone can use the data for any purpose without attribution. This maximizes reuse and avoids "attribution stacking," where a dataset combining many CC BY sources must credit every one. Many data repositories and scientific communities recommend CC0 for data, relying on scholarly norms, rather than legal requirements, to ensure citation.

**CC BY 4.0 (attribution).** Anyone can use the data for any purpose, as long as they credit you. This is common for research data and is required by some funders.

**CC BY-SA (attribution, share-alike).** Derivatives must be released under the same license. This can complicate combining your data with other sources.

**CC BY-NC (non-commercial).** Prohibits commercial use. This sounds attractive but causes practical problems: "commercial" is ambiguous (is a startup's research commercial? a university lab funded by a company?), and it prevents inclusion in many open datasets and repositories. Use it only if you have a specific reason.

**Open Data Commons licenses** (ODC-By, ODbL) were written specifically for databases and are used by some large open data projects.

Creative Commons licenses are designed for creative works and data, not for software. Use a software license for code and a CC or ODC license for data.

## Model Licenses

Trained model weights are a new kind of artifact, and their legal status is not fully settled. Whether weights are copyrightable at all is an open question in many jurisdictions. In practice, model developers attach licenses to set clear terms, and users treat those terms as binding. Several types are in common use.

**Standard open source licenses** (Apache 2.0, MIT) applied to weights. These are simple and permissive, and many research models use them.

**Responsible AI Licenses (RAIL / OpenRAIL).** These permit broad use and redistribution but include use-based restrictions, such as prohibiting use for certain harmful purposes, that must be passed along to anyone who receives the model or a derivative {footcite}`contractor2022`. The "Open" variants allow free redistribution; "-M" versions apply to the model. They are used for many image generation and language models.

**Custom community licenses.** Several major open-weight model families use their own licenses with specific conditions, such as acceptable use policies, attribution requirements, naming requirements for derivatives, or thresholds above which large commercial users need a separate agreement. These are not open source licenses in the traditional sense.

When choosing a license for your own model, consider:

**What did you build on?** If you fine-tuned a base model, its license governs what you can do with your fine-tuned version. Many custom licenses require that derivatives carry the same terms. Read the base model's license before you start fine-tuning, not after.

**What was it trained on?** The training data's license and terms may limit sharing the model. If you trained on data licensed for non-commercial research only, releasing the model under a permissive license may be inappropriate. If the data were sensitive, the model may need restricted access (Chapter 19).

**What risks do you want to address?** If your model could be misused in foreseeable ways, a RAIL license lets you state restrictions. Keep in mind that license restrictions are hard to enforce and do not replace thoughtful decisions about whether and how to release.

Document the license in the model card's metadata (Chapter 10) and in a `LICENSE` file in the repository. If the code and weights have different licenses, say so clearly.

Before you fine-tune, look up the base model's license programmatically and record it alongside your training config, so the decision is documented:

```python
from huggingface_hub import HfApi
info = HfApi().model_info("your-org/base-model", revision="main")
print(info.card_data.get("license"), info.card_data.get("license_name"), info.card_data.get("license_link"))
```

Custom licenses usually appear as `license: other` with a `license_name` and `license_link`. When you see `other`, follow the link and read the terms before going further.

## Scraped and Third-Party Data

AI research often uses data the researcher did not create: web pages, social media posts, images, public records, or datasets released by others. Before you share a dataset built from such sources, or a model trained on them, ask:

**What were the terms of the source?** Websites and platforms have terms of service that may prohibit scraping or redistribution. Existing datasets have licenses that may restrict derivatives or commercial use. You cannot grant users more rights than you received.

**Is the content copyrighted?** Text, images, and recordings are usually copyrighted by their creators. Using them for research may be permissible under fair use in the United States, but redistributing the content itself is a different question.

**Does it contain personal information?** Even public posts can contain personal data, and redistribution may raise privacy concerns or conflict with platform rules (Chapter 19).

When you cannot redistribute the content itself, you can often share:

- **Identifiers and pointers**, such as post IDs or URLs, with code to rehydrate the dataset from the original source. This respects the source's terms, though content may disappear over time.
- **Derived data**, such as extracted features, labels, or aggregate statistics.
- **The collection and processing code**, so others can build their own version.

Record the source and license of every component in your datasheet (Chapter 17). This provenance record is what allows others to determine whether they can use your work.

### Hands-On: Flag License Constraints in Your Sources

Keep a simple table of every external component, then let a script flag the ones that limit what you can release:

```text
component,kind,source,license
Street-level images (city open data),data,City open data portal,CC BY 4.0
Building footprints,data,OpenStreetMap,ODbL 1.0
Photo labels from a prior study,data,Zenodo record,CC BY-NC 4.0
Pretrained image backbone,model,Hugging Face Hub,Apache-2.0
Tile download helper,code,GitHub repository,unknown
Vision-language labeling model,model,Model provider,Custom terms of use
```

```python
# scripts/check_provenance.py: flag license constraints across everything you built on
import re
import pandas as pd

sources = pd.read_csv("sources.csv")   # columns: component, kind, source, license

RESTRICTIONS = {   # regular expression -> what it means for your release
    r"\bNC\b":   "non-commercial only: your release cannot be more permissive",
    r"\bND\b":   "no derivatives: you may not be able to share modified versions",
    r"\bSA\b":   "share-alike: derivatives must use the same license",
    r"ODbL":     "share-alike for databases: derived databases must stay under ODbL",
    r"GPL":      "copyleft: distributed derivatives must be GPL-compatible",
    r"unknown":  "no license found: ask the source before redistributing",
    r"terms":    "custom terms: read them and record what they require",
}
for _, row in sources.iterrows():
    hits = [msg for pattern, msg in RESTRICTIONS.items()
            if re.search(pattern, row["license"], flags=re.IGNORECASE)]
    print(f"{'CHECK' if hits else 'ok   '} {row['component']:38} {row['license']:20} {'; '.join(hits)}")
```

```text
ok    Street-level images (city open data)   CC BY 4.0            
CHECK Building footprints                    ODbL 1.0             share-alike for databases: derived databases must stay under ODbL
CHECK Photo labels from a prior study        CC BY-NC 4.0         non-commercial only: your release cannot be more permissive
ok    Pretrained image backbone              Apache-2.0           
CHECK Tile download helper                   unknown              no license found: ask the source before redistributing
CHECK Vision-language labeling model         Custom terms of use  custom terms: read them and record what they require
```

In this example, the non-commercial labels mean the combined dataset cannot be released under CC BY or CC0, the OpenStreetMap footprints carry their own share-alike obligations, and two components need follow-up before anything is shared. A script cannot interpret licenses for you, but it makes sure no component slips through unexamined. The `sources.csv` file then goes into the datasheet as the provenance record.

## A License Decision Flow

For a typical research release:

1. **Code** you wrote: MIT or Apache 2.0, unless you have a reason for copyleft or commercial considerations (talk to Innovation Partnerships).
2. **Data** you collected, with no third-party restrictions or privacy concerns: CC0 or CC BY 4.0. Check whether your funder requires a specific license.
3. **Data derived from third-party sources**: the most restrictive of the source licenses, or pointers only if redistribution is not allowed.
4. **Model weights** trained from scratch on data you can share: Apache 2.0 or MIT, or an OpenRAIL license if you want to state use restrictions.
5. **Model weights** fine-tuned from a base model: follow the base model's license terms, then consider the training data.
6. **Anything involving sensitive data, contracts, or commercial potential**: ask before releasing.

## Try This

List every component of one of your projects: code, raw data, processed data, model weights, documentation, and any base models or third-party datasets you used. For each, note its current license (or "none") and the license of anything it was derived from. Identify any components that are missing a license or that may be released under terms more permissive than their sources allow.

## Further Reading

choosealicense.com explains code licenses in plain language. The Creative Commons website explains each CC license. The Longpre et al. audit {footcite}`longpre2024` and its accompanying Data Provenance Initiative tools help trace the licenses of popular AI datasets. The U-M Library Copyright Office offers consultations on copyright and data licensing.

## In the Model Zoo

Every Model Zoo entry should state a license. Entries without one cannot be listed.

## Related Chapters

- [Chapter 14: Sharing on Hugging Face](ch14_hugging_face.md)
- [Chapter 17: Documenting Datasets](ch17_documenting_datasets.md)
- [Chapter 19: Sharing Sensitive and Restricted Data](ch19_sensitive_data.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
