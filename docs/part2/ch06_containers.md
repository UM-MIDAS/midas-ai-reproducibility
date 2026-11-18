# Chapter 6: Containers for Reproducible Models

:::{admonition} What You Will Learn
:class: tip

- When a container is worth the effort for a model or analysis
- How to write a Dockerfile that packages a trained model with its environment
- How to build GPU-enabled images
- How to run containers on U-M's Great Lakes cluster using Apptainer
- How to use dev containers so collaborators can start working in one click
- Where and how to publish container images
:::

## Why Containers for Models

A lockfile (Chapter 5) pins your Python or R packages. A container goes further. It packages an operating system, system libraries, a language runtime, your packages, your code, and optionally your model weights into a single image that runs the same way on any machine with a container runtime {footcite}`boettiger2015`. If a lockfile is a precise recipe, a container is the finished meal, sealed and ready to heat.

For AI models this matters more than for most research code. Deep learning stacks involve layers that Python lockfiles cannot touch: CUDA libraries, cuDNN, system packages for image and audio processing, and sometimes compiled extensions that only build on specific Linux versions. A container captures all of it.

Containers are not always necessary. If your project is pure Python with no GPU and no unusual system dependencies, a lockfile is usually enough. Reach for a container when one or more of these is true:

- Your model needs a GPU and a specific CUDA version.
- Your code depends on system libraries (GDAL, FFmpeg, OpenCV builds, and so on).
- Collaborators or users are on different operating systems and hitting installation problems.
- You want someone to run your model with a single command and no setup.
- You need the environment to keep working for many years, even after packages disappear from public indexes.

## Key Terms

An **image** is a read-only template: the packaged environment. A **container** is a running instance of an image. A **Dockerfile** is a text file with step-by-step instructions for building an image. A **registry** is a server that stores images, such as Docker Hub or GitHub Container Registry. **Docker** is the most common tool for building and running images on laptops and cloud servers. **Apptainer** (formerly Singularity) is the equivalent designed for shared high-performance computing clusters, and it can run Docker images.

## A Minimal Model Container

Here is an annotated Dockerfile for serving a trained PyTorch image classifier from the command line. It uses uv and a lockfile from Chapter 5.

```dockerfile
# 1. Pin the base image to an exact version (never use :latest)
FROM python:3.11.9-slim

# 2. Install system libraries your code needs
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3. Install uv, pinned to a specific version
COPY --from=ghcr.io/astral-sh/uv:0.4.20 /uv /usr/local/bin/uv

WORKDIR /app

# 4. Install dependencies first, so this layer is cached between code changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
# Put the project's virtual environment first on PATH, so plain `python` uses it
ENV PATH="/app/.venv/bin:$PATH"

# 5. Copy code and model weights
COPY src/ ./src/
COPY scripts/predict.py ./scripts/
COPY models/classifier.safetensors ./models/

# 6. Record provenance as image metadata
LABEL org.opencontainers.image.source="https://github.com/your-lab/your-model" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.licenses="Apache-2.0"

# 7. Define how the container runs
ENTRYPOINT ["python", "/app/scripts/predict.py"]
```

The entry point calls `python` directly rather than `uv run`, because `uv run` may try to update the environment at startup, which fails in read-only settings such as Apptainer on a cluster.

The `scripts/predict.py` that the container runs can be very small. What matters is that it takes inputs from the command line and prints machine-readable output, so the container can be used in pipelines as well as by hand:

```python
# scripts/predict.py
import argparse, json, sys
from pathlib import Path

import torch
from PIL import Image
from safetensors.torch import load_file

sys.path.insert(0, "/app/src")
from my_project.model import build_model, preprocess, LABELS

parser = argparse.ArgumentParser(description="Classify roof condition in house photos.")
parser.add_argument("images", nargs="+", type=Path, help="Image files to classify")
parser.add_argument("--weights", default="/app/models/classifier.safetensors")
args = parser.parse_args()

device = "cuda" if torch.cuda.is_available() else "cpu"
model = build_model(num_classes=len(LABELS))
model.load_state_dict(load_file(args.weights))
model.to(device).eval()

with torch.no_grad():
    for path in args.images:
        x = preprocess(Image.open(path).convert("RGB")).unsqueeze(0).to(device)
        probs = model(x).softmax(dim=-1).squeeze(0).tolist()
        print(json.dumps({"file": path.name,
                          "label": LABELS[max(range(len(probs)), key=probs.__getitem__)],
                          "probabilities": dict(zip(LABELS, [round(p, 4) for p in probs]))}))
```

Each line of output is a JSON record, which is easy to collect into a table later.

Build and run it:

```bash
docker build -t my-classifier:1.0.0 .
docker run --rm -v "$PWD/images:/data" my-classifier:1.0.0 /data/example.jpg
```

The `-v` flag mounts a folder from your computer into the container, so the model can read your input files without copying them into the image.

