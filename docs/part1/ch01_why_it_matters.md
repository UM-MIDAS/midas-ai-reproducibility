# Chapter 1: Why Reproducibility and Accessibility Matter

:::{admonition} What You Will Learn
:class: tip

- What reproducible, replicable, and generalizable mean, and why the distinction matters for AI research
- The most common ways machine learning research fails to reproduce
- What "accessible" means in this handbook: open, runnable on modest hardware, and usable by people with disabilities
- How this handbook relates to the MIDAS AI in Research Handbook and the MIDAS Model Zoo
:::

## The Paper Said It Worked

A graduate student reads a paper describing a model that classifies land cover from satellite imagery with 94% accuracy. It is exactly what her project needs. The paper has a "code available" link. She clicks it and finds a GitHub repository with a training script, no requirements file, a README that says "see paper for details," and a link to the trained weights on a lab server that returns a 404 error. She emails the corresponding author, who has since moved to industry. After two weeks she gets the training script running with a guessed set of library versions, trains the model herself, and gets 81% accuracy. She has no way of knowing whether the gap comes from her environment, a preprocessing step the paper did not describe, a different random seed, or an error in the original work.

Nothing in this story involves misconduct. Everyone involved did roughly what was expected of them at the time. And yet a published result is effectively unusable, a student has lost a month, and the scientific record contains a number that nobody can check.

This handbook is about closing that gap. It covers the practical steps that let someone else (including your future self) find your model or dataset, run it, get the same answer you did, and use it in their own work. The steps are not exotic. Most of them take an afternoon to learn. The hard part is doing them consistently, at the moment when the paper is accepted and everyone wants to move on.

## A Shared Vocabulary

Researchers use "reproducible" to mean several different things, and the confusion causes real disagreements about whether a result "holds up." This handbook follows the definitions from the National Academies of Sciences, Engineering, and Medicine {footcite}`nasem2019`:

**Reproducibility** means obtaining consistent results using the same input data, computational steps, methods, code, and conditions of analysis. If I give you my data and my code and you run it, do you get my numbers?

**Replicability** means obtaining consistent results across studies aimed at answering the same scientific question, each of which has obtained its own data. If you collect a new sample and train a new model following my methods, do you reach the same conclusion?

Two further terms are useful for AI work. **Repeatability** is the narrowest case: can I get the same result again on my own machine, today? It sounds trivial, but for models trained on GPUs it often is not (see Chapter 7). **Generalizability** is the broadest: does the model work on data from a different hospital, a different city, or a different decade?

These form a ladder. A result that is not repeatable cannot be reproducible, and a result that is not reproducible gives nobody a firm basis for testing replicability. This handbook focuses on the lower rungs, repeatability and reproducibility, because they are almost entirely within your control. Replicability and generalizability depend on the science itself. But you cannot study them properly until the lower rungs are solid.

## Where AI Research Breaks

The evidence that computational research often fails to reproduce is now substantial. A study of 1.4 million Jupyter notebooks on GitHub found that only about a quarter ran without errors, and only about 4% reproduced their original results {footcite}`pimentel2019`. A study of R code deposited in the Harvard Dataverse, most of it attached to published research, found that 74% of files failed to run without error on first attempt {footcite}`trisovic2022`. When researchers asked authors of computational papers in *Science* for their data and code, they obtained materials for fewer than half of the articles and could reproduce results for about a quarter {footcite}`stodden2018`. A survey of papers at top AI conferences found that most shared too little information to be reproduced at all {footcite}`gundersen2018`.

When you look at why AI results fail to reproduce, the same causes appear again and again.

**Environment drift.** The code depended on specific versions of Python, PyTorch, CUDA, and dozens of other libraries, and none of that was recorded. By the time someone else runs it, the versions have changed. Chapters 5 and 6 cover this.

**Missing or unfindable data.** The data lived on a lab server, a personal Google Drive, or a student's laptop. Or it was shared "on request" and the request was never answered. Part III of this handbook covers this.

**Undocumented steps.** A preprocessing script was run once, by hand, and never committed. A filtering decision was made in a spreadsheet. Hyperparameters were tuned interactively and the final values were never written down. Chapters 4, 8, and 9 cover this.

