"""Load parsed transfers and balances into BigQuery.

Tables are created by Terraform (terraform/minimal). This module only loads data:
- transfers: append via MERGE dedupe on the natural unique key (safe to re-run)
- balances: per-wallet snapshot replace (delete wallet rows, insert current state)
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from google.cloud import bigquery

logger = logging.getLogger(__name__)

TRANSFERS_SCHEMA = [
    bigquery.SchemaField("wallet", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("agent_name", "STRING"),
    bigquery.SchemaField("tx_id", "STRING"),
    bigquery.SchemaField("tx_hash", "STRING"),
    bigquery.SchemaField("chain", "STRING"),
    bigquery.SchemaField("mined_at", "TIMESTAMP"),
    bigquery.SchemaField("direction", "STRING"),
    bigquery.SchemaField("sender", "STRING"),
    bigquery.SchemaField("recipient", "STRING"),
    bigquery.SchemaField("token_id", "STRING"),
    bigquery.SchemaField("token_name", "STRING"),
    bigquery.SchemaField("token_symbol", "STRING"),
    bigquery.SchemaField("token_address", "STRING"),
    bigquery.SchemaField("chain_id", "STRING"),
    bigquery.SchemaField("decimals", "INTEGER"),
    bigquery.SchemaField("amount_raw", "STRING"),
    bigquery.SchemaField("amount_float", "FLOAT"),
    bigquery.SchemaField("price", "FLOAT"),
    bigquery.SchemaField("usd_value", "FLOAT"),
    bigquery.SchemaField("provider", "STRING"),
]

BALANCES_SCHEMA = [
    bigquery.SchemaField("wallet", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("agent_name", "STRING"),
    bigquery.SchemaField("chain", "STRING"),
    bigquery.SchemaField("position_type", "STRING"),
    bigquery.SchemaField("token_id", "STRING"),
    bigquery.SchemaField("token_name", "STRING"),
    bigquery.SchemaField("token_symbol", "STRING"),
    bigquery.SchemaField("token_address", "STRING"),
    bigquery.SchemaField("chain_id", "STRING"),
    bigquery.SchemaField("decimals", "INTEGER"),
    bigquery.SchemaField("balance_raw", "STRING"),
    bigquery.SchemaField("balance_float", "FLOAT"),
    bigquery.SchemaField("price", "FLOAT"),
    bigquery.SchemaField("usd_value", "FLOAT"),
    bigquery.SchemaField("is_receipt_token", "BOOLEAN"),
    bigquery.SchemaField("updated_at", "TIMESTAMP"),
    bigquery.SchemaField("provider", "STRING"),
]

RECONCILIATION_SCHEMA = [
    bigquery.SchemaField("run_timestamp", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("agent_name", "STRING"),
    bigquery.SchemaField("wallet", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("provider", "STRING"),
    bigquery.SchemaField("computed_usd", "FLOAT"),
    bigquery.SchemaField("same_provider_total_usd", "FLOAT"),
    bigquery.SchemaField("cross_provider_total_usd", "FLOAT"),
    bigquery.SchemaField("same_provider_delta_pct", "FLOAT"),
    bigquery.SchemaField("cross_provider_delta_pct", "FLOAT"),
    bigquery.SchemaField("onchain_total_usd", "FLOAT"),
    bigquery.SchemaField("onchain_unverified_usd", "FLOAT"),
    bigquery.SchemaField("onchain_delta_pct", "FLOAT"),
    bigquery.SchemaField("status", "STRING"),
    bigquery.SchemaField("loaded_at", "TIMESTAMP"),
]

# Same natural unique key as the SQLite UNIQUE constraint in storage.py.
TRANSFERS_KEY = ["wallet", "tx_id", "token_id", "direction", "sender", "recipient", "amount_raw"]

# Columns stored in BigQuery (excludes the SQLite autoincrement id).
TRANSFER_COLUMNS = [f.name for f in TRANSFERS_SCHEMA]
BALANCE_COLUMNS = [f.name for f in BALANCES_SCHEMA]


def get_client(project: str | None = None) -> bigquery.Client:
    return bigquery.Client(project=project)


def _null_safe_join(key_columns: list[str]) -> str:
    """Build an ON clause that treats NULLs as equal (like SQLite UNIQUE does not,
    but our data is effectively keyed this way and MERGE forbids NULL mismatches)."""
    parts = [
        f"(T.{c} = S.{c} OR (T.{c} IS NULL AND S.{c} IS NULL))"
        for c in key_columns
    ]
    return " AND ".join(parts)


def load_transfers(
    client: bigquery.Client,
    dataset: str,
    rows: list[dict[str, Any]],
) -> int:
    """Append new transfers via staging table + MERGE dedupe.

    Returns the number of rows actually inserted (0 on re-runs).
    """
    if not rows:
        logger.info("BigQuery transfers: nothing to load")
        return 0

    project = client.project
    target = f"`{project}.{dataset}.transfers`"
    staging_id = f"_staging_transfers_{uuid.uuid4().hex[:12]}"
    staging_ref = f"{project}.{dataset}.{staging_id}"

    payload = [{c: r.get(c) for c in TRANSFER_COLUMNS} for r in rows]

    job_config = bigquery.LoadJobConfig(
        schema=TRANSFERS_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    client.load_table_from_json(payload, staging_ref, job_config=job_config).result()

    try:
        merge_sql = f"""
        MERGE {target} T
        USING `{staging_ref}` S
        ON {_null_safe_join(TRANSFERS_KEY)}
        WHEN NOT MATCHED THEN
          INSERT ({", ".join(TRANSFER_COLUMNS)})
          VALUES ({", ".join("S." + c for c in TRANSFER_COLUMNS)})
        """
        job = client.query(merge_sql)
        result = job.result()
        inserted = job.num_dml_affected_rows or 0
        logger.info(
            "BigQuery transfers: staged %d rows, inserted %d new rows",
            len(payload),
            inserted,
        )
        return inserted
    finally:
        client.delete_table(staging_ref, not_found_ok=True)


def load_balances(
    client: bigquery.Client,
    dataset: str,
    wallet: str,
    rows: list[dict[str, Any]],
) -> int:
    """Replace the balance snapshot for one wallet. Returns rows inserted."""
    project = client.project
    target = f"`{project}.{dataset}.balances`"

    client.query(
        f"DELETE FROM {target} WHERE wallet = @wallet",
        job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("wallet", "STRING", wallet)]
        ),
    ).result()

    if not rows:
        logger.info("BigQuery balances: cleared snapshot for %s (no positions)", wallet)
        return 0

    payload = [{c: r.get(c) for c in BALANCE_COLUMNS} for r in rows]
    job_config = bigquery.LoadJobConfig(
        schema=BALANCES_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    client.load_table_from_json(
        payload, f"{project}.{dataset}.balances", job_config=job_config
    ).result()

    logger.info("BigQuery balances: replaced snapshot for %s (%d rows)", wallet, len(payload))
    return len(payload)


def save_reconciliation(
    client: bigquery.Client,
    dataset: str,
    records: list[dict[str, Any]],
) -> int:
    """Append balance reconciliation records (one per agent per run)."""
    if not records:
        return 0

    from datetime import datetime, timezone

    loaded_at = datetime.now(timezone.utc).isoformat()
    payload = [
        {f.name: (r.get(f.name) if f.name != "loaded_at" else loaded_at) for f in RECONCILIATION_SCHEMA}
        for r in records
    ]
    job_config = bigquery.LoadJobConfig(
        schema=RECONCILIATION_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    client.load_table_from_json(
        payload, f"{client.project}.{dataset}.balance_reconciliation", job_config=job_config
    ).result()

    mismatches = [r for r in records if r.get("status") == "MISMATCH"]
    logger.info(
        "BigQuery reconciliation: saved %d records (%d mismatches)",
        len(payload),
        len(mismatches),
    )
    return len(payload)
