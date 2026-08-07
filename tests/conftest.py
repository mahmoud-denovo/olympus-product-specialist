"""
Pytest configuration and shared fixtures for olympus-product-specialist test suite.
"""

import os
import sys
import tempfile
import sqlite3
import pytest
from pathlib import Path

# Add project root directory to python path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def temp_db_path(tmp_path):
    """Provides a temporary SQLite database path for Knowledge Graph testing."""
    db_file = tmp_path / "test_knowledge_graph.db"
    return str(db_file)


@pytest.fixture
def initialized_db(temp_db_path):
    """Creates a temporary SQLite database initialized with schema and sample optical rules."""
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    
    # Table: components
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS components (
            id TEXT PRIMARY KEY,
            model_name TEXT NOT NULL,
            category TEXT NOT NULL,
            thread_type TEXT,
            parfocal_distance REAL,
            sensor_format TEXT,
            optical_standard TEXT DEFAULT 'UIS2',
            arabic_name TEXT,
            english_specs TEXT
        );
    """)
    
    # Table: compatibility_rules
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compatibility_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_a TEXT NOT NULL,
            category_b TEXT NOT NULL,
            rule_type TEXT NOT NULL,
            allowed_values TEXT,
            required_adapter TEXT,
            lockout_message TEXT
        );
    """)

    # Table: web_cache
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS web_cache (
            url TEXT PRIMARY KEY,
            model_number TEXT NOT NULL,
            verified INTEGER NOT NULL,
            html_content TEXT,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Seed sample components
    cursor.executemany("""
        INSERT INTO components (id, model_name, category, thread_type, parfocal_distance, sensor_format, optical_standard, arabic_name, english_specs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, [
        ("IX73", "Olympus IX73", "frame", "RMS", 45.0, "Full Frame", "UIS2", "إطار مجهر مقلوب IX73", '{"ports": 2, "light_path": "inverted"}'),
        ("UPLSAPO60XO", "UPLSAPO 60XO", "objective", "M25", 45.0, "Full Frame", "UIS2", "عدسة شيئية زيتية UPLSAPO 60X", '{"mag": 60, "na": 1.42, "immersion": "oil"}'),
        ("DP74", "Olympus DP74", "camera", "C-Mount", 17.5, "1.1 inch", "UIS2", "كاميرا رقمية بدقة عالية DP74", '{"resolution": "20.7MP", "sensor": "CMOS"}'),
        ("U-TV1X-2", "U-TV1X-2", "camera_adapter", "C-Mount", 45.0, "1 inch", "UIS2", "محول كاميرا 1X", '{"mag": 1.0, "mount": "C-Mount"}'),
        ("LED-ILL", "Transmitted LED", "light_source", "Standard Bayonet", 0.0, "N/A", "UIS2", "مصدر إضاءة LED نافذ", '{"lifetime_hours": 20000, "color_temp": 5600}')
    ])

    # Seed optical compatibility rules
    cursor.executemany("""
        INSERT INTO compatibility_rules (category_a, category_b, rule_type, allowed_values, required_adapter, lockout_message)
        VALUES (?, ?, ?, ?, ?, ?);
    """, [
        ("objective", "frame", "thread_match", "M25", "M25-to-RMS-Adapter", "Objective thread mismatch: requires M25 adapter for RMS nosepiece"),
        ("camera", "camera_adapter", "mount_match", "C-Mount", None, "Camera mount mismatch"),
        ("objective", "frame", "optical_standard", "UIS2", None, "Non-UIS2 optical standard incompatible with Olympus frames")
    ])

    conn.commit()
    conn.close()
    return temp_db_path


@pytest.fixture
def sample_optical_components():
    """Provides a set of valid optical component dictionaries for assembly scenarios."""
    return {
        "frame": {
            "id": "IX73",
            "model_name": "Olympus IX73",
            "category": "frame",
            "thread_type": "RMS",
            "parfocal_distance": 45.0,
            "sensor_format": "Full Frame",
            "optical_standard": "UIS2"
        },
        "light_source": {
            "id": "LED-ILL",
            "model_name": "Transmitted LED",
            "category": "light_source",
            "thread_type": "Standard Bayonet",
            "parfocal_distance": 0.0,
            "sensor_format": "N/A",
            "optical_standard": "UIS2"
        },
        "objective": {
            "id": "UPLSAPO60XO",
            "model_name": "UPLSAPO 60XO",
            "category": "objective",
            "thread_type": "M25",
            "parfocal_distance": 45.0,
            "sensor_format": "Full Frame",
            "optical_standard": "UIS2"
        },
        "objectives": {
            "id": "UPLSAPO60XO",
            "model_name": "UPLSAPO 60XO",
            "category": "objective",
            "thread_type": "M25",
            "parfocal_distance": 45.0,
            "sensor_format": "Full Frame",
            "optical_standard": "UIS2"
        },
        "camera_adapter": {
            "id": "U-TV1X-2",
            "model_name": "U-TV1X-2",
            "category": "camera_adapter",
            "thread_type": "C-Mount",
            "parfocal_distance": 45.0,
            "sensor_format": "1 inch",
            "optical_standard": "UIS2"
        },
        "software": {
            "id": "cellSens-Dim",
            "model_name": "cellSens Dimension 3.2",
            "category": "software",
            "thread_type": "N/A",
            "parfocal_distance": 0.0,
            "sensor_format": "N/A",
            "optical_standard": "UIS2"
        }
    }


@pytest.fixture
def mock_gemini_env(monkeypatch):
    """Sets up GEMINI_API_KEY environment variable for testing Gemini LLM Judge."""
    monkeypatch.setenv("GEMINI_API_KEY", "test_mock_gemini_key_12345")


@pytest.fixture
def mock_no_gemini_env(monkeypatch):
    """Clears GEMINI_API_KEY environment variable to test zero-cloud fallback."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