**Leakage and evaluation errors.** A review of machine learning-based science across 17 fields found data leakage (for example, information from the test set influencing training) affecting hundreds of published papers {footcite}`kapoor2023`. These errors are hard to spot without the code and data, which is one more reason to share them.

**Randomness and hardware.** Two training runs with different random seeds can differ by more than the improvement a paper claims. GPUs introduce their own nondeterminism. Hosted large language models can change behind the same API name. Chapter 7 covers this.

**Link rot.** The model weights, the dataset, or the project website simply disappeared. Chapter 20 covers this.

The common thread is that none of these are failures of intelligence or effort. They are failures of recording and packaging, and they are mostly preventable.

## Three Meanings of Accessible

The second half of this handbook's title is "accessible," and we use it in three senses. All three are about the same thing: whether someone other than the creator can actually benefit from the work.

**Can I get it?** This is open access in the familiar sense: is the model, data, or code available at a stable address, under a license that permits reuse, with enough documentation to understand what it is? This connects to the FAIR principles in Chapter 3, and to the funder mandates, repositories, and licensing questions in Part III.

**Can I run it?** A model that requires eight high-end GPUs is technically open but practically closed to most researchers, students, community organizations, and institutions without large computing budgets. Chapter 21 covers how to make models usable on modest hardware, and Chapter 22 covers interactive demos that let people try a model with no installation at all.

**Can I use it?** Research outputs should be usable by people with disabilities: a figure needs alt text for a blind reader, a color scheme should not depend on distinguishing red from green, a tutorial video needs captions, and a demo app should work with a keyboard. For public universities in the United States, this is also becoming a legal requirement under the updated ADA Title II rule (Chapter 23).

We group these together because they tend to fail together, and because the practices that fix one often help the others. A well-documented model with a lightweight variant and an accessible demo page is easier to reproduce, easier to access, and easier to use.

## Who This Handbook Is For

This handbook is written for anyone who produces or curates AI research outputs.

- **Researchers publishing a model, dataset, or tool** will find the most value in Parts II and III.
- **Students inheriting a project** from a graduated labmate can use Part II to diagnose what is missing and rebuild it.
- **Principal investigators writing grant proposals** will want Chapter 12 on data management and sharing plans.
- **Research staff and data stewards** can use Chapters 2, 20, and 25 to set up review and maintenance processes.
- **Reviewers and editors** can use Chapter 11 as a guide to what a reproducible artifact should include.

