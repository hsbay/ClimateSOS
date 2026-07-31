# Climate State transition model OS
# Github Project Code: https://github.com/hsbay/ClimateSOS, CC-BY 4.0 2026 @safiume

"""Product pathway translation and queue bundling services.

The `ProductAdapter` translates externally described product material into a
normalized `ProductPathway`. `QueueBundler` builds a `ProductQueueBundle` by
creating `ProductQueue` objects from the queue-labelled nodes of a
`ProductPathway`.

Neither service performs synchronization, binding, runtime execution, market
simulation, engineering validation, or result evaluation.
"""

from __future__ import annotations

from .models import (
    ProductPathway,
    ProductQueue,
    ProductQueueBundle,
)


class ProductAdapter:
    """Translate external product material into a ProductPathway.

    ProductAdapter is the intake translation boundary. It normalizes and
    structures externally supplied product material without creating product
    queues, synchronizing pathways, binding runtime state, or evaluating
    results.
    """

    def adapt(self, source: object) -> ProductPathway:
        """Translate one external product submission into a product pathway."""
        raise NotImplementedError


class QueueBundler:
    """Build a `ProductQueueBundle` from a `ProductPathway` graph.

    `QueueBundler` creates queues only from pathway nodes that declare a queue
    direction. It preserves the pathway graph and does not perform
    synchronization, binding, or runtime evaluation.
    """

    def bundle(self, pathway: ProductPathway) -> ProductQueueBundle:
        """Create the product queue bundle represented by a pathway graph."""
        queues = tuple(
            ProductQueue(
                id=node.id,
                name=node.name,
                direction=node.queue_direction,
                source_ids=node.source_ids,
                evidence_ids=node.evidence_ids,
            )
            for node in pathway.nodes
            if node.queue_direction is not None
        )

        return ProductQueueBundle(
            product_pathway_id=pathway.pathway_id,
            queues=queues,
            source_ids=pathway.source_ids,
            evidence_ids=pathway.evidence_ids,
        )
