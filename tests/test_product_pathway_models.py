# Climate State transition model OS
# Github Project Code: https://github.com/hsbay/ClimateSOS, CC-BY 4.0 2026 @safiume

"""Tests for Product Pathway Adapter graph models."""

from climatesos.models import (
    Context,
    PathwayEdge,
    PathwayNode,
    ProductPathway,
    ProductQueueDirection,
)


def test_product_pathway_preserves_normalized_product_graph() -> None:
    user_id = "customer_01"
    pathway_id = "customer_01-product_01-datacenter"

    context = Context(
        user_id=user_id,
        pathway_id=pathway_id,
        invocation_mode="comparison",
    )

    landfill_methane = PathwayNode(
        id=f"{pathway_id}-landfill-methane",
        name="Waste methane from landfills",
        kind="feedstock",
        queue_direction=ProductQueueDirection.INPUT,
    )
    conversion_process = PathwayNode(
        id=f"{pathway_id}-conversion-process",
        name="Proprietary conversion process",
        kind="process",
    )
    hydrogen = PathwayNode(
        id=f"{pathway_id}-hydrogen",
        name="Hydrogen",
        kind="product-output",
        queue_direction=ProductQueueDirection.OUTPUT,
    )
    enriched_biochar = PathwayNode(
        id=f"{pathway_id}-enriched-biochar",
        name="Enriched biochar",
        kind="product-output",
        queue_direction=ProductQueueDirection.OUTPUT,
    )

    pathway = ProductPathway(
        user_id=user_id,
        pathway_id=pathway_id,
        name="Waste-methane conversion pathway",
        description=(
            "Convert waste methane into hydrogen and enriched biochar for a "
            "proposed datacenter customer."
        ),
        context=context,
        nodes=(
            landfill_methane,
            conversion_process,
            hydrogen,
            enriched_biochar,
        ),
        edges=(
            PathwayEdge(
                source_node_id=landfill_methane.id,
                target_node_id=conversion_process.id,
                relationship="feeds",
            ),
            PathwayEdge(
                source_node_id=conversion_process.id,
                target_node_id=hydrogen.id,
                relationship="produces",
            ),
            PathwayEdge(
                source_node_id=conversion_process.id,
                target_node_id=enriched_biochar.id,
                relationship="produces",
            ),
        ),
    )

    assert pathway.user_id == user_id
    assert pathway.pathway_id == pathway_id
    assert pathway.context.pathway_id == pathway_id
    assert pathway.nodes == (
        landfill_methane,
        conversion_process,
        hydrogen,
        enriched_biochar,
    )
    assert pathway.edges[0].relationship == "feeds"
    assert pathway.edges[1].relationship == "produces"
    assert pathway.edges[2].relationship == "produces"
    assert landfill_methane.queue_direction is ProductQueueDirection.INPUT
    assert hydrogen.queue_direction is ProductQueueDirection.OUTPUT
    assert enriched_biochar.queue_direction is ProductQueueDirection.OUTPUT
    assert conversion_process.queue_direction is None
