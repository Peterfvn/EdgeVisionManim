# EdgeVision: Edge-Deployed Nanopore Sequencing for Rapid Sepsis Pathogen ID
## Project Outline & Literature Survey

---

## Landscape Summary

The literature reveals a clear picture: nanopore sequencing for sepsis pathogen identification is an **active clinical research area**, but nearly all existing workflows still depend on cloud or centralized HPC for the heavy compute (basecalling). Your project's edge computing angle — co-locating GPU-accelerated basecalling with the sequencer at the hospital bedside — fills a genuine architectural gap in the literature. Nobody has cleanly framed this as an **edge computing problem** with explicit task partitioning, which is exactly what your class project requires.

### Key Papers Found (Candidate Citations)

| # | Paper / Source | Key Contribution | How It Fits Your Project |
|---|---------------|-----------------|------------------------|
| 1 | Chen et al. (2025), *BMC Infectious Diseases* — "Clinical application of targeted nanopore sequencing in pathogen detection in patients with sepsis" | TNPseq achieved **94.4% positivity rate** vs 30% for culture | Motivation: proves nanopore superiority over culture for sepsis |
| 2 | Taxt et al. (2020), *Scientific Reports* — "Rapid identification of pathogens, antibiotic resistance genes and plasmids in blood cultures by nanopore sequencing" | Pathogen ID in **10 minutes** of sequencing; AMR genes within **1 hour** | Processing estimates: real-world timing benchmarks for your pipeline |
| 3 | Abouelkhair et al. (2024), *Scientific Reports* — "Short turnaround time of seven to nine hours from sample collection" | End-to-end TAT of **7–9 hours** including shortened incubation + nanopore sequencing | Architecture: establishes the baseline your edge system improves upon |
| 4 | Harris et al. (2024), *Microbiology Spectrum* — "Rapid nanopore sequencing and predictive susceptibility testing of positive blood cultures from intensive care patients with sepsis" | ONT sequencing from blood cultures with AST prediction; faster than phenotypic methods but notes accuracy limitations | Trade-offs: honest about current limitations (accuracy vs speed) |
| 5 | Seymour et al. (2017), *AJRCCM* — "The Timing of Early Antibiotics and Hospital Mortality in Sepsis" | Each hourly delay → **1.8% increased mortality** in septic shock (35,000 patients, 21 EDs) | Motivation: the clinical urgency that justifies edge deployment |
| 6 | Oxford Nanopore — Dorado basecaller documentation & GitHub | GPU-accelerated basecalling; runs on NVIDIA Pascal+; **8 GB+ vRAM minimum**; multi-GPU linear scaling | Architecture: defines the edge node hardware requirements |
| 7 | Oxford Nanopore — GridION Mk1 specs | Benchtop device, **5 flow cells**, integrated GPU; basecalling uses only **~10% of GPU**, leaving 90% for downstream analysis | Architecture: this IS your edge node — it already exists as hardware |
| 8 | Van Uffelen et al. (2024), *Scientific Data* — "Benchmarking bacterial taxonomic classification using nanopore metagenomics data" | Comprehensive comparison of Kraken2, Centrifuge, Bracken, etc. for nanopore reads | Processing details: justifies your classifier choice |
| 9 | MARTi (2025), *PMC* — "Real-time analysis and visualization of nanopore metagenomic samples" | Open-source real-time classification tool supporting Kraken2/Centrifuge/BLAST; can run on a laptop | Architecture: proves real-time local classification is feasible |
| 10 | AWS Benchmarks (2023) — "Benchmarking the Oxford Nanopore Technologies basecallers on AWS" | Dorado achieves **490M samples/sec** on p4d.24xlarge (A100 GPUs); benchmarks across 20 GPU types | Processing estimates: lets you estimate edge vs cloud throughput |

---

## Section-by-Section Outline

### 1. Motivation and Use Case (~5 min presentation / ~1 page report)

**Story Arc:** Open with the human stakes, then reveal the bottleneck, then show how edge computing solves it.

