# Chapter 20: Making Sure It Stays Shared

:::{admonition} What You Will Learn
:class: tip

- Why shared research artifacts disappear, and how often
- How to verify that a dataset or model can actually be obtained and used by a stranger
- How to set up automated checks that catch broken links and failing downloads
- How to plan stewardship for the years after a paper is published
- How to retire an artifact responsibly
- How the Model Zoo can help keep entries alive
:::

## Shared Is Not the Same as Available

Chapters 12 through 19 covered how to share. This chapter covers something that gets much less attention: making sure that what you shared is still there, and still usable, a year or five years later.

The problem is common. A Pew Research Center study found that 38% of web pages that existed in 2013 were no longer accessible a decade later, and that more than half of Wikipedia pages had at least one broken reference link {footcite}`pew2024`. Scholarly articles are not immune. A large study of science, technology, and medicine articles found that about one in five articles that referenced web resources suffered from "reference rot": links that no longer worked or no longer pointed to the original content {footcite}`klein2014`. Links to code and data are especially fragile because they often point to personal accounts and lab servers.

When an artifact disappears, the paper that depends on it loses much of its value. The results can no longer be checked, the model cannot be reused, and the time others spent trying to find it is wasted.

## How Artifacts Disappear

The causes are mostly mundane.

**Personal accounts.** A student uploads data to their personal Google Drive or GitHub account. They graduate, their university account is closed, or they delete old repositories while cleaning up.

**Lab and project websites.** A server is retired, a domain is not renewed, or a website is rebuilt and old pages are not migrated.

**Hub deletions and changes.** A repository on Hugging Face, Kaggle, or GitHub is deleted, renamed, or made private. Renaming often breaks links even when the content survives.

**Silent changes.** The content still exists at the same address, but it has changed. A dataset is updated in place, or a model on a hub is overwritten with a new version, and users of the paper get something different from what the authors used.

**Dependency rot.** The files are available, but the code cannot run because a package it depends on has vanished or changed (Chapters 5 and 6).

**Access process breakdown.** Data are listed as "available on request" or through a controlled-access process, but nobody is left to answer requests.

Almost every one of these is preventable with the practices in this handbook: archival repositories with DOIs (Chapter 16), institutional or organizational accounts (Chapter 14), pinned versions and tags (Chapters 4 and 14), and lockfiles and containers (Chapters 5 and 6). This chapter adds two more: verification and stewardship.

## Verify Like a Stranger

Before you publish, and periodically after, check your shared artifacts from the perspective of someone who has never seen them. This is the sharing counterpart to the clean-room rerun in Chapter 11.

**Use the paper's links, not your bookmarks.** Start from the DOIs and URLs in the published paper or preprint. Click each one.

**Log out, or use a private browser window.** Many broken shares only look fine because you are logged in. A private Google Drive link, a private Hugging Face repository, or a Kaggle dataset still in draft all appear to work for their owner.

**Download the files and verify checksums.** Compare the SHA-256 hash of each downloaded file with the one in your README:

```bash
sha256sum -c SHA256SUMS.txt
```

To create the checksum file in the first place:

```bash
sha256sum data/*.parquet models/*.safetensors > SHA256SUMS.txt
```

On macOS, use `shasum -a 256` in place of `sha256sum`. On Windows, or if you want one tool for every platform, this short Python script creates and verifies the same file format:

```python
# scripts/checksums.py: create or verify SHA256SUMS.txt on any operating system
#   python checksums.py make   release/   -> writes release/SHA256SUMS.txt
#   python checksums.py verify release/   -> checks every file listed in it
import hashlib, sys
from pathlib import Path

def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()

mode, folder = sys.argv[1], Path(sys.argv[2])
manifest = folder / "SHA256SUMS.txt"

if mode == "make":
    files = sorted(p for p in folder.rglob("*") if p.is_file() and p != manifest)
    lines = [f"{sha256(p)}  {p.relative_to(folder).as_posix()}" for p in files]
    manifest.write_text("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} checksums to {manifest}")
else:
    bad = 0
    for line in manifest.read_text().splitlines():
        expected, name = line.split(maxsplit=1)
        path = folder / name
        ok = path.exists() and sha256(path) == expected
        bad += not ok
        print(f"{'OK     ' if ok else 'FAILED '} {name}")
    sys.exit(1 if bad else 0)
```

```text
$ python checksums.py make release/
wrote 3 checksums to release/SHA256SUMS.txt

$ python checksums.py verify release/
OK      README.md
FAILED  model.safetensors
OK      sub/labels.csv
```

The `SHA256SUMS.txt` it writes is compatible with `sha256sum -c`, so users on Linux and macOS can verify with the standard tools. A `FAILED` line means the file is corrupted, incomplete, or not the version you released. Deposit `SHA256SUMS.txt` alongside your files in every repository you use, so users can verify their download no matter where it came from.

