# Climate State transition model OS
# Github Project Code: https://github.com/hsbay/ClimateSOS, CC-BY 4.0 2026 @safiume

"""Tests for the SynchronizationComparison foundation model."""

from dataclasses import FrozenInstanceError

import pytest

from climatesos.models import (
    ProductQueue,
    ProductQueueBundle,
    ProductQueueDirection,
    SynchronizationComparison,
)


def test_synchronization_comparison_preserves_input_and_findings() -> None:
    pathway_id = "customer_01-product_01"

    bundle = ProductQueueBundle(
        product_pathway_id=pathway_id,
        queues=(
            ProductQueue(
                id=f"{pathway_id}-feedstock",
                name="Recovered feedstock",
                direction=ProductQueueDirection.INPUT,
            ),
            ProductQueue(
                id=f"{pathway_id}-output",
                name="Converted product",
                direction=ProductQueueDirection.OUTPUT,
            ),
        ),
        source_ids=("source-bundle",),
        evidence_ids=("evidence-bundle",),
    )

    comparison = SynchronizationComparison(
        product_pathway_id=pathway_id,
        queue_bundle=bundle,
        findings=("Output timing remains unresolved.",),
        unresolved_requirements=("deployment-timeline",),
        source_ids=("source-comparison",),
        evidence_ids=("evidence-comparison",),
    )

    assert comparison.product_pathway_id == pathway_id
    assert comparison.queue_bundle is bundle
    assert comparison.findings == ("Output timing remains unresolved.",)
    assert comparison.unresolved_requirements == ("deployment-timeline",)
    assert comparison.source_ids == ("source-comparison",)
    assert comparison.evidence_ids == ("evidence-comparison",)


def test_synchronization_comparison_is_immutable() -> None:
    pathway_id = "customer_01-product_01"
    comparison = SynchronizationComparison(
        product_pathway_id=pathway_id,
        queue_bundle=ProductQueueBundle(
            product_pathway_id=pathway_id,
        ),
    )

    with pytest.raises(FrozenInstanceError):
        comparison.product_pathway_id = "replacement-pathway"
