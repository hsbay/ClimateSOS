# Climate State transition model OS
# Github Project Code: https://github.com/hsbay/ClimateSOS, CC-BY 4.0 2026 @safiume

"""Executable Product Pathway Adapter vertical slice.

This example demonstrates the current product-intake boundary:

external source mapping
    -> ProductAdapter
    -> ProductPathway
    -> QueueBundler
    -> ProductQueueBundle

It intentionally stops before synchronization or runtime evaluation.
"""

from __future__ import annotations

from collections.abc import Mapping

from climatesos.models import (
    Context,
    PathwayEdge,
    PathwayNode,
    ProductPathway,
    ProductQueueDirection,
)
from climatesos.product_adapter import ProductAdapter, QueueBundler


class ExampleMappingProductAdapter(ProductAdapter):
    """Translate one example source mapping into a ProductPathway."""

    def adapt(self, source: object) -> ProductPathway:
        if not isinstance(source, Mapping):
            raise TypeError("ExampleMappingProductAdapter requires a mapping.")

        user_id = self._required_string(source, "user_id")
        pathway_id = self._required_string(source, "pathway_id")
        name = self._required_string(source, "name")
        description = self._required_string(source, "description")

        raw_nodes = source.get("nodes")
        if not isinstance(raw_nodes, tuple):
            raise TypeError("'nodes' must be a tuple of mappings.")

        raw_edges = source.get("edges")
        if not isinstance(raw_edges, tuple):
            raise TypeError("'edges' must be a tuple of mappings.")

        nodes = tuple(self._adapt_node(raw_node) for raw_node in raw_nodes)
        edges = tuple(self._adapt_edge(raw_edge) for raw_edge in raw_edges)

        return ProductPathway(
            user_id=user_id,
            pathway_id=pathway_id,
            name=name,
            description=description,
            context=Context(
                user_id=user_id,
                pathway_id=pathway_id,
                invocation_mode="example",
            ),
            nodes=nodes,
            edges=edges,
            source_ids=("example-source",),
        )

    @staticmethod
    def _adapt_node(source: object) -> PathwayNode:
        if not isinstance(source, Mapping):
            raise TypeError("Each node must be a mapping.")

        raw_direction = source.get("queue_direction")
        direction = (
            ProductQueueDirection(raw_direction)
            if isinstance(raw_direction, str)
            else None
        )

        return PathwayNode(
            id=ExampleMappingProductAdapter._required_string(source, "id"),
            name=ExampleMappingProductAdapter._required_string(source, "name"),
            kind=ExampleMappingProductAdapter._required_string(source, "kind"),
            queue_direction=direction,
        )

    @staticmethod
    def _adapt_edge(source: object) -> PathwayEdge:
        if not isinstance(source, Mapping):
            raise TypeError("Each edge must be a mapping.")

        return PathwayEdge(
            source_node_id=ExampleMappingProductAdapter._required_string(
                source,
                "source_node_id",
            ),
            target_node_id=ExampleMappingProductAdapter._required_string(
                source,
                "target_node_id",
            ),
            relationship=ExampleMappingProductAdapter._required_string(
                source,
                "relationship",
            ),
        )

    @staticmethod
    def _required_string(source: Mapping[object, object], key: str) -> str:
        value = source.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"'{key}' must be a non-empty string.")
        return value


def build_example_source() -> dict[str, object]:
    """Return generic external material for the vertical-slice example."""
    pathway_id = "customer_01-product_01"

    return {
        "user_id": "customer_01",
        "pathway_id": pathway_id,
        "name": "Recovered-methane conversion pathway",
        "description": (
            "Convert recovered methane into hydrogen and enriched biochar."
        ),
        "nodes": (
            {
                "id": f"{pathway_id}-recovered-methane",
                "name": "Recovered methane",
                "kind": "feedstock",
                "queue_direction": "input",
            },
            {
                "id": f"{pathway_id}-conversion-process",
                "name": "Conversion process",
                "kind": "process",
            },
            {
                "id": f"{pathway_id}-hydrogen",
                "name": "Hydrogen",
                "kind": "product-output",
                "queue_direction": "output",
            },
            {
                "id": f"{pathway_id}-enriched-biochar",
                "name": "Enriched biochar",
                "kind": "product-output",
                "queue_direction": "output",
            },
        ),
        "edges": (
            {
                "source_node_id": f"{pathway_id}-recovered-methane",
                "target_node_id": f"{pathway_id}-conversion-process",
                "relationship": "feeds",
            },
            {
                "source_node_id": f"{pathway_id}-conversion-process",
                "target_node_id": f"{pathway_id}-hydrogen",
                "relationship": "produces",
            },
            {
                "source_node_id": f"{pathway_id}-conversion-process",
                "target_node_id": f"{pathway_id}-enriched-biochar",
                "relationship": "produces",
            },
        ),
    }


def main() -> None:
    """Run and display the ProductAdapter vertical slice."""
    source = build_example_source()

    pathway = ExampleMappingProductAdapter().adapt(source)
    bundle = QueueBundler().bundle(pathway)

    print(f"ProductPathway: {pathway.pathway_id}")
    print(f"Graph nodes: {len(pathway.nodes)}")
    print(f"Graph edges: {len(pathway.edges)}")
    print("Product queues:")

    for queue in bundle.queues:
        print(f"  {queue.direction.value}: {queue.name}")


if __name__ == "__main__":
    main()