#### 1.1 The Sepsis Crisis
- Sepsis: ~49 million cases/year globally, ~11 million deaths (Rudd et al., Lancet 2020 — widely cited stat)
- Mortality rate for septic shock remains **30–50%**
- Surviving Sepsis Campaign guidelines: administer antibiotics within **1 hour** of recognition
- Seymour et al. (2017): each hourly delay in antibiotics associated with **1.8% absolute increase** in mortality for septic shock patients
- The problem: clinicians must prescribe antibiotics *before* they know what the pathogen is → broad-spectrum overuse → AMR crisis

#### 1.2 The Diagnostic Bottleneck
- **Blood culture** (current gold standard): 48–96 hour turnaround; only ~30% positivity rate
- **Illumina mNGS**: better sensitivity but still requires batching, library prep, cloud upload → 24–72 hours
- **Nanopore sequencing** (ONT): real-time, long-read, portable — but current workflows still send data to cloud (EPI2ME) or require HPC access

#### 1.3 The Edge Computing Opportunity
- **Core thesis:** By co-locating GPU-accelerated basecalling and taxonomic classification with the nanopore sequencer at the hospital, we can collapse the diagnostic loop from days → **under 2 hours**
- Privacy: raw genomic data (patient cfDNA is in the sample) never leaves the hospital network
- Reliability: no dependency on internet connectivity for time-critical results
- Bandwidth: a single MinION run can generate **30+ GB** of raw signal data — uploading this is impractical under time pressure

#### Manim Animation Ideas (Section 1)
- **Timeline comparison**: Animated horizontal bar chart showing culture (72h) → Illumina+cloud (24h) → Edge nanopore (2h)
- **Patient journey**: Simple animated figure showing a patient deteriorating while waiting for results vs. rapid treatment with edge

---

### 2. Key Class Concepts (~4 min presentation / woven into ~1.5 pages)

Map each required concept explicitly:

#### 2.1 Latency Reduction
- Cloud path: sample → sequencer → raw data upload (network) → cloud basecalling → cloud classification → results download → clinician
- Edge path: sample → sequencer → **local GPU basecalling** → **local classification** → clinician
- Estimated latency savings: eliminate ~30 min–2 hr network round-trip + cloud queue time
- For real-time streaming basecalling, latency target: **basecalling must keep pace with sequencing** (~450 bases/sec per pore × 512 active pores)

#### 2.2 Task Partitioning / Offloading Decisions
- **Edge tasks** (latency-critical, privacy-sensitive):
  - Basecalling (signal → nucleotide sequence) — GPU-intensive, real-time
  - Read classification (Kraken2/Centrifuge against local DB) — RAM-intensive, fast
  - Preliminary AMR gene detection — clinically urgent
  - Quality filtering and human read removal — privacy-critical
- **Cloud tasks** (latency-tolerant, compute-heavy):
  - Long-term archival and population-level surveillance
  - De novo assembly for novel pathogen characterization
  - Database updates and model retraining
  - Epidemiological dashboards aggregating across hospitals

#### 2.3 Hybrid Edge–Cloud Processing
- Results flow: edge produces actionable clinical report in <2 hours; anonymized/summarized data syncs to cloud asynchronously
- Cloud sends back: updated reference databases, retrained basecalling models, surveillance alerts
- Fallback: if edge node fails, raw POD5 files can be queued and uploaded to cloud for processing (degraded TAT but no data loss)

#### 2.4 Resource Allocation & Orchestration
- **Unified memory model**: Jetson Thor's 128 GB LPDDR5X is shared between CPU and GPU — no PCIe bottleneck for data transfer, but requires careful allocation to avoid contention
  - Budget: ~8 GB Dorado basecalling + ~40 GB Kraken2 standard DB + ~10 GB Bowtie2 human reference + ~8 GB OS/pipeline = ~66 GB, leaving ~62 GB headroom