Like the [AI in Research Handbook](https://midas-ai-in-research.readthedocs.io/en/main/), this book assumes basic familiarity with Python for the technical chapters but explains concepts in plain language first. You do not need to be a software engineer.

## How the Handbook Is Organized

**Part I: Foundations** (Chapters 1 through 3) sets up the concepts. Chapter 2 introduces the MIDAS Model Zoo, which is the practical destination for much of the work described here. Chapter 3 covers the FAIR and CARE principles that underpin responsible sharing.

**Part II: Building Reproducible Models** (Chapters 4 through 11) moves from project organization through environments, containers, randomness, experiment tracking, automation, documentation, and finally a pre-release reproducibility check.

**Part III: Sharing Data and Models** (Chapters 12 through 20) covers funder requirements, choosing where to share, specific guidance for Hugging Face, Kaggle, and archival repositories, dataset documentation, licensing, sensitive data, and the often-neglected question of how to make sure what you shared stays available.

**Part IV: Accessible AI** (Chapters 21 through 24) covers running models on modest hardware, building demos, disability accessibility, and writing documentation that newcomers can follow.

**Part V: Resources and Reference** (Chapters 25 through 27) collects checklists, templates, U-M resources, and a glossary.

Every chapter stands on its own. If you are about to publish a model next week, start with Chapters 10, 11, and 14. If you are writing a grant, start with Chapter 12. If you are trying to get someone else's model to run, start with Chapters 5 through 7.

## Try This

Pick a paper you published or contributed to at least a year ago that involved code or a model. Without looking at your own files, go to the paper and follow only what it links to. Can you find the code? The data? The trained model? Do the links still work? Could you tell which version of the code produced the figures?

Write down every point where you got stuck. That list is a personal map of which chapters in this handbook will be most useful to you.

### Hands-On: A Five-Minute Project Audit

For a quick, automated first look at one of your own project folders, save this script and run it with `python repro_audit.py path/to/your/project`. It checks for the files that later chapters will ask you to create, and looks for two common problems: file paths that only exist on your computer, and notebooks saved with their outputs.

```python
# repro_audit.py: a quick reproducibility check of a project folder
import json, re, sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

def exists(*patterns):
    return any(list(root.glob(p)) for p in patterns)

checks = {
    "README":                 exists("README*"),
    "License":                exists("LICENSE*", "LICENCE*"),
    "Citation file":          exists("CITATION.cff"),
    "Environment/lockfile":   exists("uv.lock", "poetry.lock", "requirements*.txt",
                                     "environment.yml", "conda-lock.yml", "pixi.lock", "renv.lock"),
    "Container":              exists("Dockerfile", "*.def", ".devcontainer/devcontainer.json"),
    "Tests":                  exists("tests/*", "test_*.py"),
    "Automated checks (CI)":  exists(".github/workflows/*.yml", ".github/workflows/*.yaml"),
    ".gitignore":             exists(".gitignore"),
}

# Hard-coded personal paths are a common reason code fails elsewhere
path_pattern = re.compile(r"(/Users/\w+|/home/\w+|[A-Za-z]:[\\/]+Users)")
hard_coded = [str(p.relative_to(root)) for p in root.rglob("*")
              if p.suffix in {".py", ".R", ".ipynb", ".sh"} and p.is_file()
              and path_pattern.search(p.read_text(errors="ignore"))]

# Notebooks saved with outputs make diffs noisy and can leak data
with_outputs = []
for nb in root.rglob("*.ipynb"):
    try:
        cells = json.loads(nb.read_text())["cells"]
        if any(c.get("outputs") for c in cells if c["cell_type"] == "code"):
            with_outputs.append(str(nb.relative_to(root)))
    except Exception:
        pass

for name, ok in checks.items():
    print(f"[{'x' if ok else ' '}] {name}")
print(f"[{'x' if not hard_coded else ' '}] No hard-coded personal paths"
      + (f"  -> {hard_coded[:5]}" if hard_coded else ""))
print(f"[{'x' if not with_outputs else ' '}] Notebooks saved without outputs"
      + (f"  -> {with_outputs[:5]}" if with_outputs else ""))
```

Here is the output for a typical early-stage project:

```text
[x] README
[ ] License
[ ] Citation file
[x] Environment/lockfile
[ ] Container
[ ] Tests
[ ] Automated checks (CI)
[ ] .gitignore
[ ] No hard-coded personal paths  -> ['scripts/clean.py']
[ ] Notebooks saved without outputs  -> ['notebooks/01_explore.ipynb']
```

Each unchecked box maps to a chapter: licenses in Chapter 18, citation files in Chapter 10, environments in Chapter 5, containers in Chapter 6, tests and CI in Chapter 9, and paths and notebooks in Chapter 4. A project does not need every box checked to be useful, but each one you add removes a common reason someone else could not use your work. The script only looks for files; it cannot tell whether your README is clear or your lockfile complete. Chapter 11 covers how to test that.

## Further Reading

The National Academies report *Reproducibility and Replicability in Science* {footcite}`nasem2019` is the standard reference for definitions and the broader policy context. For a field-specific diagnosis of what goes wrong in ML-based science, Kapoor and Narayanan's paper on leakage {footcite}`kapoor2023` and the REFORMS checklist that followed it {footcite}`kapoor2024` are essential reading. The Turing Way {footcite}`TheturingwayTeam2022` is a large community-written handbook that covers reproducibility, collaboration, and ethics across all of computational research.

## Related Chapters

- [Chapter 2: The MIDAS Model Zoo](ch02_model_zoo.md)
- [Chapter 3: FAIR, FAIR4RS, and CARE](ch03_fair_principles.md)
- [Chapter 7: Randomness, Determinism, and Hardware](../part2/ch07_determinism.md)
- [Chapter 20: Making Sure It Stays Shared](../part3/ch20_persistence.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
