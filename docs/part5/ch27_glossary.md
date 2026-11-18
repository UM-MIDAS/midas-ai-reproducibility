# Chapter 27: Glossary

:::{admonition} What You Will Learn
:class: tip

- Plain-language definitions of key terms used in this handbook
:::

Adapter (LoRA adapter)
: A small set of trained parameters added to a frozen base model during parameter-efficient fine-tuning. Adapters can be shared separately from the base model. (Chapter 21)

Alt text (alternative text)
: A text description of an image that is read aloud by screen readers and shown when the image cannot load. (Chapter 23)

Apptainer
: A container system designed for shared HPC clusters, formerly called Singularity. It can run Docker images without administrator privileges. (Chapter 6)

Archival repository
: A repository designed for long-term preservation, with persistent identifiers, fixity checks, and a commitment to keep content available. Examples: Deep Blue Data, Zenodo, ICPSR. (Chapter 16)

Artifact
: Any research output other than the paper itself: code, data, trained models, containers, notebooks, or demos.

CARE principles
: Collective benefit, Authority to control, Responsibility, and Ethics: principles for Indigenous data governance that complement FAIR. (Chapter 3)

Checksum (hash)
: A short string calculated from a file's contents, such as a SHA-256 hash. If a single bit of the file changes, the checksum changes, so it can be used to verify downloads. (Chapter 20)

CITATION.cff
: A machine-readable file in a repository that tells people how to cite the software or model. GitHub and Zenodo read it automatically. (Chapter 10)

Clean-room rerun
: Reproducing your own work on a fresh machine using only the public artifacts and written instructions. (Chapter 11)

Community hub
: A platform optimized for discovering and using artifacts, such as Hugging Face, Kaggle, or GitHub. Hubs generally do not make formal preservation commitments. (Chapter 13)

Concept DOI / version DOI
: A version DOI identifies one specific version of a record; a concept DOI always resolves to the latest version. (Chapter 16)

Container / image
: An image is a packaged, read-only environment including an operating system, libraries, and code. A container is a running instance of an image. (Chapter 6)

Continuous integration (CI)
: Automatically building and testing code on a server whenever changes are pushed, or on a schedule. (Chapter 9)

Controlled access
: Sharing data only with approved users who agree to specific conditions, such as through a data use agreement or data enclave. (Chapter 19)

Croissant
: A machine-readable metadata format for machine learning datasets, with a Responsible AI extension. (Chapter 17)

Data dictionary (codebook)
: A table describing every variable in a dataset: meaning, type, units, allowed values, and missing value codes. (Chapter 17)

Data Management and Sharing Plan (DMS Plan)
: A document, required by NIH and other funders, describing what data a project will generate and how they will be managed and shared. (Chapter 12)

Datasheet (dataset card)
: A document describing a dataset's motivation, composition, collection, processing, uses, distribution, and maintenance. (Chapter 17)

De-identification
: Removing or transforming information that could identify individuals in a dataset. (Chapter 19)

Determinism
: The property of producing exactly the same output from the same input every time. Many GPU operations are not deterministic by default. (Chapter 7)

Distillation (knowledge distillation)
: Training a smaller "student" model to imitate a larger "teacher" model. (Chapter 21)

Dockerfile
: A text file with step-by-step instructions for building a container image. (Chapter 6)

DOI (Digital Object Identifier)
: A persistent identifier that always resolves to the current location of a research output. (Chapter 16)

FAIR principles
: Findable, Accessible, Interoperable, and Reusable: principles for well-managed research data. FAIR4RS adapts them for research software. (Chapter 3)

Gated repository
: A public repository whose files can only be downloaded after a user accepts conditions and, optionally, is approved. (Chapter 14)

GGUF
: A file format for quantized models used by llama.cpp and related tools for efficient CPU and laptop inference. (Chapter 21)

k-anonymity
: A measure of identifiability: every record shares its quasi-identifier values with at least *k* − 1 other records. (Chapter 19)

Link rot / reference rot
: The tendency of links to stop working (link rot) or to point to content that has changed (reference rot) over time. (Chapter 20)

Lockfile
: A machine-generated file recording the exact version of every package in an environment, including dependencies, often with hashes. Examples: `uv.lock`, `conda-lock.yml`, `renv.lock`. (Chapter 5)

Membership inference
: An attack that determines whether a particular record was in a model's training data. (Chapter 19)

Model card
: A document describing a trained model's intended use, training data, evaluation, performance across subgroups, and limitations. (Chapter 10)

ONNX
: Open Neural Network Exchange, an open file format for trained models that runs in ONNX Runtime on many platforms without the original training library. (Chapter 21)

ORCID
: A persistent identifier for an individual researcher. (Chapter 10)

Pipeline (workflow)
: A set of analysis steps and their dependencies written as code, so the full analysis can be rerun with one command. (Chapter 9)

Provenance
: The record of where a result or artifact came from: the code, data, configuration, and environment that produced it. (Chapter 8)

Quantization
: Storing model weights at lower numerical precision (for example, 8-bit or 4-bit) to reduce memory use and speed up inference. (Chapter 21)

Quasi-identifier
: An attribute that does not identify someone on its own, such as age or ZIP code, but can in combination with others or with outside data. (Chapter 19)

Replicability
: Obtaining consistent results across studies that collect their own data to answer the same question. (Chapter 1)

Reproducibility
: Obtaining consistent results using the same data, code, and conditions of analysis. (Chapter 1)

Revision
: A specific version of a Git or Hugging Face repository, identified by a commit hash or tag. (Chapter 14)

Safetensors
: A file format for model weights that stores only tensors and cannot execute code when loaded. (Chapter 14)

Seed (random seed)
: The starting value for a pseudo-random number generator. Setting it makes random operations repeatable. (Chapter 7)

Smoke test
: A quick run of a pipeline on a tiny data sample to check that it executes end to end. (Chapter 9)

SPDX identifier
: A standard short name for a license, such as `MIT` or `Apache-2.0`, often placed at the top of source files. (Chapter 18)

Specification (environment specification)
: A human-written list of required packages and version ranges, such as `pyproject.toml` or `environment.yml`. Compare with lockfile. (Chapter 5)

Steward
: The person responsible for maintaining a shared artifact and responding to questions over time. (Chapter 20)

Synthetic data
: Artificial data generated to mimic the statistical properties of real data. (Chapters 17 and 19)

Tombstone
: A landing page that remains after an artifact is withdrawn, explaining what it was and why it was removed. (Chapters 16 and 20)

WCAG
: Web Content Accessibility Guidelines, the international standard for web accessibility. Level AA of WCAG 2.1 is required for public universities under the ADA Title II rule. (Chapter 23)

---

**Questions or feedback?** [Open an issue on GitHub](https://github.com/UM-MIDAS/midas-ai-reproducibility/issues)