- **GPU compute partitioning**: basecalling is the most GPU-intensive task; classification (Kraken2) is CPU/RAM-bound — these can run concurrently without GPU contention
- **Power mode orchestration**: Thor supports configurable 40–130W TDP modes; during active sequencing, run at 130W for real-time basecalling; drop to 40W during idle/sync periods to conserve power
- Multi-patient scenario: flow cell multiplexing (barcoding) allows multiple patient samples per run — edge node processes all barcodes in a single pipeline

#### 2.5 Networking Approaches
- Hospital LAN: sequencer → edge GPU node (gigabit Ethernet, <1 ms latency)
- Edge → Cloud: asynchronous sync over hospital WAN/VPN; encrypted; only processed summaries, not raw signal
- Air-gapped mode: edge node can operate completely offline with pre-loaded reference databases

#### 2.6 Bandwidth/Latency Trade-offs
- Raw signal data: **~1–2 TB per PromethION run**, ~30 GB per MinION run
- Basecalled FASTQ: ~10× smaller than raw signal
- Classification report: **kilobytes** — trivially transmittable
- Trade-off: processing locally means you need the GPU, but you eliminate the bandwidth bottleneck entirely for clinical results
- Cloud sync of raw data can happen in background over hours/days for archival

#### Manim Animation Ideas (Section 2)
- **Data flow diagram**: Animated arrows showing data moving from sequencer → edge → cloud, with packet sizes shrinking at each stage
- **Task partitioning visual**: Split screen — edge side (fast, highlighted) vs. cloud side (slow, grayed out) showing what runs where

---

### 3. Architecture Diagram (~included in section 2 timing / ~1.5 pages)

#### 3.1 System Components

**Layer 1 — Data Sources (Bedside)**
- Oxford Nanopore MinION Mk1D or GridION (sequencer hardware)
- Connected to edge node via USB-C (MinION) or integrated (GridION)
- Sample input: patient blood culture or direct cfDNA extraction

**Layer 2 — Edge Node (Hospital Lab / ICU)**
- Hardware: **NVIDIA Jetson AGX Thor** (Blackwell GPU, 128 GB LPDDR5X unified memory, 40–130W TDP)
  - Form factor: ~87×100 mm module — compact enough for bedside or mobile lab cart
  - 2070 FP4 TFLOPS AI compute; Dorado already supports Blackwell architecture
  - 128 GB unified memory: critical — fits Kraken2 standard DB (~30–50 GB) + basecalling workload simultaneously
  - Precedent: ONT's MinIT was built on Jetson TX2; Dorado+MinKNOW confirmed working on Jetson Orin AGX
  - Developer kit: ~$3,499 — realistic for clinical deployment at scale
  - Alternative (current-gen): Jetson AGX Orin (64 GB, 275 TOPS, ~$1,999) — viable but forces use of mini Kraken2 DB (8 GB)
- Connected to MinION Mk1D via USB-C
- Software stack:
  - MinKNOW (device control + data acquisition)
  - Dorado (GPU basecalling — **HAC model**; SUP model likely too compute-intensive for real-time on edge)
  - Kraken2 (taxonomic classification — standard DB fits in 128 GB unified memory)
  - Custom reporting dashboard (real-time pathogen + AMR results to clinician)
- Storage: 1 TB NVMe SSD (ships with dev kit) for raw data + reference databases
- Network: hospital LAN via Ethernet; Wi-Fi 6E for fallback
- Power: runs on standard hospital outlet or battery backup (130W max)

**Layer 3 — Hospital Network**
- Firewall / security boundary
- Results pushed to hospital EMR/EHR system
- HIPAA/GDPR compliance: raw genomic data stays within this boundary

**Layer 4 — Cloud Backend (Asynchronous)**
- Anonymized summary data uploaded for:
  - Epidemiological surveillance (outbreak detection across hospitals)
  - Reference database updates (new pathogen genomes)
  - Model retraining (improved basecalling accuracy)
  - Long-term archival storage
- Services: could be AWS, Azure, or institutional HPC

