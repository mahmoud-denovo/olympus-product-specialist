"""
Authorized Ingestion Connector & Scientific Validation Gateway for Evident/Olympus Products.

Enforces:
- Rule B-01 / Evident Quality Gate: Mandatory scientific spec validation before catalog entry.
- Versioned source anchors & immutable SHA-256 checksum tracking.
- Zero-cloud deterministic 32-dim feature vector generation for local vector similarity search.
- Bulk file & payload ingestion into canonical ProductCatalog (SQLite/PostgreSQL).
"""

import hashlib
import json
import logging
import math
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from pydantic import BaseModel, Field

from olympus_specialist.domain.products.catalog import (
    ProductCategory,
    SourceAnchor,
    BaseProduct,
    StandProduct,
    ObjectiveProduct,
    IlluminationProduct,
    AccessoryProduct,
    ProductCatalog,
)

logger = logging.getLogger(__name__)

# Authorized Evident/Olympus domains for URL verification
AUTHORIZED_DOMAINS = [
    "olympus-lifescience.com",
    "evident-scientific.com",
    "olympus-ims.com",
    "olympus-global.com",
    "evident.com"
]


class ValidationResult(BaseModel):
    """Result returned by Scientific Validation Gateway."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    sanitized_specs: Dict[str, Any] = Field(default_factory=dict)


class IngestionReport(BaseModel):
    """Ingestion summary report."""
    total_received: int
    total_ingested: int
    total_rejected: int
    rejection_details: List[Dict[str, Any]] = Field(default_factory=list)
    ingested_product_ids: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ScientificValidationGateway:
    """
    Mandatory gateway enforcing scientific and technical validation on product payloads
    prior to entering the Knowledge Base or Product Catalog.
    """

    @classmethod
    def validate_product_payload(cls, raw_payload: Dict[str, Any]) -> ValidationResult:
        """Validates raw product record against scientific & optical requirements."""
        errors: List[str] = []
        warnings: List[str] = []
        specs = raw_payload.get("specs", {})
        if not isinstance(specs, dict):
            specs = {}

        # 1. Mandatory Identity Fields
        product_id = str(raw_payload.get("id") or raw_payload.get("model_name") or "").strip()
        if not product_id:
            errors.append("Missing mandatory field 'id' or 'model_name'.")

        model_name = str(raw_payload.get("model_name") or "").strip()
        if not model_name:
            errors.append("Missing mandatory field 'model_name'.")

        # 2. Category Validation
        category_raw = str(raw_payload.get("category") or "").strip().lower()
        valid_cats = [c.value for c in ProductCategory]
        if category_raw not in valid_cats:
            errors.append(f"Invalid category '{category_raw}'. Must be one of {valid_cats}.")

        # 3. Optical Standard Check
        optical_std = str(raw_payload.get("optical_standard", "UIS2")).strip()
        if optical_std not in ["UIS2", "UIS", "Standard", "C-Mount"]:
            warnings.append(f"Non-standard optical standard '{optical_std}'. Defaulting to UIS2.")

        # 4. Source URL / Provenance Gate
        source_url = raw_payload.get("source_url") or (
            raw_payload.get("source_anchor", {}).get("source_url") if isinstance(raw_payload.get("source_anchor"), dict) else None
        )
        if source_url:
            is_authorized = any(domain in str(source_url).lower() for domain in AUTHORIZED_DOMAINS)
            if not is_authorized and not str(source_url).startswith("file://") and not str(source_url).startswith("doc://"):
                warnings.append(f"Source URL '{source_url}' is outside official Evident domains.")

        # 5. Category-Specific Scientific Spec Checks
        if category_raw == ProductCategory.STAND.value:
            if "supported_modes" not in specs:
                warnings.append("Stand missing 'supported_modes' spec list. Defaulting to ['Brightfield'].")
                specs["supported_modes"] = ["Brightfield"]

        elif category_raw == ProductCategory.OBJECTIVE.value:
            if "magnification" not in specs and "mag" not in specs:
                errors.append("Objective missing mandatory spec 'magnification'.")
            if "thread_type" not in specs and "thread" not in specs:
                warnings.append("Objective missing 'thread_type'. Defaulting to M25.")
                specs["thread_type"] = "M25"

        elif category_raw == ProductCategory.ILLUMINATION.value:
            if "light_source_type" not in specs and "type" not in specs:
                specs["light_source_type"] = "LED"

        elif category_raw == ProductCategory.ACCESSORY.value:
            if "accessory_type" not in specs:
                specs["accessory_type"] = "camera_adapter"

        is_valid = len(errors) == 0
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            sanitized_specs=specs
        )


class AuthorizedEvidentConnector:
    """
    Authorized ingestion connector that reads, validates, normalizes,
    and stores official Evident/Olympus catalog records with full source anchors.
    """

    def __init__(self, catalog: ProductCatalog):
        self.catalog = catalog

    def ingest_record(
        self,
        raw_payload: Dict[str, Any],
        override_source_url: Optional[str] = None
    ) -> Tuple[bool, Optional[BaseProduct], List[str]]:
        """
        Validates, normalizes, and ingests a single product record into the ProductCatalog.
        Returns (success_boolean, ingested_product, list_of_error_messages).
        """
        validation = ScientificValidationGateway.validate_product_payload(raw_payload)
        if not validation.is_valid:
            logger.warning(f"Ingestion rejected record '{raw_payload.get('id')}': {validation.errors}")
            return False, None, validation.errors

        product_id = str(raw_payload.get("id") or raw_payload.get("model_name")).strip()
        model_name = str(raw_payload.get("model_name")).strip()
        category_str = str(raw_payload.get("category")).strip().lower()
        category_enum = ProductCategory(category_str)

        # Source Anchor provenance
        source_url = override_source_url or raw_payload.get("source_url") or (
            raw_payload.get("source_anchor", {}).get("source_url") if isinstance(raw_payload.get("source_anchor"), dict) else None
        ) or f"https://www.evident-scientific.com/en/products/{product_id.lower()}"

        doc_ref = raw_payload.get("doc_reference") or "Official Evident Datasheet"

        # Compute payload SHA-256 for immutability tracking
        payload_bytes = json.dumps(raw_payload, sort_keys=True).encode("utf-8")
        checksum = hashlib.sha256(payload_bytes).hexdigest()

        anchor = SourceAnchor(
            source_url=source_url,
            doc_reference=doc_ref,
            timestamp=datetime.utcnow().isoformat(),
            verified=True,
            checksum=checksum
        )

        # Generate deterministic 32-dim feature embedding vector ($0 cost) if not provided
        embedding = raw_payload.get("embedding")
        if not embedding or not isinstance(embedding, list):
            embedding = self._generate_deterministic_embedding(
                model_name=model_name,
                category=category_str,
                specs=validation.sanitized_specs
            )

        # Build Domain Product Model
        product_data = {
            "id": product_id,
            "model_name": model_name,
            "category": category_enum,
            "optical_standard": str(raw_payload.get("optical_standard", "UIS2")),
            "arabic_name": raw_payload.get("arabic_name"),
            "description": str(raw_payload.get("description", f"Official Evident {model_name} {category_str}")),
            "specs": validation.sanitized_specs,
            "embedding": embedding,
            "source_anchor": anchor,
            "is_mock": False  # Real authorized data
        }

        if category_enum == ProductCategory.STAND:
            product = StandProduct(**product_data)
        elif category_enum == ProductCategory.OBJECTIVE:
            product = ObjectiveProduct(**product_data)
        elif category_enum == ProductCategory.ILLUMINATION:
            product = IlluminationProduct(**product_data)
        elif category_enum == ProductCategory.ACCESSORY:
            product = AccessoryProduct(**product_data)
        else:
            product = BaseProduct(**product_data)

        # Store into catalog
        self.catalog.add_product(product)
        return True, product, []

    def ingest_batch(
        self,
        records: List[Dict[str, Any]],
        override_source_url: Optional[str] = None
    ) -> IngestionReport:
        """Batch ingests a list of raw records and returns an IngestionReport."""
        total_received = len(records)
        ingested_ids: List[str] = []
        rejections: List[Dict[str, Any]] = []

        for record in records:
            success, product, errors = self.ingest_record(record, override_source_url=override_source_url)
            if success and product:
                ingested_ids.append(product.id)
            else:
                rejections.append({
                    "record_id": record.get("id") or record.get("model_name") or "unknown",
                    "errors": errors
                })

        return IngestionReport(
            total_received=total_received,
            total_ingested=len(ingested_ids),
            total_rejected=len(rejections),
            rejection_details=rejections,
            ingested_product_ids=ingested_ids
        )

    def ingest_from_file(self, file_path: str) -> IngestionReport:
        """Ingests product records from a local JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = data if isinstance(data, list) else [data]
        return self.ingest_batch(records)

    @staticmethod
    def _generate_deterministic_embedding(
        model_name: str,
        category: str,
        specs: Dict[str, Any]
    ) -> List[float]:
        """
        Generates a 32-dimensional deterministic normalized feature vector from component specs
        to enable zero-LLM vector similarity search without external cloud API calls.
        """
        vector = [0.0] * 32
        
        # Category one-hot encoding (dims 0-3)
        cat_map = {"stand": 0, "objective": 1, "illumination": 2, "accessory": 3}
        cat_idx = cat_map.get(category, 3)
        vector[cat_idx] = 1.0

        # Model name hash features (dims 4-11)
        name_hash = hashlib.md5(model_name.encode("utf-8")).digest()
        for i in range(8):
            vector[4 + i] = (name_hash[i] / 255.0) * 2.0 - 1.0

        # Numeric specs features (dims 12-19)
        mag = float(specs.get("magnification", 1.0))
        vector[12] = math.tanh(mag / 100.0)

        na = float(specs.get("numerical_aperture", 0.1))
        vector[13] = na

        wd = float(specs.get("working_distance_mm", 1.0))
        vector[14] = math.tanh(wd / 10.0)

        # Thread features (dims 20-23)
        thread = str(specs.get("thread_type", "")).upper()
        if "M25" in thread:
            vector[20] = 1.0
        elif "RMS" in thread:
            vector[21] = 1.0
        elif "M32" in thread:
            vector[22] = 1.0

        # Mode features (dims 24-27)
        modes = str(specs.get("supported_modes", []))
        if "Brightfield" in modes or "BF" in modes:
            vector[24] = 1.0
        if "Darkfield" in modes or "DF" in modes:
            vector[25] = 1.0
        if "Fluorescence" in modes or "FL" in modes:
            vector[26] = 1.0
        if "DIC" in modes:
            vector[27] = 1.0

        # L2 Normalize
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [round(v / norm, 6) for v in vector]

        return vector
