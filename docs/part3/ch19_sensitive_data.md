# Chapter 19: Sharing Sensitive and Restricted Data

:::{admonition} What You Will Learn
:class: tip

- How to plan for sharing from the moment you design consent
- What de-identification can and cannot do, and why re-identification risk is higher than it looks
- Controlled-access options: restricted-use files, data enclaves, and gated repositories
- What synthetic data can and cannot replace
- Why models trained on sensitive data can leak it, and how to decide what to release
- What to share when the raw data cannot move
:::

:::{admonition} Get expert help
:class: warning

Sharing data about people involves legal, ethical, and institutional requirements that depend on your specific study. This chapter is an orientation, not a substitute for consulting your IRB, U-M's privacy and compliance offices, and repository curators such as ICPSR.
:::

## As Open as Possible, as Closed as Necessary

Much of the most valuable research data is also the most sensitive: health records, surveys about personal experiences, interviews, location traces, educational records, and data about small or vulnerable communities. The people in these datasets are owed protection. At the same time, funders expect data to be shared, and research built on data nobody else can check is hard to trust or build upon.

These goals are not as opposed as they seem. The FAIR principles (Chapter 3) do not require data to be public, only that access conditions be clear. Between "fully public" and "never shared" there is a range of options, and most sensitive datasets can be shared somewhere on that range. This chapter walks through them.

## Planning at Consent

The most important decisions about sharing human subjects data are made before any data are collected, in the consent form and the IRB application. If participants were told their data would be seen only by the research team, you may be unable to share it later, no matter how carefully you de-identify it.

When designing a study:

- **Include sharing language in consent forms.** Explain that de-identified data may be shared with other researchers through a repository, possibly under controlled access. The revised Common Rule allows for "broad consent" to future research use of identifiable data and specimens, under specific conditions.
- **Describe the sharing plan in the IRB application** so the IRB can review it. U-M's IRBs have template language for data sharing.
- **Consider a Certificate of Confidentiality.** NIH-funded research that collects identifiable, sensitive information is automatically covered, which protects the data from compelled disclosure in legal proceedings.
- **Talk to your target repository early.** ICPSR, for example, can advise on consent language that will make deposit possible.

## De-identification

De-identification removes or transforms information that could identify individuals. It is often the first step toward sharing, and it is required for public release of most human subjects data.

For health data covered by HIPAA, there are two recognized methods. **Safe Harbor** requires removing 18 specified types of identifiers (names, most geographic units smaller than a state, all date elements except year, phone numbers, email addresses, record numbers, device identifiers, full-face photographs, and so on) and having no actual knowledge that the remaining information could identify someone. **Expert Determination** requires a qualified expert to apply statistical methods and document that the risk of re-identification is very small. Expert Determination allows more detail to be retained (such as finer dates or geography) when justified.

Outside HIPAA, similar principles apply, but the rules are less prescriptive. The risk is often underestimated.

**Re-identification risk is higher than intuition suggests.** Combinations of ordinary attributes can be surprisingly unique. Researchers have shown that 99.98% of Americans could be correctly re-identified in any dataset using 15 demographic attributes {footcite}`rocher2019`. Removing names and ID numbers is not enough.

Particular risks for AI research data include:

- **Small populations or rare categories.** A dataset about a small town, a rare disease, or a small community can identify people through combinations of a few attributes.
- **Location data.** Home and work locations, or even a handful of location points, can uniquely identify most people.
- **Geospatial and image data.** Street-level imagery, satellite imagery of residential areas, and property records can identify households even without names.
- **Free text.** Interview transcripts, clinical notes, and social media posts contain names, places, and details that are hard to remove automatically.
- **Linked data.** A de-identified dataset may be re-identifiable when combined with public data such as voter rolls, property records, or social media.

Techniques to reduce risk include coarsening (reporting age ranges instead of ages, counties instead of addresses), suppressing rare categories, adding noise, and top-coding extreme values. ICPSR and other curated repositories perform disclosure risk review as part of deposit.

### Hands-On: Measure How Identifiable Your Records Are