#### 3.2 Data Flow
```
Patient Blood Sample
       ↓
  DNA Extraction + Library Prep (~30 min)
       ↓
  Nanopore Sequencer (MinION/GridION)
       ↓ raw electrical signal (POD5)
  ┌─────────────────────────────────┐
  │     EDGE NODE (Hospital)        │
  │                                 │
  │  Dorado Basecalling (GPU)       │
  │       ↓ FASTQ/BAM              │
  │  Human Read Removal (Bowtie2)   │
  │       ↓ filtered reads          │
  │  Kraken2 Classification         │
  │       ↓ species report          │
  │  AMR Gene Detection             │
  │       ↓                         │
  │  Clinical Report → Clinician    │
  └─────────────────────────────────┘
       ↓ (async, summarized)
  ┌─────────────────────────────────┐
  │     CLOUD BACKEND               │
  │  - Surveillance aggregation     │
  │  - DB updates                   │
  │  - Archival                     │
  └─────────────────────────────────┘
```

#### Manim Animation Ideas (Section 3)
- **The main architecture animation**: Build the diagram piece by piece — first the sequencer appears, then arrows flow to edge node, processing stages animate sequentially, then results fly to clinician while a slower dotted line goes to cloud
- This could be the centerpiece animation of the presentation

---

### 4. Processing Details and Estimates (~3 min / ~1 page)

#### 4.1 Processing Split

| Task | Location | % of Total Compute | Latency Target |
|------|----------|-------------------|----------------|
| Basecalling (Dorado HAC) | Edge GPU | ~60% | Real-time (keep pace with sequencing) |
| Human read filtering | Edge CPU | ~5% | <1 min per batch |
| Taxonomic classification (Kraken2) | Edge CPU/RAM | ~15% | <10 min total |
| AMR gene detection | Edge CPU | ~10% | <10 min total |
| Report generation | Edge CPU | ~2% | <1 min |
| Surveillance sync + archival | Cloud | ~8% | Hours–days (async) |

**Edge handles ~92% of clinically-relevant compute; cloud handles ~8% (non-urgent)**

#### 4.2 Hardware Estimates for Edge Node (NVIDIA Jetson AGX Thor)

- **GPU**: Blackwell architecture, 2070 FP4 TFLOPS
  - Dorado HAC basecalling: Blackwell GPUs show ~30% speed improvement over prior gen; Thor's compute should comfortably keep pace with a single MinION flow cell in real-time
  - A single MinION flow cell: ~512 active pores × ~450 bases/sec = ~230 Kbases/sec
  - Key constraint: **SUP (super-accurate) model likely cannot sustain real-time on Thor** → must use HAC model (this is a genuine edge trade-off worth discussing)
  - Prior Jetson Orin AGX basecalling benchmarks: ~1.6M samples/sec HAC with Guppy; Dorado on Blackwell Thor expected to be significantly faster
- **Memory**: 128 GB LPDDR5X unified (shared between CPU and GPU)
  - Kraken2 standard database: ~30–50 GB
  - Dorado basecalling working set: ~4–8 GB
  - OS + pipeline + Bowtie2 index: ~8–10 GB
  - **~60 GB headroom** — comfortable margin; no memory contention
  - Compare: Jetson Orin (64 GB) would force use of mini Kraken2 DB (8 GB), sacrificing classification accuracy
- **Storage**: 1 TB NVMe SSD (included with dev kit)
  - One MinION run raw data: ~30 GB
  - Reference databases: ~50–100 GB
  - Temporary working space: ~200 GB
- **CPU**: ARM Neoverse V3AE cores
  - Kraken2 classification is CPU-bound and parallelizable
- **Power**: 40–130W configurable TDP (vs. ~350W+ for a workstation with RTX 4090)
  - Can run on hospital UPS / battery backup
  - Power efficiency is a key edge advantage for deployment in resource-limited settings
- **Network**: Gigabit Ethernet + Wi-Fi 6E
- **Form factor**: ~87×100 mm module — fits on a lab cart next to the MinION
- **Cost**: ~$3,499 (dev kit) — compare to ~$5,000–10,000 for a GPU workstation

#### 4.3 Timing Estimates (End-to-End)

