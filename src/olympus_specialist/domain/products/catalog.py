"""
Canonical Product Catalog & Zero-LLM Lookup Engine for Evident/Olympus Microscopy.

Provides:
- SQLite & PostgreSQL relational schema for Stands, Objectives, Illumination, and Accessories.
- Vector embedding storage & vector cosine similarity search.
- Zero-LLM deterministic lookup engine ($0 cost, 0 cloud tokens in hot path).
- Domain models with strict source anchor provenance & clean data isolation.
"""

from enum import Enum
import json
import math
import sqlite3
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from pydantic import BaseModel, Field


class ProductCategory(str, Enum):
    STAND = "stand"
    OBJECTIVE = "objective"
    ILLUMINATION = "illumination"
    ACCESSORY = "accessory"


class SourceAnchor(BaseModel):
    """Source attribution metadata for scientific provenance verification."""
    source_url: str = Field(..., description="Official Evident/Olympus product spec URL")
    doc_reference: str = Field("Official Evident Specification Sheet", description="Manual or catalog doc reference")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Ingestion timestamp")
    verified: bool = Field(True, description="Scientific verification status")
    checksum: str = Field("", description="SHA-256 payload checksum for immutability tracking")


class BaseProduct(BaseModel):
    """Canonical base product model with source anchor and embedding storage."""
    id: str = Field(..., description="Primary product identifier / SKU")
    model_name: str = Field(..., description="Official model designation e.g. BX53M")
    category: ProductCategory = Field(..., description="Product category classification")
    optical_standard: str = Field("UIS2", description="Optical standard e.g. UIS2, UIS")
    arabic_name: Optional[str] = Field(None, description="Localized Arabic product title")
    description: str = Field("", description="Detailed product description")
    specs: Dict[str, Any] = Field(default_factory=dict, description="Structured technical specifications")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding representation")
    source_anchor: Optional[SourceAnchor] = Field(None, description="Source provenance attribution")
    is_mock: bool = Field(False, description="Strict data isolation flag - must be False for canonical data")


class StandProduct(BaseProduct):
    """Domain representation for Microscope Frames / Stands."""
    category: ProductCategory = ProductCategory.STAND

    @property
    def stand_type(self) -> str:
        return self.specs.get("stand_type", "Upright")

    @property
    def supported_modes(self) -> List[str]:
        return self.specs.get("supported_modes", ["Brightfield"])


class ObjectiveProduct(BaseProduct):
    """Domain representation for Microscope Objectives."""
    category: ProductCategory = ProductCategory.OBJECTIVE

    @property
    def magnification(self) -> float:
        return float(self.specs.get("magnification", 10.0))

    @property
    def numerical_aperture(self) -> float:
        return float(self.specs.get("numerical_aperture", 0.25))

    @property
    def thread_type(self) -> str:
        return self.specs.get("thread_type", "M25")

    @property
    def working_distance_mm(self) -> float:
        return float(self.specs.get("working_distance_mm", 0.0))


class IlluminationProduct(BaseProduct):
    """Domain representation for Illumination units."""
    category: ProductCategory = ProductCategory.ILLUMINATION

    @property
    def light_source_type(self) -> str:
        return self.specs.get("light_source_type", "LED")


class AccessoryProduct(BaseProduct):
    """Domain representation for Cameras, Adapters, Filters, Stages, and Nosepieces."""
    category: ProductCategory = ProductCategory.ACCESSORY

    @property
    def accessory_type(self) -> str:
        return self.specs.get("accessory_type", "camera_adapter")

    @property
    def mount_type(self) -> str:
        return self.specs.get("mount_type", "C-Mount")


