# Chapter 11: Testing Reproducibility Before You Share

:::{admonition} What You Will Learn
:class: tip

- How to do a clean-room rerun of your own work
- How to organize a quick reproducibility swap with a colleague
- Tools that let others run your code without installing anything
- What artifact evaluation and reproducibility badges look for
- A pre-release checklist you can use for every paper
:::

## You Cannot Check Your Own Work From the Inside

When you run your own code, your machine quietly fills every gap. The package you installed six months ago for a different project is still there. The data file is in the folder where you left it. The environment variable is set in your shell profile. The cell you ran out of order in the notebook left a variable in memory. Everything works, and so you conclude that everything is documented.

The only reliable way to find out whether your work reproduces is to try it somewhere that does not have your hidden state: a fresh machine, a fresh account, or a different person. This chapter describes how to do that efficiently, ideally before you submit a paper rather than after a reader reports a problem.

## The Clean-Room Rerun

A clean-room rerun means starting from nothing except what you are going to share, and following only your written instructions.

**Get a clean environment.** Options include a GitHub Codespace, a fresh Google Colab session, a new virtual machine, a Great Lakes session with no modules loaded, a Docker container from a plain base image, or a colleague's laptop. The important thing is that it has never seen your project.

**Get your artifacts the way a stranger would.** Clone the public repository (not your local copy). Download data and weights from the public links in your README, while logged out, so you see what an anonymous user sees. Use the DOIs from your paper, not bookmarks.

**Follow the README literally.** Type exactly the commands it gives, in the order it gives them. Do not fix anything from memory. Every time you have to improvise, whether by installing a missing package, creating a folder, guessing a file path, or looking something up in your own code, write it down. Each of these is a bug in your documentation.

**Compare results.** Run the quickstart and check its output matches the README. Then run the main pipeline, or a representative portion if training is expensive, and compare key numbers against the paper. Use tolerances that reflect the variability you measured in Chapter 7.

**Fix and repeat.** Update the README, lockfile, or code to remove every improvisation, then do another clean-room run. Keep going until a run needs no improvisation at all.

### Hands-On: A Clean Room in One Command

If you have Docker installed, a throwaway container is the quickest clean machine there is. It starts with nothing but Python and disappears when you exit:

```bash
docker run --rm -it python:3.11.9-slim bash

# Inside the container: you are now a stranger with a fresh computer
apt-get update && apt-get install -y git
git clone https://github.com/your-lab/your-project.git && cd your-project
# ...now follow your README, word for word, and note every improvisation
```

GitHub Codespaces offers the same thing in a browser: open the repository on GitHub, choose **Code → Codespaces → Create codespace**, and you have a fresh Linux environment with your repository already cloned. Delete the codespace when you finish.

To keep a record of what you did, run `script clean-room-log.txt` at the start of the session; everything you type and every output is saved to that file until you type `exit`. The log is a useful attachment for a reproducibility report.

### Hands-On: Compare Against the Paper Automatically

Comparing numbers by eye is error-prone. A short script makes the comparison explicit, including what tolerance you consider "reproduced":

```python
# scripts/check_reproduction.py
import json, sys

# Values reported in the paper, with the tolerance you consider "reproduced".
# Base tolerances on the seed-to-seed spread you measured (Chapter 7).
REPORTED = {
    "test_accuracy":  {"value": 0.912, "tol": 0.010},
    "test_f1_macro":  {"value": 0.874, "tol": 0.015},
    "n_test_samples": {"value": 1830,  "tol": 0},      # counts should match exactly
}

reproduced = json.load(open(sys.argv[1]))
failures = 0
for name, spec in REPORTED.items():
    got = reproduced.get(name)
    ok = got is not None and abs(got - spec["value"]) <= spec["tol"]
    failures += not ok
    print(f"{'OK  ' if ok else 'FAIL'} {name:15} paper={spec['value']:<8} "
          f"reproduced={got!s:<8} tolerance=±{spec['tol']}")
sys.exit(1 if failures else 0)
```

```bash
python scripts/check_reproduction.py runs/<run_id>/metrics.json
```

```text
OK   test_accuracy   paper=0.912    reproduced=0.9087   tolerance=±0.01
FAIL test_f1_macro   paper=0.874    reproduced=0.851    tolerance=±0.015
OK   n_test_samples  paper=1830     reproduced=1830     tolerance=±0
```

The script exits with an error code when anything fails, so it can run in CI (Chapter 9). Writing the tolerances down before you run the check protects you from yourself: it is tempting to decide afterwards that a gap was "close enough." A failure like the F1 score above is worth investigating, since accuracy reproduced but a class-sensitive metric did not, which often points to a difference in the test set or class balance.

This typically takes an afternoon for a well-organized project and a few days for one that was not. It is much faster before publication than after, when you may have moved on to other work and forgotten the details.

## Ask a Colleague

A clean-room rerun by you is good. A rerun by someone else is better, because they do not share your assumptions about what is "obvious."

A **reproducibility swap** is a simple arrangement: two researchers, or two labs, agree to try to reproduce each other's work before submission. Each gets the public repository and README and spends a fixed amount of time (an hour or two is enough to find most problems) trying to get the quickstart running and one key result reproduced. They record where they got stuck and send a short report.

