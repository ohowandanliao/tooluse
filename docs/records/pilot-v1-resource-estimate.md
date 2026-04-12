# Pilot-V1 Resource Estimate

## Planning Assumptions

- one backbone family only
- `7B-8B` instruct model as the pilot default
- `LoRA/PEFT`, not full fine-tuning
- single-turn paired-schema data
- full pilot methods:
  - `direct`
  - `hammer_like`
  - `latent_bottleneck`
  - `latent_consistency_only`
  - `reuse_main`
- `3` random seeds for the serious run

## Recommended Server

### Preferred

- `1x A100 80GB` or `1x H100 80GB`
- `24-32 vCPU`
- `128GB RAM`
- `1TB NVMe SSD`

Why this is the safest choice:

- enough headroom for `7B-8B` LoRA training, eval, and larger decode batches
- much lower risk of repeated batch-size retuning
- better turnaround for multi-method pilot loops

### Minimum Workable

- `1x RTX 4090 24GB` is not recommended for the full matrix
- `1x RTX 6000 Ada 48GB` or similar `48GB` card is workable
- `16-24 vCPU`
- `64GB RAM`
- `500GB-1TB NVMe SSD`

Limits of the minimum setup:

- more fragile sequence-length and batch-size tuning
- slower full-matrix turnaround
- higher chance that eval becomes the bottleneck

## Rough Compute Budget

### Stage 0: data and evaluator bring-up

- dataset filtering, transform generation, and report scripts are mainly CPU work
- expect `4-8` CPU-hours plus manual checking time

### Stage 1: smoke run

- `1-2` methods
- `1` seed
- target: verify the full pipeline, not judge the thesis
- expect roughly `6-12 GPU-hours`

### Stage 2: pilot-v1 decision run

- all core methods
- `3` seeds
- full `Track R` and `Track P`
- expect roughly:
  - `50-100 GPU-hours` on `A100 80GB / H100 80GB`
  - `80-160 GPU-hours` on a strong `48GB` card

These numbers assume the project stays on the current narrow pilot and does not expand to larger backbones or multi-turn BFCL main tables.

## Storage Budget

- processed datasets and intermediate JSONL: `20-80GB`
- adapters, checkpoints, and logs: `50-150GB`
- predictions, reports, and ablation outputs: `20-80GB`
- comfortable total budget: `200-500GB`

`1TB` is the comfortable choice because pilot work often keeps extra checkpoints and failed runs for auditability.

## Practical Recommendation

- do not rent for `14B+` yet
- do not plan around full fine-tuning
- the fastest research loop is `1x 80GB GPU` with enough CPU and local NVMe
- if budget is tight, choose a strong `48GB` setup, but expect slower iteration and tighter memory margins
