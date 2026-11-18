# Chapter 24: Accessible Documentation and Teaching Materials

:::{admonition} What You Will Learn
:class: tip

- How to write documentation that newcomers to your field can follow
- How to organize documentation into tutorials, how-to guides, reference, and explanation
- How to design tutorials that run anywhere, including on free cloud notebooks
- Approaches to reaching readers beyond English
- How to collect and act on feedback
:::

## The Curse of Knowledge

By the time you share a model or dataset, you understand it better than anyone. That is exactly what makes documenting it hard. Terms that feel basic to you ("embedding," "stratified split," "the usual preprocessing") are unfamiliar to a researcher from another field. Steps that feel obvious (activating the environment, downloading the weights, changing into the right folder) are invisible to you and blocking to them. This is sometimes called the curse of knowledge.

The earlier chapters covered what documentation must contain: READMEs and model cards (Chapter 10), datasheets (Chapter 17), and accessibility requirements (Chapter 23). This chapter is about how to write and structure it so that people with different backgrounds, languages, and resources can actually use your work. It also applies to teaching materials, such as workshop notebooks and tutorials, which are among the most reused outputs of research groups like MIDAS.

## Plain Language

Plain language is writing that the intended audience can understand the first time they read it. It is not "dumbing down." Experts also read plain language faster and misunderstand it less often.

A few habits make the biggest difference:

**Lead with what the reader wants to do.** Start sections with the task or outcome ("To run the model on your own images...") rather than background.

**Define terms on first use,** or link to a glossary (Chapter 27). If a term is not needed, leave it out.

**Use short sentences and active voice.** "Run the script" rather than "The script should be run."

**Give an example before the general rule.** A concrete command or code snippet is usually clearer than a paragraph describing it.

**Be explicit about prerequisites.** Say what the reader needs to know and have installed before starting, and link to resources for anything missing.

**Avoid "simply," "just," and "obviously."** If a step were obvious, it would not need documenting, and these words make readers who are stuck feel worse.

Plain language also supports the cognitive accessibility goals of Chapter 23, and makes machine translation work better.

### Hands-On: A Quick Plain-Language Report

Long sentences are the easiest plain-language problem to measure. This script strips code and formatting from Markdown files and reports average sentence length, the number of sentences over 30 words, and the share of very long words, which often signal jargon:

```python
# scripts/plain_language_report.py: quick plain-language check for Markdown docs
import re, sys

def prose_only(markdown):
    text = re.sub(r"```.*?```", " ", markdown, flags=re.S)    # drop code blocks
    text = re.sub(r"`[^`]*`", " ", text)                       # drop inline code
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)       # keep link text only
    text = re.sub(r"^\s*(:::|:\w+:).*$", "", text, flags=re.M)     # MyST directive lines
    text = re.sub(r"^\s*(#+|[-*]|\d+\.)\s*", "", text, flags=re.M)  # headings, list marks
    return text.replace("*", "")

for path in sys.argv[1:]:
    text = prose_only(open(path, encoding="utf-8").read())
    sentences = [s for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.split()) > 2]
    lengths = [len(s.split()) for s in sentences]
    long_ones = [s for s, n in zip(sentences, lengths) if n > 30]
    words = re.findall(r"[A-Za-z]+", text)
    print(f"{path}\n  {len(sentences)} sentences, {sum(lengths) / len(lengths):.1f} words on average; "
          f"{len(long_ones)} over 30 words; "
          f"{sum(len(w) >= 13 for w in words) / len(words):.1%} very long words")
    for s in long_ones[:3]:
        print(f"  long: {' '.join(s.split()[:16])} ...")
```

Running it on two chapters of this handbook:

```text
docs/part4/ch24_accessible_docs.md
  107 sentences, 12.5 words on average; 2 over 30 words; 2.1% very long words
  long: A common problem in research documentation is a single README that tries to be a tutorial, ...