Useful questions for the report:

- How long did it take to get the environment working?
- Did the quickstart run, and did its output match the README?
- Were you able to reproduce a key result? How close was it?
- Where did you have to guess or improvise?
- Was anything in the README unclear or wrong?
- What would you need to use this model for your own work?

Some departments and labs run these swaps as a regular event, sometimes called a "ReproHack." They are also an excellent training exercise for students, who learn more about reproducibility by trying to reproduce someone else's work than by reading about it.

## One-Click Environments

Several services let people run your code in a browser, with no installation. Offering one lowers the barrier for reviewers, students, and anyone curious about your work.

**Google Colab** runs Jupyter notebooks in the cloud for free, with limited GPU access. Adding an "Open in Colab" badge to a notebook in your GitHub repository takes one line of Markdown. The companion notebooks for the AI in Research Handbook use this approach. Colab's preinstalled packages change over time, so install pinned versions at the top of your notebook rather than relying on what is already there.

**Binder** (mybinder.org) builds a Docker image from your repository's environment files and launches it as a Jupyter or RStudio session. It is free and open source, and it forces you to have complete environment files, which is itself a good reproducibility test. Resources are limited and sessions are temporary, so it is best for demonstrations rather than heavy computation.

Binder looks for standard environment files in the repository root or in a `binder/` folder. For a pip-based project, two small files are enough:

```text
binder/requirements.txt    # pinned packages, e.g. exported from uv (Chapter 5)
binder/runtime.txt         # contains one line, such as: python-3.11
```

Then add badges to your README. Replace the user, repository, branch, and notebook path with your own:

```markdown
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/your-lab/your-project/main?labpath=notebooks%2Fquickstart.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/your-lab/your-project/blob/main/notebooks/quickstart.ipynb)
```

Point Binder at a tag rather than `main` (for example `.../your-project/v1.0?labpath=...`) if you want the badge in a paper to always open the published version.

**GitHub Codespaces** launches a full VS Code environment in the cloud from your repository's dev container configuration (Chapter 6). It includes a monthly free allowance for personal accounts, with additional benefits for students and educators through GitHub Education.

**Code Ocean** is a research-focused platform that packages code, data, environment, and results into "compute capsules" that can be run and verified by others. Some journals integrate with it for peer review.

**Hugging Face Spaces** and similar demo platforms (Chapter 22) let users try a model through a web interface without seeing code at all.

## Artifact Evaluation

Some computer science conferences and a growing number of journals formally evaluate research artifacts. The ACM's badging system is widely used and gives a useful picture of what "reproducible" means to evaluators. It distinguishes:

**Artifacts Available.** The artifacts are in a permanent, publicly accessible archive with a persistent identifier. A GitHub link is not sufficient; a Zenodo DOI is.

**Artifacts Evaluated: Functional.** The artifacts are documented, consistent with the paper, complete, and can be run.

**Artifacts Evaluated: Reusable.** Beyond functional, they are well documented and structured so others can build on them.

**Results Reproduced.** Evaluators obtained the main results using the authors' artifacts.

**Results Replicated.** Evaluators obtained the main results without the authors' artifacts, using an independent implementation.

Even if your venue does not offer badges, these levels are a helpful self-assessment. They also map closely to the proposed Model Zoo tiers in Chapter 2: "Available" corresponds to Listed with an archival DOI, "Functional" and "Reusable" to Documented and Reproducible.

## A Pre-Release Checklist

Use this checklist before you submit a paper or release a model. Chapter 25 has a printable version.

**Code**
- [ ] All code needed to produce reported results is committed and pushed.
- [ ] A release is tagged and archived with a DOI.
- [ ] No hard-coded paths to your machine; no secrets in the repository.

**Environment**
- [ ] A lockfile or container is committed and documented.
- [ ] Hardware requirements (GPU, memory) are stated.

**Data and models**
- [ ] Data and trained weights are in a public or controlled-access repository with a DOI, or the README explains why not and how to get access.
- [ ] Checksums are provided for downloaded files.

**Documentation**
- [ ] README quickstart runs on a clean machine and produces the documented output.
- [ ] Model card and/or datasheet are complete.
- [ ] `CITATION.cff` and a license are present.

**Verification**
- [ ] A clean-room rerun succeeded without improvisation.
- [ ] Key results match the paper within stated tolerance.
- [ ] Results report variability across seeds.

## Try This

Pick your most recent paper that involved code. Run the clean-room procedure on it using a GitHub Codespace or a fresh Colab session. Time how long it takes to reproduce one key figure or number, and list every improvisation. If you want an extra challenge, trade projects with a colleague and do a reproducibility swap.

## Further Reading

The ACM's "Artifact Review and Badging" policy page defines each badge. The NeurIPS reproducibility program report {footcite}`pineau2021` describes what happened when a major conference asked authors to share code and invited the community to reproduce papers.

## Related Chapters

- [Chapter 9: Pipelines, Automation, and Continuous Integration](ch09_workflows.md)
- [Chapter 20: Making Sure It Stays Shared](../part3/ch20_persistence.md)
- [Chapter 25: Checklists and Templates](../part5/ch25_checklists_templates.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
