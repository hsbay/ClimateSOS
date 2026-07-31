# Climate State transition model OS
# Github Project Code: https://github.com/hsbay/ClimateSOS, CC-BY 4.0 2026 @safiume

"""Tests for the ProductAdapter intake-translation boundary."""

from climatesos.models import Context, ProductPathway
from climatesos.product_adapter import ProductAdapter


class StaticProductAdapter(ProductAdapter):
    """Test adapter that returns a predefined normalized pathway."""

    def __init__(self, pathway: ProductPathway) -> None:
        self._pathway = pathway
        self.received_source: object | None = None

    def adapt(self, source: object) -> ProductPathway:
        self.received_source = source
        return self._pathway


def test_product_adapter_translates_source_into_product_pathway() -> None:
    user_id = "customer_01"
    pathway_id = "customer_01-product_01"

    pathway = ProductPathway(
        user_id=user_id,
        pathway_id=pathway_id,
        name="Example product pathway",
        description="Normalized representation of an external product.",
        context=Context(
            user_id=user_id,
            pathway_id=pathway_id,
        ),
    )
    source = {
        "product_name": "Example external product",
        "questionnaire_version": "1",
    }

    adapter = StaticProductAdapter(pathway)

    result = adapter.adapt(source)

    assert result is pathway
    assert adapter.received_source is source