class ProductCatalogSchema:
    """SQL DDL definitions for SQLite and PostgreSQL with vector embedding support."""

    SQLITE_INIT_DDL = """
    -- Primary Products Table
    CREATE TABLE IF NOT EXISTS products (
        id TEXT PRIMARY KEY,
        model_name TEXT NOT NULL,
        category TEXT NOT NULL,
        optical_standard TEXT DEFAULT 'UIS2',
        arabic_name TEXT,
        description TEXT,
        specs_json TEXT NOT NULL,
        embedding_json TEXT,
        source_url TEXT,
        doc_reference TEXT,
        ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        verified INTEGER DEFAULT 1,
        checksum TEXT,
        is_mock INTEGER DEFAULT 0
    );

    -- Category Specific Relational Views / Tables for Fast Direct SQL Queries
    CREATE TABLE IF NOT EXISTS stands (
        id TEXT PRIMARY KEY,
        model_name TEXT NOT NULL,
        stand_type TEXT,
        supported_modes_json TEXT,
        ports_count INTEGER DEFAULT 1,
        FOREIGN KEY(id) REFERENCES products(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS objectives (
        id TEXT PRIMARY KEY,
        model_name TEXT NOT NULL,
        magnification REAL NOT NULL,
        numerical_aperture REAL,
        working_distance_mm REAL,
        thread_type TEXT NOT NULL,
        immersion_type TEXT DEFAULT 'air',
        parfocal_distance REAL DEFAULT 45.0,
        FOREIGN KEY(id) REFERENCES products(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS illumination (
        id TEXT PRIMARY KEY,
        model_name TEXT NOT NULL,
        light_source_type TEXT NOT NULL,
        lifetime_hours INTEGER,
        color_temp_k INTEGER,
        FOREIGN KEY(id) REFERENCES products(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS accessories (
        id TEXT PRIMARY KEY,
        model_name TEXT NOT NULL,
        accessory_type TEXT NOT NULL,
        mount_type TEXT,
        magnification REAL,
        FOREIGN KEY(id) REFERENCES products(id) ON DELETE CASCADE
    );

    -- Indexes for Zero-LLM Fast Filtering
    CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
    CREATE INDEX IF NOT EXISTS idx_products_model_name ON products(model_name);
    CREATE INDEX IF NOT EXISTS idx_products_optical_std ON products(optical_standard);
    CREATE INDEX IF NOT EXISTS idx_objectives_thread ON objectives(thread_type);
    CREATE INDEX IF NOT EXISTS idx_objectives_mag ON objectives(magnification);
    """

    POSTGRES_PGVECTOR_DDL = """
    -- PostgreSQL Schema with pgvector extension enabled
    CREATE EXTENSION IF NOT EXISTS vector;

    CREATE TABLE IF NOT EXISTS products (
        id VARCHAR(128) PRIMARY KEY,
        model_name VARCHAR(256) NOT NULL,
        category VARCHAR(64) NOT NULL,
        optical_standard VARCHAR(64) DEFAULT 'UIS2',
        arabic_name TEXT,
        description TEXT,
        specs_json JSONB NOT NULL,
        embedding vector(32),
        source_url TEXT,
        doc_reference TEXT,
        ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        verified BOOLEAN DEFAULT TRUE,
        checksum VARCHAR(64),
        is_mock BOOLEAN DEFAULT FALSE
    );

    CREATE INDEX IF NOT EXISTS idx_pg_products_category ON products(category);
    CREATE INDEX IF NOT EXISTS idx_pg_products_model ON products(model_name);
    CREATE INDEX IF NOT EXISTS idx_pg_products_embedding ON products USING ivfflat (embedding vector_cosine_ops);
    """