**Load and use the artifact following only the documentation.** Load the dataset with the documented code, run the model quickstart, and check that the output matches the README.

**Check the access path for restricted data.** If data are available through a controlled-access process, confirm that the process is described, that the contact address works, and that someone is responsible for responding.

**Check the citation.** Does the landing page tell users how to cite the artifact, and does the DOI resolve to it?

## Automated Health Checks

Manual checks happen once; automated checks happen every week. The scheduled CI jobs described in Chapter 9 can monitor your shared artifacts with very little code.

Here is a simple Python script that checks a list of artifact links and, for downloadable files, verifies checksums:

```python
# scripts/check_artifacts.py
import hashlib, sys, requests

ARTIFACTS = [
    {"name": "paper code (Zenodo)", "url": "https://doi.org/10.5281/zenodo.0000000"},
    {"name": "dataset (Deep Blue Data)", "url": "https://doi.org/10.7302/xxxx"},
    {"name": "model card (Hugging Face)",
     "url": "https://huggingface.co/your-lab/roof-condition-classifier/resolve/v1.0/README.md"},
    {"name": "test file", "url": "https://example.org/test_sample.parquet",
     "sha256": "3f2a...e91c"},
]

failures = []
for a in ARTIFACTS:
    try:
        r = requests.get(a["url"], timeout=60, allow_redirects=True)
        if r.status_code != 200:
            failures.append(f"{a['name']}: HTTP {r.status_code}")
            continue
        if "sha256" in a:
            digest = hashlib.sha256(r.content).hexdigest()
            if digest != a["sha256"]:
                failures.append(f"{a['name']}: checksum mismatch")
    except requests.RequestException as e:
        failures.append(f"{a['name']}: {e}")

if failures:
    print("\n".join(failures))
    sys.exit(1)
print("All artifacts OK")
```

Run it weekly with GitHub Actions:

```yaml
# .github/workflows/artifact-health.yml
name: artifact-health
on:
  schedule:
    - cron: "0 12 * * 1"   # Mondays 12:00 UTC
  workflow_dispatch:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install requests
      - run: python scripts/check_artifacts.py
```

### Hands-On: Check Everything in Your Sharing Inventory

If you keep the sharing inventory from Chapter 12, the health check can read its list of artifacts from there rather than from a hand-maintained list in the script. This version also checks that a Hugging Face tag still exists and points to a commit, which catches deleted, renamed, or privatized repositories as well as removed tags:

```python
# scripts/check_inventory.py: check every shared output listed in sharing_inventory.yaml
import sys
import requests
import yaml

def check_url(url):
    # stream=True fetches headers without downloading large files
    r = requests.get(url, timeout=60, allow_redirects=True, stream=True)
    r.close()
    return r.status_code == 200, f"HTTP {r.status_code}"

def check_hf_revision(repo_id, revision, repo_type="model"):
    from huggingface_hub import HfApi
    try:
        info = HfApi().repo_info(repo_id, revision=revision, repo_type=repo_type)
        return True, f"revision {revision} -> {info.sha[:10]}"
    except Exception as e:                      # deleted, renamed, private, or tag removed
        return False, type(e).__name__

inventory = yaml.safe_load(open("sharing_inventory.yaml"))
failures = 0
for o in inventory["outputs"]:
    if o.get("status") != "shared":
        continue
    if o.get("hf_repo"):
        ok, detail = check_hf_revision(o["hf_repo"], o.get("revision", "main"),
                                       o.get("hf_type", "model"))
    else:
        ok, detail = check_url(f"https://doi.org/{o['doi']}" if o.get("doi") else o["url"])
    failures += not ok
    print(f"{'OK  ' if ok else 'FAIL'} {o['name']}: {detail}")
sys.exit(1 if failures else 0)
```

Inventory entries for Hugging Face artifacts gain two fields, for example `hf_repo: your-lab/roof-condition-classifier` and `revision: v1.1`, and dataset repositories add `hf_type: dataset`. A run against an inventory containing one working page and one broken lab-site link prints:

```text
OK   Project page: HTTP 200
FAIL Old lab site link: HTTP 404
```

Outputs that are still in curation are skipped until their status changes to `shared`.

If a check fails, GitHub notifies the repository owners. For larger files, check headers or partial downloads rather than downloading the whole file each week. For models, go further: load the model at a pinned revision and run the golden output test from Chapter 9. This confirms not just that the files exist, but that they still work with the documented environment.

## Stewardship and Handoff

Every shared artifact needs a **steward**: someone responsible for responding to questions, fixing problems, and deciding what happens to it over time. By default this is whoever uploaded it, which is often a student or postdoc who will leave. Plan for that.

