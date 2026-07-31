# Climate State transition model OS
# Github Project Code: https://github.com/hsbay/ClimateSOS, CC-BY 4.0 2026 @safiume

"""Tests for ProductPathway queue projection."""

from climatesos.models import (
    Context,
    PathwayNode,
    ProductPathway,
    ProductQueueDirection,
)
from climatesos.product_adapter import QueueBundler


def test_queue_bundler_projects_labelled_pathway_nodes() -> None:
    user_id = "customer_01"
    pathway_id = "customer_01-product_01"

    feedstock = PathwayNode(
        id=f"{pathway_id}-feedstock",
        name="Recovered feedstock",
        kind="feedstock",
        queue_direction=ProductQueueDirection.INPUT,
        source_ids=("source-feedstock",),
        evidence_ids=("evidence-feedstock",),
    )
    conversion_process = PathwayNode(
        id=f"{pathway_id}-conversion-process",
        name="Conversion process",
        kind="process",
    )
    product_output = PathwayNode(
        id=f"{pathway_id}-product-output",
        name="Converted product",
        kind="product-output",
        queue_direction=ProductQueueDirection.OUTPUT,
        source_ids=("source-output",),
        evidence_ids=("evidence-output",),
    )

    pathway = ProductPathway(
        user_id=user_id,
        pathway_id=pathway_id,
        name="Example conversion pathway",
        description="Convert recovered feedstock into a useful product.",
        context=Context(
            user_id=user_id,
            pathway_id=pathway_id,
        ),
        nodes=(
            feedstock,
            conversion_process,
            product_output,
        ),
        source_ids=("source-pathway",),
        evidence_ids=("evidence-pathway",),
    )

    bundle = QueueBundler().bundle(pathway)

    assert bundle.product_pathway_id == pathway_id
    assert tuple(queue.id for queue in bundle.queues) == (
        feedstock.id,
        product_output.id,
    )
    assert bundle.input_queues[0].direction is ProductQueueDirection.INPUT
    assert bundle.output_queues[0].direction is ProductQueueDirection.OUTPUT
    assert bundle.input_queues[0].source_ids == ("source-feedstock",)
    assert bundle.output_queues[0].evidence_ids == ("evidence-output",)
    assert bundle.source_ids == ("source-pathway",)
    assert bundle.evidence_ids == ("evidence-pathway",)
    assert all(queue.id != conversion_process.id for queue in bundle.queues)