class ProductCatalog:
    """
    Canonical Product Catalog repository providing deterministic zero-LLM lookup
    and vector similarity search.
    """

    def __init__(self, db_path_or_conn: Union[str, sqlite3.Connection] = ":memory:"):
        if isinstance(db_path_or_conn, sqlite3.Connection):
            self.conn = db_path_or_conn
            self.db_path = None
        else:
            self.db_path = db_path_or_conn
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        
        self.initialize_schema()

    def initialize_schema(self) -> None:
        """Executes DDL to initialize database tables and indexes."""
        cursor = self.conn.cursor()
        cursor.executescript(ProductCatalogSchema.SQLITE_INIT_DDL)
        self.conn.commit()

    def add_product(self, product: BaseProduct) -> None:
        """
        Inserts or updates a product in the catalog along with category relational tables.
        """
        cursor = self.conn.cursor()

        specs_str = json.dumps(product.specs)
        embedding_str = json.dumps(product.embedding) if product.embedding else None
        
        source_url = product.source_anchor.source_url if product.source_anchor else None
        doc_ref = product.source_anchor.doc_reference if product.source_anchor else None
        checksum = product.source_anchor.checksum if product.source_anchor else None
        verified = 1 if (product.source_anchor and product.source_anchor.verified) else 1

        cursor.execute("""
            INSERT OR REPLACE INTO products (
                id, model_name, category, optical_standard, arabic_name,
                description, specs_json, embedding_json, source_url,
                doc_reference, verified, checksum, is_mock
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product.id,
            product.model_name,
            product.category.value if isinstance(product.category, Enum) else str(product.category),
            product.optical_standard,
            product.arabic_name,
            product.description,
            specs_str,
            embedding_str,
            source_url,
            doc_ref,
            verified,
            checksum,
            1 if product.is_mock else 0
        ))

        # Insert into specific category table
        cat_val = product.category.value if isinstance(product.category, Enum) else str(product.category)
        
        if cat_val == ProductCategory.STAND.value:
            modes_json = json.dumps(product.specs.get("supported_modes", ["Brightfield"]))
            cursor.execute("""
                INSERT OR REPLACE INTO stands (id, model_name, stand_type, supported_modes_json, ports_count)
                VALUES (?, ?, ?, ?, ?)
            """, (
                product.id,
                product.model_name,
                product.specs.get("stand_type", "Upright"),
                modes_json,
                int(product.specs.get("ports_count", 1))
            ))

        elif cat_val == ProductCategory.OBJECTIVE.value:
            cursor.execute("""
                INSERT OR REPLACE INTO objectives (
                    id, model_name, magnification, numerical_aperture, working_distance_mm,
                    thread_type, immersion_type, parfocal_distance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product.id,
                product.model_name,
                float(product.specs.get("magnification", 10.0)),
                float(product.specs.get("numerical_aperture", 0.25)),
                float(product.specs.get("working_distance_mm", 0.0)),
                str(product.specs.get("thread_type", "M25")),
                str(product.specs.get("immersion_type", "air")),
                float(product.specs.get("parfocal_distance", 45.0))
            ))

        elif cat_val == ProductCategory.ILLUMINATION.value:
            cursor.execute("""
                INSERT OR REPLACE INTO illumination (id, model_name, light_source_type, lifetime_hours, color_temp_k)
                VALUES (?, ?, ?, ?, ?)
            """, (
                product.id,
                product.model_name,
                str(product.specs.get("light_source_type", "LED")),
                int(product.specs.get("lifetime_hours", 20000)),
                int(product.specs.get("color_temp_k", 5600))
            ))

        elif cat_val == ProductCategory.ACCESSORY.value:
            cursor.execute("""
                INSERT OR REPLACE INTO accessories (id, model_name, accessory_type, mount_type, magnification)
                VALUES (?, ?, ?, ?, ?)
            """, (
                product.id,
                product.model_name,
                str(product.specs.get("accessory_type", "camera_adapter")),
                str(product.specs.get("mount_type", "C-Mount")),
                float(product.specs["magnification"]) if "magnification" in product.specs else None
            ))

        self.conn.commit()

    def bulk_add_products(self, products: List[BaseProduct]) -> int:
        """Informs catalog of a batch of products and returns successfully added count."""
        count = 0
        for p in products:
            self.add_product(p)
            count += 1
        return count

    def get_product(self, product_id: str) -> Optional[BaseProduct]:
        """Deterministic product retrieval by primary ID/SKU ($0 cost)."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_product(row)

    def search_by_model(self, model_name_query: str) -> List[BaseProduct]:
        """Substring lookup on model_name ($0 cost)."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE model_name LIKE ? ORDER BY model_name ASC", (f"%{model_name_query}%",))
        rows = cursor.fetchall()
        return [self._row_to_product(r) for r in rows]

    def lookup_zero_llm(
        self,
        category: Optional[Union[ProductCategory, str]] = None,
        optical_standard: Optional[str] = None,
        specs_filter: Optional[Dict[str, Any]] = None,
        limit: int = 50
    ) -> List[BaseProduct]:
        """
        Zero-LLM deterministic catalog search using direct relational criteria and spec matching.
        Operates with 0 LLM token cost.
        """
        query = "SELECT * FROM products WHERE 1=1"
        params: List[Any] = []

        if category:
            cat_str = category.value if isinstance(category, Enum) else str(category)
            query += " AND category = ?"
            params.append(cat_str)

        if optical_standard:
            query += " AND optical_standard = ?"
            params.append(optical_standard)

        query += " ORDER BY id ASC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = [self._row_to_product(r) for r in rows]

        # Apply specific in-memory specs_filter matching if requested
        if specs_filter:
            filtered = []
            for prod in results:
                match = True
                for k, expected_v in specs_filter.items():
                    actual_v = prod.specs.get(k)
                    if isinstance(expected_v, list):
                        if actual_v not in expected_v and not (isinstance(actual_v, list) and any(item in expected_v for item in actual_v)):
                            match = False
                            break
                    elif actual_v != expected_v:
                        match = False
                        break
                if match:
                    filtered.append(prod)
            return filtered

        return results

    def search_vector_similarity(
        self,
        query_vector: List[float],
        top_k: int = 5,
        category: Optional[Union[ProductCategory, str]] = None
    ) -> List[Tuple[BaseProduct, float]]:
        """
        Performs deterministic vector cosine similarity search over stored product embeddings.
        Returns sorted list of (BaseProduct, similarity_score) tuples.
        """
        cursor = self.conn.cursor()
        if category:
            cat_str = category.value if isinstance(category, Enum) else str(category)
            cursor.execute("SELECT * FROM products WHERE embedding_json IS NOT NULL AND category = ?", (cat_str,))
        else:
            cursor.execute("SELECT * FROM products WHERE embedding_json IS NOT NULL")
        
        rows = cursor.fetchall()
        scored_products: List[Tuple[BaseProduct, float]] = []

        for r in rows:
            prod = self._row_to_product(r)
            if not prod.embedding:
                continue
            
            score = self._cosine_similarity(query_vector, prod.embedding)
            scored_products.append((prod, score))

        scored_products.sort(key=lambda x: x[1], reverse=True)
        return scored_products[:top_k]

    def hybrid_lookup(
        self,
        query_text: Optional[str] = None,
        query_vector: Optional[List[float]] = None,
        category: Optional[Union[ProductCategory, str]] = None,
        specs_filter: Optional[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Combines zero-LLM spec filtering with vector similarity ranking for robust hybrid search.
        """
        # Step 1: Get spec/category filtered candidates
        candidates = self.lookup_zero_llm(category=category, specs_filter=specs_filter, limit=100)

        # Filter candidates by text substring if provided
        if query_text:
            q_lower = query_text.lower()
            candidates = [
                c for c in candidates
                if q_lower in c.model_name.lower() or q_lower in c.description.lower() or q_lower in str(c.specs).lower()
            ]

        results = []
        for prod in candidates:
            sim_score = 0.0
            if query_vector and prod.embedding:
                sim_score = self._cosine_similarity(query_vector, prod.embedding)
            
            results.append({
                "product": prod,
                "similarity_score": round(sim_score, 4),
                "deterministic_match": True
            })

        if query_vector:
            results.sort(key=lambda x: x["similarity_score"], reverse=True)

        return results[:top_k]

    def get_catalog_stats(self) -> Dict[str, Any]:
        """Returns diagnostic counts and metadata for catalog health monitoring."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT category, COUNT(*) as cnt FROM products GROUP BY category")
        cat_counts = {row["category"]: row["cnt"] for row in cursor.fetchall()}
        
        cursor.execute("SELECT COUNT(*) as total FROM products")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as embedded FROM products WHERE embedding_json IS NOT NULL")
        embedded = cursor.fetchone()["embedded"]

        return {
            "total_products": total,
            "embedded_products": embedded,
            "category_counts": cat_counts
        }

    def _row_to_product(self, row: sqlite3.Row) -> BaseProduct:
        """Converts an SQLite row into appropriate BaseProduct or domain model instance."""
        specs = json.loads(row["specs_json"]) if row["specs_json"] else {}
        embedding = json.loads(row["embedding_json"]) if row["embedding_json"] else None
        
        anchor = None
        if row["source_url"]:
            anchor = SourceAnchor(
                source_url=row["source_url"],
                doc_reference=row["doc_reference"] or "Official Specification",
                verified=bool(row["verified"]),
                checksum=row["checksum"] or ""
            )

        cat_str = row["category"]
        product_data = {
            "id": row["id"],
            "model_name": row["model_name"],
            "category": cat_str,
            "optical_standard": row["optical_standard"] or "UIS2",
            "arabic_name": row["arabic_name"],
            "description": row["description"] or "",
            "specs": specs,
            "embedding": embedding,
            "source_anchor": anchor,
            "is_mock": bool(row["is_mock"])
        }

        if cat_str == ProductCategory.STAND.value:
            return StandProduct(**product_data)
        elif cat_str == ProductCategory.OBJECTIVE.value:
            return ObjectiveProduct(**product_data)
        elif cat_str == ProductCategory.ILLUMINATION.value:
            return IlluminationProduct(**product_data)
        elif cat_str == ProductCategory.ACCESSORY.value:
            return AccessoryProduct(**product_data)

        return BaseProduct(**product_data)

    @staticmethod
    def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """Calculates cosine similarity between two vector float lists."""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_v1 = math.sqrt(sum(a * a for a in v1))
        norm_v2 = math.sqrt(sum(b * b for b in v2))
        
        if norm_v1 == 0.0 or norm_v2 == 0.0:
            return 0.0
        
        return dot_product / (norm_v1 * norm_v2)