**Use organizational accounts.** Host artifacts under a lab, center, or department account on GitHub, Hugging Face, and Kaggle, with at least two administrators. Personal accounts should be the exception.

**Name a steward and a backup.** Record them in the README and in your lab's internal records. The steward is usually the PI or a long-term staff member, even if a student did the work.

**Write a handoff note when people leave.** When someone who created shared artifacts leaves the group, they should list what they shared, where, and under which accounts, and transfer ownership or administrative access before their university account is closed.

**Keep a lab inventory.** A simple spreadsheet listing every shared artifact, its location, its DOI, its steward, and its license makes stewardship manageable. It also makes grant reporting easier (Chapter 12).

**Decide how long to support it.** Archival copies in Deep Blue Data or Zenodo will persist without effort. Active support, such as answering questions, updating for new library versions, and maintaining a demo, takes time. It is reasonable to state in the README how long you plan to actively maintain an artifact, and what happens after that.

## Deprecation Done Well

Sometimes an artifact should be retired: a dataset is superseded by a corrected version, a model is found to have a serious flaw, or a demo is too costly to host. Retiring well means never leaving users with a dead link and no explanation.

**Do not silently delete.** Replace the content with a clear notice, sometimes called a tombstone, that says what the artifact was, why it was retired, when, and where to go instead. On GitHub or Hugging Face, the simplest tombstone is a replacement README:

```markdown
# Roof Condition Classifier (retired)

**Status:** Retired on 2027-03-01. Do not use for new work.

**Why:** A labeling error affected about 4% of the training images in the
`major_damage` class. Version 1.1 corrects this.

**Use instead:** [roof-condition-classifier v1.1](https://huggingface.co/your-lab/roof-condition-classifier/tree/v1.1)

**For reproducing Doe et al. (2026):** The original v1.0 weights remain archived,
unchanged, at https://doi.org/10.5281/zenodo.0000000.

Contact: your-lab@umich.edu
```

On GitHub, also archive the repository in its settings, which makes it read-only and marks it clearly as no longer maintained.

**Point to successors.** Link to the corrected dataset, newer model version, or archived copy.

**Keep the archival version.** If a corrected version replaces a flawed one, the original should generally remain in the archive (clearly marked) so that published results can still be checked. Archival repositories handle this through versioning and withdrawal notices.

**Tell users.** If you know who uses the artifact (for example, through a gated repository or a mailing list), let them know. Update the Model Zoo entry.

**For models with serious problems**, such as discovered bias or unsafe behavior, update the model card with a prominent warning before or instead of deletion, so users of existing copies can learn about the problem.

## The Model Zoo as a Steward

Individual researchers are often not well placed to maintain artifacts for years. An institutional catalog like the Model Zoo can share some of the burden. Planned stewardship features include:

- **Periodic automated checks** of every entry's links, using the same approach as the health check above, with more thorough checks (such as running the quickstart) for higher-tier entries.
- **A status indicator** for each entry showing when it was last verified and whether its links work.
- **Outreach to creators** when an entry fails a check, with help to fix it.
- **Deprecation notes** rather than removals, linking to archived copies where they exist.
- **Encouraging archival copies**, so that every entry has a DOI-backed version that does not depend on any one person's account.

If you list an artifact in the Model Zoo, keep your contact information up to date and tell the MIDAS team if you move institutions or can no longer maintain it.

## Try This

Make a list of every dataset, model, and code repository you have shared in the last five years. For each one, do the "verify like a stranger" steps: open the link from the paper in a private window, download a file, and check that it works. Record which ones fail and why. Then set up the health check workflow for your most important artifacts, and move anything hosted on a personal account to an organizational account or archival repository.

## Further Reading

The Pew Research Center report on link rot {footcite}`pew2024` and Klein et al. on reference rot in scholarly articles {footcite}`klein2014` document the scale of the problem. The Internet Archive's Wayback Machine can sometimes recover lost pages, and you can ask it to save a copy of your project pages today. Saving a page takes one request, which you could add to your release routine:

```python
import requests
for url in ["https://your-lab.github.io/roof-condition/",
            "https://huggingface.co/your-lab/roof-condition-classifier"]:
    r = requests.get(f"https://web.archive.org/save/{url}", timeout=120)
    print(r.status_code, url)
```

The Wayback Machine limits how often pages can be saved, so use this for a handful of key pages, not every file.

## Related Chapters

- [Chapter 2: The MIDAS Model Zoo](../part1/ch02_model_zoo.md)
- [Chapter 9: Pipelines, Automation, and Continuous Integration](../part2/ch09_workflows.md)
- [Chapter 16: Institutional and Archival Repositories](ch16_archival_repositories.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