docs/part3/ch12_mandates.md
  131 sentences, 14.6 words on average; 8 over 30 words; 0.9% very long words
  long: When researchers systematically requested data and code from authors of computational papers in Science, a journal ...
```

The policy chapter has four times as many very long sentences, which is common for writing that summarizes regulations, and the report points straight to the ones worth splitting. Plain-language guides commonly suggest averaging around 15 to 20 words per sentence. Treat the numbers as prompts for a second look, not as scores to optimize: a clear 32-word sentence is better than two confusing short ones.

## Layered Documentation

A common problem in research documentation is a single README that tries to be a tutorial, a reference manual, and a methods paper at once, and does none of them well. The **Diátaxis** framework {footcite}`procida_diataxis` separates documentation into four types based on what the reader needs:

**Tutorials** are learning-oriented. They take a newcomer through a complete, guided example from start to finish, with a guaranteed successful outcome. "Classify your first ten images with the roof condition model."

**How-to guides** are task-oriented. They help someone who already knows the basics accomplish a specific goal. "How to fine-tune the model on images from a new city." "How to run the model on Great Lakes."

**Reference** is information-oriented. It describes the functions, parameters, file formats, and data fields accurately and completely. API documentation and data dictionaries are reference.

**Explanation** is understanding-oriented. It discusses background, design choices, and trade-offs. "Why we chose this architecture." "How the labels were validated." Model cards and datasheets contain a lot of explanation.

For a small project, these can be sections of a single README: a quickstart (a mini-tutorial), a few how-to recipes, a reference table, and a link to the paper for explanation. For larger projects, they become separate pages in a documentation site. The key is to know which kind of writing you are doing in each place, and not mix them.

## Tutorials That Run Anywhere

A tutorial that only runs on a machine with the right GPU, the right operating system, and an afternoon of setup will lose most of its audience at step one. Tutorials should be designed so that anyone with a web browser can complete them.

**Use a free cloud notebook.** Google Colab is the most common choice, and Kaggle notebooks (Chapter 15) are an alternative. Add an "Open in Colab" badge to the top of the notebook and the README:

```markdown
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/your-lab/your-repo/blob/main/notebooks/tutorial.ipynb)
```

The AI in Research Handbook's companion notebooks use this approach, and it is a good model to follow.

**Install pinned versions in the first cell.** Colab's preinstalled packages change over time. A first cell such as `!pip install -q transformers==4.44.2 datasets==2.21.0` makes the tutorial much more likely to work a year from now.

### Hands-On: A Setup Cell That Works Everywhere

A good first cell does more than install packages. This one installs pinned versions only when running in Colab (so it does not disturb a reader's own environment), downloads the sample data from a stable, versioned URL, warns if the data have changed since the tutorial was written (Chapter 20), and reports whether a GPU is available:

```python
# Setup: run this cell first. It works in Colab, Kaggle, and on your own computer.
import subprocess, sys

PINNED = ["scikit-learn==1.5.2", "pandas==2.2.3"]          # versions this tutorial was tested with
IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", *PINNED], check=True)

import hashlib, urllib.request
from pathlib import Path

DATA_URL = "https://zenodo.org/records/0000000/files/sample.csv"   # stable, versioned URL
DATA_SHA256 = "replace-with-the-real-checksum"
data_path = Path("sample.csv")
if not data_path.exists():
    urllib.request.urlretrieve(DATA_URL, data_path)
if hashlib.sha256(data_path.read_bytes()).hexdigest() != DATA_SHA256:
    print("Warning: the data file differs from the version this tutorial was written for.")

try:
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError:
    device = "cpu"