A simple and widely used measure is **k-anonymity**. Choose the **quasi-identifiers**: attributes that are not names or IDs but could be linked to outside data, such as age, sex, and ZIP code. Group the records by those attributes. The size of the smallest group is *k*: every person in the data is indistinguishable from at least *k* − 1 others on those attributes. A record in a group of size 1 is unique, and potentially identifiable by anyone who knows those few facts about the person.

This script measures *k* on a synthetic survey of 2,000 people, then shows the effect of generalizing ages to ten-year bands (with everyone 80 and over top-coded into one band), shortening ZIP codes to three digits, and finally suppressing the few records that are still in small groups:

```python
# scripts/check_k_anonymity.py
import pandas as pd

def k_report(df, quasi_identifiers):
    """Size of the smallest group of people who share the same quasi-identifier values."""
    groups = df.groupby(quasi_identifiers, observed=True).size()
    return {"k": int(groups.min()),
            "records in groups smaller than 5": int(groups[groups < 5].sum()),
            "unique records": int((groups == 1).sum())}

df = pd.read_csv("survey.csv", dtype={"zip": str})
qi = ["age", "sex", "zip"]
print("original:   ", k_report(df, qi))

# Generalize: 10-year age bands, 3-digit ZIP prefixes, and top-code ages 80+
safe = df.copy()
safe["age"] = pd.cut(safe["age"].clip(upper=80), bins=range(10, 91, 10), right=False,
                     labels=[f"{a}-{a+9}" for a in range(10, 81, 10)]).astype(str)
safe.loc[df["age"] >= 80, "age"] = "80+"
safe["zip"] = safe["zip"].str[:3]
print("generalized:", k_report(safe, qi))

# Suppress whatever is still in groups smaller than k=5
sizes = safe.groupby(qi, observed=True)["age"].transform("size")
safe.loc[sizes < 5, qi] = "suppressed"
print("suppressed: ", k_report(safe[sizes >= 5], qi), f"({(sizes < 5).sum()} record(s) suppressed)")
```

```text
original:    {'k': 1, 'records in groups smaller than 5': 2000, 'unique records': 1801}
generalized: {'k': 1, 'records in groups smaller than 5': 1, 'unique records': 1}
suppressed:  {'k': 10, 'records in groups smaller than 5': 0, 'unique records': 0} (1 record(s) suppressed)
```

With exact age, sex, and five-digit ZIP code, 1,801 of the 2,000 people are unique: a dataset with no names at all is close to fully identifiable. Generalizing two columns brings that down to a single unique record, and suppressing that one record gives *k* = 10. The price is lost detail, so choose generalizations that keep what your analysis needs.

