"""
Unit tests for Canonical Product Catalog and Authorized Evident Ingestion Connector.
Verifies zero-LLM lookup, vector similarity search, DDL schema, and Scientific Validation Gateway.
"""

import os
import tempfile
import pytest
from olympus_specialist.domain.products.catalog import (
    ProductCategory,
    SourceAnchor,
    BaseProduct,
    StandProduct,
    ObjectiveProduct,
    IlluminationProduct,
    AccessoryProduct,
    ProductCatalog,
    ProductCatalogSchema,
)
from olympus_specialist.ingestion.authorized_connector import (
    ScientificValidationGateway,
    AuthorizedEvidentConnector,
    ValidationResult,
    IngestionReport,
)


@pytest.fixture
def memory_catalog():
    """Provides an in-memory ProductCatalog database instance."""
    return ProductCatalog(":memory:")


@pytest.fixture
def sample_products_data():
    """Provides sample product dictionary records for testing."""
    return [
        {
            "id": "BX53M",
            "model_name": "Olympus BX53M",
            "category": "stand",
            "optical_standard": "UIS2",
            "arabic_name": "إطار مجهر معدني قائم BX53M",
            "description": "Upright metallurgical microscope stand with reflected/transmitted light",
            "specs": {
                "stand_type": "Upright Metallurgical",
                "supported_modes": ["Brightfield", "Darkfield", "Polarized", "DIC"],
                "ports_count": 2
            },
            "source_url": "https://www.evident-scientific.com/en/products/bx53m"
        },
        {
            "id": "GX53",
            "model_name": "Olympus GX53",
            "category": "stand",
            "optical_standard": "UIS2",
            "arabic_name": "إطار مجهر مقلوب GX53",
            "description": "Inverted metallurgical microscope frame",
            "specs": {
                "stand_type": "Inverted Metallurgical",
                "supported_modes": ["Brightfield", "Darkfield", "DIC"],
                "ports_count": 1
            },
            "source_url": "https://www.evident-scientific.com/en/products/gx53"
        },
        {
            "id": "MPLFLN10X",
            "model_name": "MPLFLN 10X",
            "category": "objective",
            "optical_standard": "UIS2",
            "arabic_name": "عدسة شيئية 10X",
            "description": "Plan Semi-Apochromat 10X metallurgical objective",
            "specs": {
                "magnification": 10.0,
                "numerical_aperture": 0.30,
                "working_distance_mm": 11.0,
                "thread_type": "M25",
                "immersion_type": "air"
            },
            "source_url": "https://www.evident-scientific.com/en/products/mplfln10x"
        },
        {
            "id": "MPLFLN100XBD",
            "model_name": "MPLFLN 100XBD",
            "category": "objective",
            "optical_standard": "UIS2",
            "arabic_name": "عدسة شيئية حقل مضيء/مظلم 100X",
            "description": "Brightfield/Darkfield metallurgical objective 100X",
            "specs": {
                "magnification": 100.0,
                "numerical_aperture": 0.90,
                "working_distance_mm": 1.0,
                "thread_type": "M25",
                "immersion_type": "air"
            },
            "source_url": "https://www.evident-scientific.com/en/products/mplfln100xbd"
        },
        {
            "id": "LED-REF-ILL",
            "model_name": "BX3M-LED",
            "category": "illumination",
            "optical_standard": "UIS2",
            "arabic_name": "وحدة إضاءة LED انعكاسية",
            "description": "Reflected light LED illuminator for BX3M series",
            "specs": {
                "light_source_type": "LED",
                "lifetime_hours": 20000,
                "color_temp_k": 5600
            },
            "source_url": "https://www.evident-scientific.com/en/products/bx3m-led"
        },
        {
            "id": "U-TV1X-2",
            "model_name": "U-TV1X-2",
            "category": "accessory",
            "optical_standard": "UIS2",
            "arabic_name": "محول كاميرا 1X C-Mount",
            "description": "C-Mount camera adapter 1x magnification",
            "specs": {
                "accessory_type": "camera_adapter",
                "mount_type": "C-Mount",
                "magnification": 1.0
            },
            "source_url": "https://www.evident-scientific.com/en/products/u-tv1x-2"
        }
    ]


