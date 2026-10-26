"""Synthetic evaluation boundaries, not model quality claims."""

import hashlib
from pathlib import Path

import pytest

from app.evaluations.investigation import (
    DATASET,
    ROOT,
    evidence_and_baseline,
    fixture,
    load_cases,
    parent_run,
    summary,
)

HOLDOUT = ROOT / "data/evaluations/holdout-010.json"


def test_fixed_benchmark_and_holdout_labels_are_frozen():
    import json

    historical = json.loads((ROOT / "docs/testing/iteration-009/ambiguous-live.json").read_text())
    assert hashlib.sha256(DATASET.read_bytes()).hexdigest() == historical["dataset_sha256"]
    assert len(load_cases(HOLDOUT)) == 7
    assert not ({c["id"] for c in load_cases()} & {c["id"] for c in load_cases(HOLDOUT)})


@pytest.mark.parametrize("case", load_cases(HOLDOUT), ids=lambda c: c["id"])
def test_holdouts_are_isolated_and_financially_scoped(case):
    with fixture(case) as engine:
        context, _ = evidence_and_baseline(engine, case)
    assert "ground_truth" not in context
    assert context["records"]["transaction:payment"]["source_id"] == case["payment"]["source_id"]
    if case["id"] == "foreign-invoice":
        assert not any(k.startswith("invoice:") for k in context["records"])


def test_missing_usage_is_unknown_and_failures_remain_in_denominator():
    measured = summary(
        [
            {
                "ground_truth": {"allocations": []},
                "assisted": {"status": "timeout", "score": {"correct": False}},
            }
        ],
        "assisted",
    )
    assert measured["known_total_tokens"] is None
    assert measured["inference_failures"] == 1
    assert measured["accuracy"] == 0


def test_report_output_cannot_overwrite_historical_evidence():
    with pytest.raises(ValueError, match="iteration-010"):
        parent_run(output_dir=Path(ROOT / "docs/testing/iteration-009"))
