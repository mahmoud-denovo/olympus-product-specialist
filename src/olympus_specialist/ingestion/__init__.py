"""
Authorized Evident/Olympus Data Ingestion Package.
Provides Scientific Validation Gateway and authorized connector for normalized catalog ingestion.
"""

from olympus_specialist.ingestion.authorized_connector import (
    ScientificValidationGateway,
    AuthorizedEvidentConnector,
    IngestionReport,
    ValidationResult,
)

__all__ = [
    "ScientificValidationGateway",
    "AuthorizedEvidentConnector",
    "IngestionReport",
    "ValidationResult",
]
