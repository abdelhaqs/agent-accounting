# GCP Cost Estimate — Zerion Pipeline (Every 30 Minutes)

> Last updated: 2026-08-26. GCP prices change; verify with the [GCP Pricing Calculator](https://cloud.google.com/products/calculator) before deploying.

## Architecture Constraints

- **Everything runs on GCP** — no Supabase, no AWS.
- **Orchestration:** Cloud Workflows + Cloud Scheduler (no Cloud Composer).
- **Sync frequency:** Every 30 minutes = **48 runs/day**.
- **Job runtime:** **3 minutes per run** (180 seconds), e.g. due to rate-limit delays and pagination.
- **Agents (wallets):** **4 agents** tracked, each run independently.

## Assumptions

| Item | Assumption |
|------|------------|
| Agents | **4 wallets** synced every 30 minutes |
| Runs per month | 48/day × 30 days × 4 agents = **~5,760 runs/month** |
| Data per run | ~175 transactions + 12 positions ≈ **1 MB raw JSON** |
| Cloud Run Job specs | **0.5 vCPU, 512 MiB (0.5 GiB), 180 seconds** per run |
| Region | `us-central1` |
| Raw retention | **90 days** in Cloud Storage + BigQuery |
| Orchestration | 1 Cloud Scheduler job triggers 1 Cloud Workflow that loops through all agents |
| Query volume | dbt transforms + light ad-hoc queries |

## Monthly Cost Breakdown (4 Agents)

| Service | Usage | Cost/month |
|---------|-------|------------|
| **Cloud Run Job** | 5,760 runs × 0.5 vCPU × 180s = **518,400 vCPU-s**<br>5,760 runs × 0.5 GiB × 180s = **518,400 GiB-s**<br>5,760 requests | **~$3.53** (exceeds free tier) |
| **Cloud Storage** | ~17 GB stored (90-day retention, 4 agents)<br>5,760 Class A writes | **~$0.35** |
| **BigQuery — Storage** | ~20 GB raw + marts (4 agents) | **~$0.40** |
| **BigQuery — Queries** | ~200 GB processed by dbt/ad-hoc = 0.2 TB × $5/TB | **~$1.00** |
| **Cloud Workflows** | 1,440 executions × ~6 steps = 8,640 steps (within 5,000 free + 3,640 charged) | **~$0.09** |
| **Cloud Scheduler** | 1 job × $0.10/job (first 3 jobs free) | **$0** |
| **Secret Manager** | 1 secret + 5,760 accesses (within free ops tier) | **~$0.06** |
| **Cloud Monitoring** | Logs/metrics scale with runs | **~$1–3** |
| **Total** | | **~$6–9/month** |

### Cloud Run free-tier check

GCP Cloud Run free tier per month:

- 360,000 vCPU-seconds
- 180,000 GiB-seconds
- 2,000,000 requests

With 4 agents:

- 518,400 vCPU-s → exceeds free by **158,400** → ~$2.85
- 518,400 GiB-s → exceeds free by **338,400** → ~$0.68
- 5,760 requests → still well within free requests

## Cost Per Agent

Roughly **$1.50–2.25/agent/month** at this configuration. If you add more agents, Cloud Run, GCS, and BigQuery scale roughly linearly; Cloud Scheduler and Workflows stay cheap.

## What If You Bump Cloud Run Resources?

If you later increase CPU/memory to handle more wallets or faster backfills:

| Config | vCPU-s/month | GiB-s/month | Cloud Run cost/month |
|--------|--------------|-------------|----------------------|
| 0.5 vCPU, 0.5 GiB, 180s | 129,600 | 129,600 | **$0** |
| 1 vCPU, 1 GiB, 180s | 259,200 | 259,200 | **~$0.16** (memory overage) |
| 2 vCPU, 2 GiB, 180s | 518,400 | 518,400 | **~$4.45** |

Even doubling resources barely moves the needle.

## What Drives Cost as You Scale?

| If this grows... | Impact |
|------------------|--------|
| **More transactions per run** | Cloud Run free tier still covers a lot. GCS/BigQuery scale linearly but remain cheap for GB-scale data. |
| **More wallets** | Linear scaling on Cloud Run, GCS, BigQuery. Batch carefully to avoid burst costs. |
| **Longer retention** | GCS/BigQuery storage grows. Move old GCS files to **Nearline** ($0.010/GB) or **Coldline** ($0.004/GB). |
| **More dashboards / API queries** | BigQuery query costs grow. For heavy reads, consider BigQuery BI Engine or caching. |

## Cost-Saving Tips

1. **Stick with Cloud Workflows + Scheduler** — no need for Composer at this scale.
2. **Right-size Cloud Run** — 0.5 vCPU / 512 MiB is plenty for this workload.
3. **Partition BigQuery tables** by `run_timestamp` and **cluster** by `wallet_address`.
4. **Archive old GCS files** to Coldline after 30–90 days.
5. **Tune sync frequency** — every 30 minutes may be overkill for a low-activity wallet. Hourly or every 6 hours cuts run volume proportionally.
6. **Use BigQuery sandbox** for early development.

## Why Not Cloud Composer?

Cloud Composer charges for the Airflow environment 24/7, which starts around **$250+/month** even when idle. For a single small pipeline, that flat fee is unnecessary. Cloud Workflows + Scheduler gives you cron-style orchestration for essentially free and is the right fit here.