print(f"Running in {'Colab' if IN_COLAB else 'a local environment'} on {device}.")
```

```text
Running in a local environment on cpu.
```

The warning about changed data is deliberately not an error: the reader can still continue, but knows that small differences from the tutorial's outputs may be expected.

**Ship small sample data.** Include a small dataset in the repository or download it from a stable URL with a checksum (Chapter 20). The tutorial should complete in minutes, not hours.

**Default to CPU, with optional GPU.** Design the tutorial to complete on a free CPU session, and note where a GPU would speed things up. Use the device detection code from Chapter 21.

**Explain as you go.** Each code cell should be preceded by a short Markdown cell explaining what it does and why, and followed by a sentence interpreting the output. This is what distinguishes a tutorial from a script.

**End with "bring your own data."** Show readers where to swap in their own data and what format it needs to be in. This is where a tutorial turns into research use.

**Test it regularly.** Run the tutorial from a fresh session before each workshop and on a schedule (Chapter 9). Tutorials break more often than any other kind of research code, because they depend on so many external services.

### Hands-On: Test Every Notebook Automatically

The `nbmake` plugin for pytest runs each notebook from top to bottom in a fresh kernel and reports any that fail:

```bash
pip install nbmake
pytest --nbmake notebooks/
```

```text
FAILED notebooks/broken.ipynb::broken.ipynb - ModuleNotFoundError: No module named 'not_a_real_package'
1 failed, 1 passed in 2.88s
```

Add it to a scheduled GitHub Actions workflow (Chapter 9) and you will learn that a tutorial broke before workshop participants do. For tutorials that take a long time with real data, tag one cell as `parameters` and use `papermill` to run a fast version with smaller settings in CI:

```bash
pip install papermill
papermill notebooks/tutorial.ipynb /tmp/tutorial-smoke.ipynb -p n_samples 200
```

Papermill replaces the values in the cell tagged `parameters` (for example, `n_samples = 5000`) with the ones you pass, then runs the whole notebook and saves the executed copy.

## Reaching Beyond English

Most AI research documentation is written only in English, which is a barrier for many students and researchers worldwide, and for community partners in the United States.

**Write for translation.** Plain language, short sentences, and consistent terminology make both machine and human translation much more accurate.

**Use AI-assisted translation with review.** Machine translation tools and large language models can produce good first drafts of documentation in other languages. As with alt text (Chapter 23), a fluent reader with domain knowledge should review the translation, especially for technical terms, which are often translated inconsistently or incorrectly.

**Prioritize what to translate.** You do not need to translate everything. The README summary, the quickstart, the model card's intended use and limitations, and demo interface text are the most valuable.

**Keep a bilingual glossary** of key terms so translations stay consistent across documents.

**Consider your audience.** If your model or dataset concerns a particular community or region, documentation in the languages spoken there is especially important, and connects to the CARE principles in Chapter 3.

## Feedback Loops

Documentation improves most quickly when readers can tell you where they got stuck.

**Make feedback easy.** Link to GitHub Issues or a short feedback form from every page. This handbook, like the AI in Research Handbook, includes a feedback link on each page.

**Watch where people struggle.** Questions in issues, emails, and workshop chats are a map of where your documentation fails. When the same question comes up twice, update the documentation.

**Run usability tests.** Ask someone new to the project to follow the tutorial while you watch silently, and note where they hesitate. This is the documentation equivalent of the reproducibility swap in Chapter 11, and is similarly effective.

**Keep a changelog** so returning readers can see what has changed.

## Try This

Pick a tutorial or README you have written. Label each section as tutorial, how-to, reference, or explanation, and notice where they are mixed. Then open the tutorial in a fresh Colab session and try to complete it as written, noting every place you have to improvise. Fix those, add pinned installs to the first cell, and add an "Open in Colab" badge.

## Further Reading

The Diátaxis website {footcite}`procida_diataxis` explains the four documentation types in depth. The U.S. federal government's plain language guidelines (plainlanguage.gov) are a practical writing reference. The Carpentries' instructor training materials offer evidence-based advice on teaching technical material to newcomers.

## Related Chapters

- [Chapter 10: Documenting Models](../part2/ch10_documenting_models.md)
- [Chapter 21: AI on Modest Hardware](ch21_low_resource.md)
- [Chapter 23: Disability Accessibility for Research Outputs](ch23_disability_access.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
