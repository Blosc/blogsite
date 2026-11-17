<!--
.. title: Sovereign Tech Agency Award for Blosc2
.. slug: sta-award-blosc2
.. date: 2026-11-17 09:45:00 UTC
.. tags: Sovereign-Tech-Agency, award, Blosc2, C-Blosc2
.. category: posts
.. link:
.. description: The Sovereign Tech Agency awards €286,000 to modernize and harden the C-Blosc2 core foundation.
.. type: text
.. author: Francesc Alted, Scott Prater
-->

We are thrilled to announce that the Blosc2 project has been awarded a contract of **€286,000** from the [Sovereign Tech Agency](https://www.sovereign.tech/) (STA) to modernize, expand, and harden our core C foundation (**C-Blosc2**).

Over the next 15 months, this funding will allow us to tackle long-standing architectural bottlenecks, decouple high-level capabilities from Python, formalize open binary specifications, and establish enterprise-grade security and compatibility testing across the entire Blosc ecosystem.

<img src="/images/Blosc2-Project-STA.png" alt="Main Goals of the Blosc2 Project for the Sovereign Tech Agency" style="width: 100%; max-width: 500px; height: auto; display: block; margin: 0 auto;">

<!-- TEASER_END -->

---

## Why This Matters: Breaking Free of the Python Silo

Originally started 16 years ago, Blosc has evolved into a high-performance data container and meta-compressor that powers core tools in use throughout the scientific and data engineering communities.
Today, it serves as a critical underlying dependency in foundational projects such as [Zarr](https://github.com/zarr-developers/zarr-python) (via [numcodecs](https://github.com/zarr-developers/numcodecs)), [PyTables](https://www.pytables.org/), [HDF5](https://www.hdfgroup.org/solutions/hdf5/) (via [hdf5plugin](https://hdf5plugin.readthedocs.io/en/stable/)), and deep-learning pipelines like [DKFZ’s nnU-Net](https://github.com/MIC-DKFZ/nnUNet).
Blosc and Blosc2 process petabytes of data daily in a wide variety of applications in fields as diverse as synchrotron physics, climate modeling, medical imaging, quantitative finance, and many others. The Python package alone sees between 2 and 4 million downloads every month.

Blosc2's wide adoption has created an architectural imbalance: many of its most powerful innovations - such as hierarchical structures (`DictStore`), columnar storage with segment indexing (`CTable`), and direct mathematical expression evaluation on compressed data -— are implemented exclusively within our high-level Python layer (`Python-Blosc2`).

While prototyping in Python has allowed us to develop the toolkit rapidly, it has imposed a barrier to adoption for developers in **C/C++, Rust, Julia, Go, or WebAssembly**, who cannot leverage these modern capabilities without embedding a full Python runtime.
Furthermore, the absence of formal, vendor-neutral format specifications for Blosc2 means that third-party tools cannot independently implement or verify readers and writers for these advanced containers.

Thanks to the Sovereign Tech Agency, we can now bring these advanced features directly into the foundational **C-Blosc2** engine, making them universally accessible, faster, and truly language-agnostic.

---

## The Roadmap for C-Blosc2

Our 15-month work plan is organized into four key pillars that are designed to mature C-Blosc2 into an open, secure, and universal data standard.

### 1. Open Data Standards & Native C Containers

**Data should never be locked inside a specific programming language**

Today, several of Blosc2's most powerful data structures -— such as dictionary (or hierarchical) stores (`DictStore`), embed stores (`EmbedStore`) and columnar tables (`CTable`) —- are implemented only in Python.

We are drafting formal, vendor-neutral open specifications (RFC blueprints) that will define down to the byte level how this data is structured. At the same time, we are building clean, native C implementations for all of them. This means any software written in C/C++, Rust, Julia, Go, or WebAssembly will be able to create, read, and write Blosc2 datasets natively, with guaranteed cross-platform compatibility.

All specifications will be reviewed through open community discussions and endorsed by the reactivated **Blosc Steering Council**, to make sure that the specifications meet the needs of the broader community of developers.

### 2. Intelligent Slicing & Fast Data Skipping

**The data you need should always be easy and fast to retrieve**

Scientific datasets - such as 3D medical scans, climate projections, or massive financial tables - are often gigabytes or terabytes in size. In practice, researchers rarely need the entire dataset all at once; they usually want to zoom in on a specific region or query a subset of rows.

We are bringing advanced multidimensional slicing (such as strided slices, boolean masks and other sophisticated indexes) and array/columnar indexing directly into the C core. This will allow Blosc2 to intelligently inspect compressed data and "prune" (skip) irrelevant chunks entirely. As a result, queries and data slices will load significantly faster while consuming only a fraction of system memory.

### 3. Computing Directly on Compressed Data (Zero Dependencies)

**Data analysis should exploit hardware capabilities as much as possible**

The conventional way to analyze data is to decompress it first, load it into memory, and then run calculations. But moving uncompressed data between RAM and the processor is often the single biggest performance bottleneck on modern hardware.

We are embedding a tiny, high-performance math engine (`miniexpr`) directly into C-Blosc2. This will enable Blosc2 to evaluate mathematical expressions and table queries (for example, finding all records where `temperature > 30`) directly as data streams through the CPU cache, without the need to first decompress whole datasets into RAM. Best of all, this engine will be completely self-contained in C, with **zero external runtime dependencies** (no NumPy or Python required).

### 4. Built-in Data Encryption & Hardened Security

**Data should never be exposed, compromised, or altered by unauthorized hands**

As Blosc2 becomes a critical building block for sensitive medical, scientific, and enterprise data pipelines, privacy and security are paramount concerns.

We are introducing native, transparent software encryption to C-Blosc2, enabling data to be encrypted and authenticated at rest.  Alongside encryption, we are systematically hardening the library’s defenses: expanding continuous fuzz testing with Google OSS-Fuzz and introducing static analysis into continuous integration to detect memory errors, undefined behavior, and other potential vulnerabilities. We are also establishing a formal vulnerability disclosure policy (SECURITY.md) with standardized CVE reporting workflows, and documenting a risk-based approach to security reviews. Future independent third-party audits will be considered according to security needs and available funding.

---

Naturally, each of these milestones will be accompanied by rigorous compatibility testing and integration testing across common downstream libraries (such as PyTables, hdf5plugin and DKFZ’s nnU-Net) before final release, ensuring that existing applications continue to run seamlessly.

Finally, we will carry out a thorough documentation overhaul that will include a comprehensive C API reference, clear tutorials, and in-depth articles highlighting the new capabilities. Crucially, we want to ensure Blosc2 remains accessible not just to users, but to future developers. Blosc2's engaged community can grow and thrive only if there is a clearly articulated, welcoming onboarding path for new contributors.

---

## The Team and Resource Commitment

Financial support is crucial, but enduring software ultimately depends on the work of experienced and passionate people.
We have assembled an A-team to carry out this 15-month effort:

- **Héctor Martínez (Junior Systems & Python Engineer):** We are very pleased to welcome Héctor as a full-time developer on the project. A recent Computer Science graduate, Héctor will take ownership of the core C container implementations, continuous integration (CI) matrices, cross-version compatibility test suites, and contributor onboarding support.
- **Scott Prater (Lead Technical Writer):** Former Governance Chair of the Fedora Project, Digital Library Strategist at the University of Wisconsin–Madison, and a long-time colleague who has helped with communications for Blosc and Blosc2 since its earliest days, Scott will lead the documentation overhaul, contributor onboarding guides, and technical blog posts.
- **J. David Ibáñez (Senior Systems Architect):** A long-standing core developer of the Blosc ecosystem with deep expertise in C-Blosc2 internals, packaging, and high-performance extensions, J. David will lead development of the data encryption subsystem, fuzzing harnesses, and advanced multidimensional slicing.
- **Francesc Alted (Project Founder & Lead Architect):** Creator of Blosc, PyTables, and CEO of [ironArray SLU](https://ironarray.io). In his role as project lead and senior software engineer, Francesc will oversee the systems architecture, core C development, compute engine integration, indexed query support, and community governance.

---

## Acknowledgments & Looking Ahead

We would like to express our deepest gratitude to the **Sovereign Tech Agency** for supporting this effort and providing the investment to make this project possible. 
Open source has become a critical foundation for modern scientific discovery and digital infrastructure, yet foundational libraries often struggle with long-term maintenance and sustainability.
The Sovereign Tech Agency's proactive mission to invest in and harden critical open-source infrastructure is essential to keeping the open digital commons resilient, secure, and autonomous.

We are especially thankful to **Jakob Kilian** and **Paloma Oliveira** from the Sovereign Tech Agency for their warm welcome, patience, and expert guidance throughout the onboarding and contracting process. Their advice was invaluable in helping us shape a roadmap that best serves both the project and the wider data community.

Our entire team is excited to embark on this new chapter.
We look forward to sharing our progress with you in the months ahead!

The Blosc Development Team  
**Compress Better, Compute Bigger, Share Faster**