Treat this as a first check, not a guarantee. *k*-anonymity depends on choosing the right quasi-identifiers, and it does not protect against inferring a sensitive attribute when everyone in a group shares it. A thorough disclosure review by ICPSR or a statistical disclosure expert is still needed for public release of sensitive data. The same small-group logic applies to published tables: suppress or combine cells that count fewer than a threshold of people (often 5 or 10, depending on the data and the data provider's rules).

## Controlled Access

When data cannot be made safely public even after de-identification, controlled access lets qualified researchers use them under agreed conditions. Options, from least to most restrictive:

**Gated repositories.** Hugging Face gated repositories (Chapter 14) and Zenodo restricted records let users request access, agree to terms, and be approved. These are suitable for low-to-moderate risk data, such as data with licensing restrictions or research-only terms. They do not verify identities rigorously or enforce security requirements.

**Restricted-use data agreements.** Repositories such as ICPSR offer restricted-use files that are available only to researchers who submit an application, obtain IRB approval, and sign a data use agreement specifying security measures and prohibiting re-identification attempts. Access is granted to a named researcher at an institution that takes responsibility.

**Data enclaves.** For the most sensitive data, researchers work in a secure remote environment, such as ICPSR's Virtual Data Enclave, and cannot download the data. Outputs are reviewed before release to ensure they do not disclose individual information.

**Domain repositories with controlled access.** NIH's dbGaP and similar resources manage access to genomic and phenotypic data through a formal data access committee. NIH now expects researchers and institutions using its controlled-access data to meet specified security standards.

**At U-M**, sensitive data for analysis should be stored and processed only on systems approved for that data type. U-M's Sensitive Data Guide lists which services are approved for which categories of data. Armis2, U-M's HPC cluster for sensitive data, is designed for work involving protected health information and similar data, and should be used instead of Great Lakes for such analyses.

## Synthetic Data

Synthetic data are artificial records generated to mimic the statistical properties of a real dataset. They are increasingly proposed as a way to share the "shape" of sensitive data without sharing real records. Tools such as `synthpop` (R) and the Synthetic Data Vault (Python) generate synthetic tabular data, and generative models can produce synthetic images and text.

Synthetic data are useful for:

- **Developing and testing code** so others can run your pipeline end to end (Chapters 9 and 11).
- **Teaching and demonstrations.**
- **Exploratory analysis** before applying for access to the real data.

They are much less reliable for:

- **Reproducing specific findings.** Synthetic data preserve the relationships the generator was designed or able to capture. Complex interactions, rare subgroups, and outliers are often lost or distorted, and results can differ from the real data.
- **Guaranteeing privacy.** A generator trained on real data can memorize and reproduce real records, especially unusual ones. Synthetic data are not automatically private. Formal privacy guarantees require techniques such as differential privacy, which add noise and reduce fidelity.

Generating a first synthetic version of a table takes a few lines. In R, the `synthpop` package is widely used in the social sciences:

```r
library(synthpop)
real <- read.csv("survey_deidentified.csv")
syn_obj <- syn(real, seed = 2026)          # fits a sequence of models, one per column
compare(syn_obj, real)                      # side-by-side distributions
write.syn(syn_obj, filename = "survey_synthetic", filetype = "csv")
```

In Python, the Synthetic Data Vault (SDV) offers similar tools. Its interface changed between major versions; this example uses SDV 2.x, where data are passed as a dictionary of named tables:

```python
import pandas as pd
from sdv.metadata import Metadata
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.evaluation import evaluate_quality

real = {"survey": pd.read_csv("survey_deidentified.csv", dtype={"zip": str})}
metadata = Metadata.detect_from_dataframes(real)       # review and correct column types
synth = GaussianCopulaSynthesizer(metadata)
synth.fit(real)
synthetic = synth.sample(num_rows=len(real["survey"]))

evaluate_quality(real, synthetic, metadata)            # prints how well distributions match
fake = synthetic["survey"] if isinstance(synthetic, dict) else synthetic
print("exact copies of real rows:", len(real["survey"].merge(fake, how="inner")))
```

On the synthetic survey used above, this reports an overall quality score of about 97% and no exact copies of real rows. Pin the SDV version in your lockfile (Chapter 5), since code written for one major version may not run on the next.

Neither tool provides a formal privacy guarantee by default. Run the *k*-anonymity check above on the synthetic output too, and check that no synthetic row exactly matches a real one.

A good practice is to release synthetic data clearly labeled as such (Chapter 17), alongside a description of how it was generated and evaluated, and to state that substantive findings should be verified on the real data through controlled access.

## Sharing Models Trained on Sensitive Data

A trained model is not the same as its training data, but it is not fully separate either. Machine learning models can leak information about the data they were trained on.

**Membership inference.** Given a model and a record, an attacker can often infer whether that record was in the training set, by exploiting differences in how the model behaves on data it has seen {footcite}`shokri2017`. For a model trained on patients with a particular condition, this could reveal that a specific person has that condition.

**Training data extraction.** Large generative models can memorize and reproduce verbatim sequences from their training data, including personal information, when prompted appropriately {footcite}`carlini2021`.

These risks are larger for models that are overfit, trained on small datasets, or trained with many parameters relative to the data. They also apply to fine-tuned language models: fine-tuning on clinical notes or interview transcripts can make that text extractable.

### Hands-On: A Quick Leakage Warning Sign

A simple first check for membership inference risk compares how confident a model is on its own training records with how confident it is on records it has never seen. If an attacker can tell the two apart from the model's outputs alone, membership leaks. This example measures that with an AUC score, where 0.5 means no signal:

```python
# A quick warning sign for training-data leakage: does the model treat
# its own training records very differently from unseen records?
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
X_in, X_out, y_in, y_out = train_test_split(X, y, test_size=0.5, random_state=0, stratify=y)

def confidence_in_true_label(model, X, y):
    return model.predict_proba(X)[np.arange(len(y)), y]

def membership_signal(model):
    """AUC of guessing 'was in training data' from the model's confidence.
    0.5 = no signal; closer to 1.0 = members are easy to tell apart."""
    conf_in = confidence_in_true_label(model, X_in, y_in)
    conf_out = confidence_in_true_label(model, X_out, y_out)
    labels = np.r_[np.ones(len(conf_in)), np.zeros(len(conf_out))]
    return roc_auc_score(labels, np.r_[conf_in, conf_out])

models = {
    "random forest, fully grown": RandomForestClassifier(n_estimators=200, random_state=0),
    "regularized logistic regression": make_pipeline(StandardScaler(), LogisticRegression(C=0.1)),
}
for name, model in models.items():
    model.fit(X_in, y_in)
    gap = model.score(X_in, y_in) - model.score(X_out, y_out)
    print(f"{name:32} train-test accuracy gap = {gap:.3f}   membership AUC = {membership_signal(model):.2f}")
```

```text
random forest, fully grown       train-test accuracy gap = 0.053   membership AUC = 0.59
regularized logistic regression  train-test accuracy gap = 0.003   membership AUC = 0.51
```

The fully grown random forest fits its training data almost perfectly, and its confidence gives away some membership information (AUC 0.59). The regularized model generalizes almost equally well to new data and leaks essentially nothing by this measure. This is a crude test: real attacks are stronger, so a low score is not proof of safety. But a high score is a clear warning not to release the model openly without further review. Running it costs nothing, and you can report the result in the model card (Chapter 10).

When deciding what to release, consider these options:

- **Release the weights publicly** if the risk is low: large training sets, well-generalized models, data already de-identified, and no generative capacity that could reproduce records.
- **Release weights under controlled access**, with the same conditions as the underlying data.
- **Provide access through an API or demo** without releasing weights, which limits some attacks (though not all).
- **Train with privacy protections**, such as differentially private training, which provides formal guarantees at some cost in accuracy.
- **Release nothing but code and documentation**, so others with authorized access to the data can retrain the model.

Document your decision and reasoning in the model card (Chapter 10) and your data management and sharing plan (Chapter 12).

## Sharing What You Can

Even when neither data nor model can be shared, you can usually share a great deal that supports reproducibility:

- **All code**, including data processing, training, and evaluation.
- **A schema or data dictionary**, so others understand the variables (Chapter 17).
- **Synthetic or mock data** with the same structure, so the code runs.
- **Aggregate statistics and summary tables** that pass disclosure review.
- **Detailed documentation** of the data collection and access process, so others can apply for the same data.
- **Model evaluation outputs**, such as confusion matrices and performance by subgroup.

This combination lets reviewers and other researchers check your methods, run your pipeline, and replicate your study with their own data, even if they cannot reproduce your exact numbers.

## Try This

For a study you are planning or running that involves human participants, check the consent form and IRB application for language about data sharing. If there is none, consider whether an amendment is appropriate. Then list the attributes in your dataset and identify which combinations might make an individual unique. Use this to draft a de-identification plan, and take it to your IRB or ICPSR for feedback.

## Further Reading

The HHS guidance on HIPAA de-identification explains Safe Harbor and Expert Determination in detail. ICPSR's guides for data depositors cover disclosure risk and restricted-use options. For model privacy risks, the membership inference {footcite}`shokri2017` and training data extraction {footcite}`carlini2021` papers are the key references. U-M's Safe Computing website hosts the Sensitive Data Guide.

## Related Chapters

- [Chapter 3: FAIR, FAIR4RS, and CARE](../part1/ch03_fair_principles.md)
- [Chapter 12: Planning for Sharing](ch12_mandates.md)
- [Chapter 16: Institutional and Archival Repositories](ch16_archival_repositories.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