| Stage | Time Estimate | Notes |
|-------|--------------|-------|
| DNA extraction + library prep | 30–45 min | Rapid kits exist (ONT Rapid Sequencing Kit) |
| Sequencing + real-time basecalling | 30–60 min | Sufficient reads for ID within 10–30 min of sequencing |
| Human read removal | ~2 min | Bowtie2, runs in parallel |
| Kraken2 classification | ~5–10 min | Against standard DB; initial results within minutes |
| AMR gene detection | ~5–10 min | Alignment against CARD database |
| Report generation | <1 min | Automated |
| **Total time-to-result** | **~75–120 min** | **vs. 48–96 hours for culture** |

Literature validation:
- Taxt et al.: pathogen ID possible after just 10 min of sequencing
- Abouelkhair et al.: 7–9 hour total TAT (their workflow includes longer incubation)
- Your edge approach cuts out the cloud/HPC queuing step entirely

#### 4.4 Data Rate Estimates
- MinION raw signal output: ~50–100 MB/min
- Basecalled FASTQ output: ~5–10 MB/min (10× reduction)
- Classification report: ~10 KB per batch
- Cloud sync payload (per run, summarized): ~1–5 MB

#### Manim Animation Ideas (Section 4)
- **Animated timeline**: Clock ticking with pipeline stages appearing sequentially, showing cumulative time
- **Edge vs Cloud race**: Two parallel timelines — edge finishes in <2 hours while cloud path is still uploading data

---

### 5. Trade-offs, Scalability, and Conclusion (~3 min / ~1 page)

#### 5.1 Advantages of Edge Approach vs. Pure Cloud
- **Speed**: eliminates network transfer + cloud queue latency
- **Privacy**: patient genomic data stays on-premise (HIPAA/GDPR compliance simplified)
- **Reliability**: no internet dependency for time-critical clinical decisions
- **Bandwidth**: avoids uploading 30+ GB of raw data under time pressure
- **Cost** (long-term): avoids per-run cloud compute charges once hardware is purchased

#### 5.2 Advantages of Edge vs. Pure On-Premise (No Cloud)
- Cloud provides population-level surveillance (outbreak detection)
- Cloud enables model updates and database refreshes
- Cloud offers disaster recovery / data redundancy

#### 5.3 Limitations
- **Upfront cost**: Jetson Thor (~$3,499) + MinION (~$1,000) = ~$4,500 per edge node — affordable for large hospitals, but challenging for rural/low-resource settings
- **Compute constraint**: SUP (super-accurate) basecalling model likely cannot run in real-time on Thor → must use HAC model, accepting slightly lower accuracy (~99% vs ~99.5% raw read accuracy). This is a **genuine edge trade-off**: accuracy vs. latency
- **Unified memory contention**: 128 GB shared between CPU and GPU — basecalling + Kraken2 running simultaneously could create memory bandwidth pressure; requires careful orchestration
- **Database freshness**: local Kraken2 DB may lag behind cloud-updated versions → periodic sync needed
- **Maintenance**: hospitals need staff capable of managing embedded Linux devices, software updates, database refreshes
- **Regulatory**: not yet FDA-approved for clinical diagnostics (all current studies are "research use only")
- **Sample prep**: still requires wet-lab steps (~30 min) that edge computing can't accelerate
- **Thermal management**: Thor at sustained 130W in a clinical environment requires attention to cooling (community reports of heat-induced reboots on Jetson devices under sustained GPU load)

#### 5.4 Scalability Considerations
- **Single hospital**: 1–2 Jetson Thor nodes + MinION sequencers, positioned in ICU or clinical microbiology lab
- **Hospital network**: deploy Thor nodes at multiple sites; each runs independently but feeds anonymized surveillance data to shared cloud
- **Pandemic scenario**: edge nodes operate fully offline if cloud is overwhelmed — critical for surge capacity
- **Tiered deployment**: high-acuity hospitals get Thor (128 GB, full DB); smaller clinics get Orin (64 GB, mini DB) — both feed same cloud backend
- **Future hardware**: next-gen Jetson or ONT-integrated devices may shrink the edge node further; ONT's own roadmap suggests tighter hardware-software integration