def test_catalog_schema_initialization(memory_catalog):
    """Verifies DDL schema initialization and table creation."""
    stats = memory_catalog.get_catalog_stats()
    assert stats["total_products"] == 0
    assert stats["embedded_products"] == 0


def test_authorized_connector_ingestion(memory_catalog, sample_products_data):
    """Verifies Scientific Validation Gateway and ingestion connector batch processing."""
    connector = AuthorizedEvidentConnector(memory_catalog)
    report = connector.ingest_batch(sample_products_data)

    assert report.total_received == 6
    assert report.total_ingested == 6
    assert report.total_rejected == 0
    assert len(report.ingested_product_ids) == 6

    stats = memory_catalog.get_catalog_stats()
    assert stats["total_products"] == 6
    assert stats["embedded_products"] == 6
    assert stats["category_counts"]["stand"] == 2
    assert stats["category_counts"]["objective"] == 2
    assert stats["category_counts"]["illumination"] == 1
    assert stats["category_counts"]["accessory"] == 1


def test_zero_llm_catalog_lookup(memory_catalog, sample_products_data):
    """Verifies deterministic zero-LLM lookup filtering by category and specs."""
    connector = AuthorizedEvidentConnector(memory_catalog)
    connector.ingest_batch(sample_products_data)

    # Lookup stands
    stands = memory_catalog.lookup_zero_llm(category=ProductCategory.STAND)
    assert len(stands) == 2
    assert set([s.id for s in stands]) == {"BX53M", "GX53"}

    # Lookup objectives with spec filter thread_type="M25"
    m25_objectives = memory_catalog.lookup_zero_llm(
        category=ProductCategory.OBJECTIVE,
        specs_filter={"thread_type": "M25"}
    )
    assert len(m25_objectives) == 2

    # Lookup single product by model name
    res = memory_catalog.search_by_model("BX53M")
    assert len(res) == 1
    assert res[0].model_name == "Olympus BX53M"
    assert res[0].source_anchor is not None
    assert res[0].source_anchor.verified is True


def test_vector_similarity_search(memory_catalog, sample_products_data):
    """Verifies vector embedding storage and vector cosine similarity search."""
    connector = AuthorizedEvidentConnector(memory_catalog)
    connector.ingest_batch(sample_products_data)

    bx53m = memory_catalog.get_product("BX53M")
    assert bx53m is not None
    assert bx53m.embedding is not None
    assert len(bx53m.embedding) == 32

    # Search with BX53M vector
    matches = memory_catalog.search_vector_similarity(bx53m.embedding, top_k=3)
    assert len(matches) > 0
    top_product, top_score = matches[0]
    assert top_product.id == "BX53M"
    assert top_score > 0.99  # Self-similarity should be ~1.0


def test_scientific_validation_gateway_rejection():
    """Verifies that invalid product payloads are rejected by Scientific Validation Gateway."""
    invalid_payload = {
        "id": "",  # Missing ID
        "model_name": "",  # Missing model name
        "category": "invalid_category",  # Invalid category
        "specs": "not_a_dict"
    }

    result = ScientificValidationGateway.validate_product_payload(invalid_payload)
    assert result.is_valid is False
    assert len(result.errors) >= 3


def test_hybrid_lookup(memory_catalog, sample_products_data):
    """Verifies hybrid search combining spec filtering and vector similarity."""
    connector = AuthorizedEvidentConnector(memory_catalog)
    connector.ingest_batch(sample_products_data)

    query_obj = memory_catalog.get_product("MPLFLN10X")
    results = memory_catalog.hybrid_lookup(
        query_text="10X",
        query_vector=query_obj.embedding,
        category=ProductCategory.OBJECTIVE,
        top_k=5
    )

    assert len(results) >= 1
    assert results[0]["product"].id == "MPLFLN10X"
    assert results[0]["deterministic_match"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