A few choices in this Dockerfile matter for reproducibility.

**Pin the base image.** `python:3.11.9-slim` is much better than `python:3` or `python:latest`. For the strongest guarantee, pin by digest (`python:3.11.9-slim@sha256:...`), which refers to one exact image that can never change. Tags can be moved to point at a new image; digests cannot.

**Order layers from least to most frequently changed.** Docker caches each step. Installing dependencies before copying your code means that editing a Python file does not trigger a full reinstall.

**Decide whether weights belong in the image.** Baking weights in makes the image fully self-contained, which is ideal for archiving. But it makes images large and couples code releases to model releases. An alternative is to download weights at startup from Hugging Face using a pinned revision (Chapter 14). For archival purposes, including weights is safer.

**Use `.dockerignore`.** Like `.gitignore`, it keeps data folders, virtual environments, and secrets out of the build. Without one, `COPY` commands can send gigabytes of data to the build and, worse, copy a `.env` file containing credentials into a public image.

```text
# .dockerignore
.git
.venv
.env
data/
runs/
mlruns/
notebooks/
**/__pycache__
**/.ipynb_checkpoints
```

### Hands-On: Check What You Built

After building, a few commands confirm that the image contains what you think it does:

```bash
# Which Python and package versions are inside?
docker run --rm --entrypoint python my-classifier:1.0.0 \
    -c "import sys, torch; print(sys.version); print(torch.__version__)"

# Open a shell inside the image to look around
docker run --rm -it --entrypoint bash my-classifier:1.0.0

# How big is it, and which steps made it big?
docker image ls my-classifier
docker history my-classifier:1.0.0

# Record the immutable digest (available after pushing to a registry)
docker image inspect --format '{{index .RepoDigests 0}}' ghcr.io/your-lab/my-classifier:1.0.0
```

### Apple Silicon and Cluster Architectures

Macs with Apple Silicon build images for the `arm64` processor architecture by default, while Great Lakes and most cloud servers use `amd64` (x86-64). An image built on a recent Mac may fail on the cluster with an "exec format error." Build for the target platform explicitly:

```bash
docker buildx build --platform linux/amd64 -t ghcr.io/your-lab/my-classifier:1.0.0 --push .
# or build for both, so the same tag works everywhere
docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/your-lab/my-classifier:1.0.0 --push .
```

## GPU Images

To use a GPU inside a container, two things must line up. On the host, you need an NVIDIA driver and the NVIDIA Container Toolkit, which lets Docker pass the GPU through. Inside the image, you need CUDA libraries compatible with that driver.

The simplest approach is to start from an official image that already includes CUDA. NVIDIA publishes `nvidia/cuda` base images, and PyTorch publishes images with PyTorch and CUDA preinstalled:

```dockerfile
FROM pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime
```

Then run the container with GPU access:

```bash
docker run --rm --gpus all my-gpu-model:1.0.0
```

The host driver must be new enough for the CUDA version in the image. Newer drivers support older CUDA versions, but not the other way around. Record the CUDA version in your README and model card.

Consider also providing a CPU-only image. Many users who want to try your model will not have a GPU, and inference for a single example is often fast enough on a CPU (Chapter 21).

## Containers on Great Lakes and Other HPC Clusters

Docker is not available on U-M's HPC clusters (Great Lakes, Armis2, and Lighthouse), because Docker requires administrator privileges that are unsafe on shared systems. Instead, Apptainer (also invoked as `singularity`) is available by default, with no module to load. Apptainer can pull and convert Docker images directly:

```bash
# Convert a Docker image from a registry into an Apptainer image file (.sif)
apptainer pull my-classifier.sif docker://ghcr.io/your-lab/my-classifier:1.0.0

# Run the image's entry point; --nv passes through the NVIDIA GPU
apptainer run --nv my-classifier.sif images/example.jpg

# Or run any command inside it
apptainer exec --nv my-classifier.sif python /app/scripts/predict.py images/example.jpg
```

Apptainer automatically mounts your home directory and current working directory, so your data files are usually visible without extra flags. Data in other locations, such as Turbo or scratch, can be mounted with `--bind`. Here is a complete Slurm batch script that classifies a folder of images on a GPU node:

```bash
#!/bin/bash
#SBATCH --job-name=roof-predict
#SBATCH --account=YOUR_SLURM_ACCOUNT
#SBATCH --partition=gpu
#SBATCH --gpus=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail
IMAGES=/nfs/turbo/your-lab/roof-images

# Record exactly which image ran, for provenance
sha256sum my-classifier.sif

apptainer run --nv --bind "$IMAGES":/data my-classifier.sif /data/*.jpg \
    > results/predictions-$SLURM_JOB_ID.jsonl
```

Submit it with `sbatch predict.sbat` and check progress with `squeue --me`. The partition and account names above are placeholders; use the ones from your ARC allocation. Check the ARC containers documentation for current details and examples.