#### 5.5 Future Potential
- Integration with hospital EMR for automated antibiotic recommendation
- Adaptive sequencing: reject human reads in real-time at the pore level (already supported by MinKNOW) → enriches pathogen signal
- Federated learning: improve basecalling models across hospitals without sharing raw patient data
- Expansion to other clinical applications: meningitis, pneumonia, wound infections

#### Manim Animation Ideas (Section 5)
- **Trade-off balance scale**: Animated scale weighing edge advantages vs limitations
- **Scalability map**: Animated hospital icons appearing across a map, each with an edge node, connected to central cloud

---

## Full Manim Presentation Structure (if going all-in)

If you do the entire presentation in Manim, here's a suggested scene breakdown:

| Scene # | Content | Duration | Animation Type |
|---------|---------|----------|---------------|
| 1 | Title card + your name | 15 sec | Fade in/out |
| 2 | "Every hour counts" — sepsis mortality stat | 45 sec | Animated counter / bar chart |
| 3 | The diagnostic bottleneck — culture vs NGS timelines | 1 min | Horizontal timeline animation |
| 4 | "What if we brought compute to the sequencer?" | 30 sec | Text + conceptual transition |
| 5 | Nanopore sequencing — how it works (brief) | 1 min | Animated DNA through pore → signal → bases |
| 6 | Architecture diagram — build it piece by piece | 2 min | **Centerpiece animation** |
| 7 | Edge class concepts mapping (6 concepts) | 2 min | Concept cards appearing over architecture |
| 8 | Processing pipeline walkthrough | 1.5 min | Sequential stage animation with timing |
| 9 | Edge vs Cloud race | 1 min | Dual timeline animation |
| 10 | Hardware specs summary | 30 sec | Spec table fade-in |
| 11 | Trade-offs | 1 min | Balance scale or pro/con animation |
| 12 | Scalability & future vision | 1 min | Map animation |
| 13 | Conclusion + references | 1 min | Summary bullets + citation list |
| | **Total** | **~14.5 min** | |

---

## Recommended Next Steps

1. **Read 3–4 key papers in full** (prioritize: Taxt 2020, Abouelkhair 2024, Seymour 2017, and the MARTi paper for real-time classification)
2. **Draft the report** — the outline above maps directly to the required sections
3. **Design the architecture diagram** — this is the most important visual; get it right in sketch form first
4. **Script the Manim scenes** — start with the architecture animation (Scene 6), as it's the hardest and most impactful
5. **Refine processing estimates** — cross-reference numbers from the papers with Dorado benchmarks

---

## Source Links

1. Chen et al. (2025): https://bmcinfectdis.biomedcentral.com/articles/10.1186/s12879-025-10604-3
2. Taxt et al. (2020): https://www.nature.com/articles/s41598-020-64616-x
3. Abouelkhair et al. (2024): https://www.nature.com/articles/s41598-024-55635-z
4. Harris et al. (2024): https://journals.asm.org/doi/10.1128/spectrum.03065-23
5. Seymour et al. (2017): https://pubmed.ncbi.nlm.nih.gov/28345952/
6. Dorado GitHub: https://github.com/nanoporetech/dorado
7. GridION Mk1: https://nanoporetech.com/news/news-introducing-gridion-mk1
8. Van Uffelen et al. (2024): https://www.nature.com/articles/s41597-024-03672-8
9. MARTi (2025): https://pmc.ncbi.nlm.nih.gov/articles/PMC12581910/
10. AWS Dorado Benchmarks: https://aws.amazon.com/blogs/hpc/benchmarking-the-oxford-nanopore-technologies-basecallers-on-aws/
11. Gu et al. (2022) — NTS for sepsis: https://pmc.ncbi.nlm.nih.gov/articles/PMC8743725/
12. Seymour meta-analysis on antibiotic delay: https://www.sciencedirect.com/science/article/abs/pii/S0163445324001346
13. Benchmarking classifiers (Kraken2 etc): https://pmc.ncbi.nlm.nih.gov/articles/PMC9676057/