You can also build Apptainer images directly from a definition file, which plays the same role as a Dockerfile. Building usually requires administrator rights or the `--fakeroot` option, so it is often easiest to build on your own Linux machine or convert from Docker:

```text
# my-classifier.def
Bootstrap: docker
From: ghcr.io/your-lab/my-classifier:1.0.0

%labels
    Version 1.0.0

%runscript
    exec python /app/scripts/predict.py "$@"
```

This workflow is one of the most useful reasons to containerize: you can build and test an image on your laptop with Docker, push it to a registry, and run the identical environment on Great Lakes for large jobs.

## Dev Containers and Codespaces

Containers are not only for shipping finished models. A **dev container** is a container configured as a development environment, described by a `.devcontainer/devcontainer.json` file in your repository. Editors like VS Code can open your project inside it automatically, and GitHub Codespaces can launch it in the cloud with one click.

```json
{
  "name": "my-project",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "postCreateCommand": "pip install uv && uv sync --frozen",
  "customizations": {
    "vscode": { "extensions": ["ms-python.python", "ms-toolsai.jupyter"] }
  }
}
```

For collaborators, students, and reviewers, this removes almost all setup friction: they open the repository and have a working environment within minutes. It also forces you to keep your environment specification complete, since anything missing will show up immediately.

## Publishing Images

An image that only exists on your laptop does not help anyone else. Push it to a registry.

**GitHub Container Registry (ghcr.io)** is convenient if your code is on GitHub. Images are linked to the repository, and public images are free to store and pull. You can build and push automatically from GitHub Actions whenever you create a release (Chapter 9).

**Docker Hub** is the most widely known registry. Free accounts can host public images, though unauthenticated pulls are rate-limited.

Tag images with meaningful versions (`1.0.0`, `paper-2026`) that match your Git tags, and record the image digest in your README and paper. Tags can be moved; digests identify one exact image forever.

### Hands-On: Push to GitHub Container Registry

```bash
# Create a GitHub personal access token with the write:packages scope, then:
echo "$GITHUB_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
docker tag my-classifier:1.0.0 ghcr.io/your-lab/my-classifier:1.0.0
docker push ghcr.io/your-lab/my-classifier:1.0.0
```

New packages on GHCR are private by default. Change the visibility to public in the package settings on GitHub so that others, and Apptainer on the cluster, can pull it without logging in.

Better still, let GitHub Actions build and push the image every time you publish a release. This guarantees the image matches the tagged code, rather than whatever happened to be on your laptop:

```yaml
# .github/workflows/publish-image.yml
name: publish-image
on:
  release:
    types: [published]
permissions:
  contents: read
  packages: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.event.release.tag_name }}
```

Repository names on GHCR must be lowercase, so if your GitHub organization or repository name contains capital letters, write the image name out in lowercase instead of using `${{ github.repository }}`.

**Registries are not archives.** Images can be deleted, accounts can lapse, and registry policies change. For long-term preservation, export the image to a file and deposit it with your other artifacts:

```bash
docker save my-classifier:1.0.0 | gzip > my-classifier-1.0.0.tar.gz
```

This file can be deposited in Zenodo or Deep Blue Data (Chapter 16) alongside your code and data, and anyone can restore it later:

```bash
gunzip -c my-classifier-1.0.0.tar.gz | docker load
# or, on a cluster, convert the archive directly to an Apptainer image
gunzip my-classifier-1.0.0.tar.gz
apptainer build my-classifier.sif docker-archive://my-classifier-1.0.0.tar
```

Record a checksum of the archive too (Chapter 20). Also deposit the Dockerfile, since it documents how the image was built.

## Try This

Take a Model Zoo model, or one of your own, and write a Dockerfile for it using the template above. Build it and run a prediction on your laptop. Push it to GitHub Container Registry, then log in to Great Lakes, pull it with Apptainer, and run the same prediction. Compare the outputs. If they match, you have a portable, reproducible model.

## Further Reading

Boettiger's paper {footcite}`boettiger2015` remains a clear introduction to why containers matter for research. The Docker, Apptainer, and Dev Containers documentation all have good tutorials. The companion workshop repository for the AI in Research Handbook, [midas-env-conda-docker-workshop](https://github.com/xiaosuhu/midas-env-conda-docker-workshop), walks through building a minimal Python container step by step.

## In the Model Zoo

A container image with a one-line run command is one way for a Model Zoo entry to reach the "Reproducible" tier. When you submit, include the registry address, the image digest, and the command.

## Related Chapters

- [Chapter 5: Managing Software Environments](ch05_environments.md)
- [Chapter 9: Pipelines, Automation, and Continuous Integration](ch09_workflows.md)
- [Chapter 21: AI on Modest Hardware](../part4/ch21_low_resource.md)

```{footbibliography}
```

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
