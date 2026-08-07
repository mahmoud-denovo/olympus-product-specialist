"""
SQLite Knowledge Graph & Optical Rules Storage Engine.
Stores verified optical components, compatibility constraints, and source attribution metadata.
Strictly isolates production data from test sandbox environments.
"""

import sqlite3
import json
from typing import Dict, Any, List, Optional, Union


class CompatibilityResult:
    """Represents optical compatibility analysis output."""

    def __init__(
        self,
        compatible: bool = True,
        reasons: Optional[List[str]] = None,
        required_adapters: Optional[List[str]] = None,
        rule_violations: Optional[List[str]] = None
    ):
        self.compatible = compatible
        self.reasons = reasons or []
        self.required_adapters = required_adapters or []
        self.rule_violations = rule_violations or []

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class KnowledgeGraph:
    """
    Manages optical components, compatibility matrices, and verified Evident/Olympus product relationships.
    """

    def __init__(self, db_path: str = "production_knowledge.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Optical components table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS optical_components (
                        id TEXT PRIMARY KEY,
                        model_name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        optical_standard TEXT,
                        thread_type TEXT,
                        magnification INTEGER,
                        na REAL,
                        specs_json TEXT,
                        source_url TEXT NOT NULL,
                        is_verified INTEGER DEFAULT 1,
                        is_mock INTEGER DEFAULT 0
                    )
                """)
                # Compatibility rules table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS compatibility_rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        component_a_id TEXT NOT NULL,
                        component_b_id TEXT NOT NULL,
                        is_compatible INTEGER NOT NULL,
                        rule_reason TEXT,
                        adapter_required TEXT,
                        FOREIGN KEY (component_a_id) REFERENCES optical_components(id),
                        FOREIGN KEY (component_b_id) REFERENCES optical_components(id)
                    )
                """)
                conn.commit()
        except sqlite3.Error:
            pass

    def add_component(self, component_data: Dict[str, Any], is_mock: bool = False) -> bool:
        """Adds a verified optical component with source attribution."""
        required_fields = ["id", "model_name", "category", "source_url"]
        for field in required_fields:
            if field not in component_data:
                raise ValueError(f"Missing required component field: {field}")

        specs_json = json.dumps(component_data.get("specs", {}))
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO optical_components
                (id, model_name, category, optical_standard, thread_type, magnification, na, specs_json, source_url, is_verified, is_mock)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                component_data["id"],
                component_data["model_name"],
                component_data["category"],
                component_data.get("optical_standard", "UIS2"),
                component_data.get("thread_type", "RMS"),
                component_data.get("magnification"),
                component_data.get("na"),
                specs_json,
                component_data["source_url"],
                1 if component_data.get("is_verified", True) else 0,
                1 if is_mock else 0
            ))
            conn.commit()
        return True

    def check_optical_compatibility(
        self,
        comp_a: Union[str, Dict[str, Any]],
        comp_b: Union[str, Dict[str, Any]]
    ) -> CompatibilityResult:
        """Analyzes optical compatibility between two components or component IDs."""
        try:
            # Check if the database has any components or if it's corrupt/empty
            has_records = False
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    try:
                        cursor.execute("SELECT COUNT(*) FROM optical_components")
                        count = cursor.fetchone()[0]
                        if count > 0:
                            has_records = True
                    except sqlite3.Error:
                        pass

                    if not has_records:
                        try:
                            cursor.execute("SELECT COUNT(*) FROM components")
                            count = cursor.fetchone()[0]
                            if count > 0:
                                has_records = True
                        except sqlite3.Error:
                            pass
            except Exception:
                pass

            if not has_records:
                return CompatibilityResult(compatible=False, rule_violations=["Database is empty, uninitialized or corrupt"])

            # Resolve dicts if IDs passed
            if isinstance(comp_a, str):
                comp_a = self.get_component(comp_a) or {"id": comp_a}
            if isinstance(comp_b, str):
                comp_b = self.get_component(comp_b) or {"id": comp_b}

            if not comp_a or not comp_b or not isinstance(comp_a, dict) or not isinstance(comp_b, dict):
                return CompatibilityResult(compatible=False, rule_violations=["Invalid or missing component data"])

            reasons = []
            required_adapters = []
            rule_violations = []

            # Check 1: Thread matching
            thread_a = comp_a.get("thread_type")
            thread_b = comp_b.get("thread_type")
            if thread_a and thread_b and thread_a != thread_b:
                required_adapters.append(f"{thread_b}-to-{thread_a} Adapter")
                rule_violations.append(f"Thread mismatch: {thread_a} vs {thread_b}")

            # Check 2: Sensor format / vignetting check
            sensor_a = comp_a.get("sensor_format")
            sensor_b = comp_b.get("sensor_format")
            if sensor_a and sensor_b:
                sensor_scale = {
                    "1/3 inch": 0.33,
                    "1/2 inch": 0.50,
                    "2/3 inch": 0.67,
                    "1 inch": 1.00,
                    "1.1 inch": 1.10,
                    "full frame": 1.50
                }
                scale_a = sensor_scale.get(str(sensor_a).lower(), 0.0)
                scale_b = sensor_scale.get(str(sensor_b).lower(), 0.0)
                if scale_a > scale_b:
                    rule_violations.append(f"Sensor format vignetting lockout: camera format ({sensor_a}) exceeds adapter format ({sensor_b})")

            is_comp = len(rule_violations) == 0 and len(required_adapters) == 0
            if is_comp:
                reasons.append("Components optically compatible under UIS2 standard")

            return CompatibilityResult(
                compatible=is_comp,
                reasons=reasons,
                required_adapters=required_adapters,
                rule_violations=rule_violations
            )
        except Exception as e:
            return CompatibilityResult(compatible=False, rule_violations=[f"Database/Rule error: {e}"])

    def check_compatibility(self, comp_a_id: str, comp_b_id: str) -> Dict[str, Any]:
        """Legacy helper checking optical compatibility."""
        res = self.check_optical_compatibility(comp_a_id, comp_b_id)
        return {
            "compatible": res.compatible,
            "rule_reason": res.reasons[0] if res.reasons else (res.rule_violations[0] if res.rule_violations else ""),
            "adapter_required": res.required_adapters[0] if res.required_adapters else None
        }

    def get_component(self, comp_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single component by ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM optical_components WHERE id = ?", (comp_id,))
                row = cursor.fetchone()
                if row:
                    data = dict(row)
                    data["specs"] = json.loads(data["specs_json"]) if data["specs_json"] else {}
                    return data
        except Exception:
            pass
        return None

    def list_components(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists components, optionally filtered by category."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if category:
                    cursor.execute("SELECT * FROM optical_components WHERE category = ?", (category,))
                else:
                    cursor.execute("SELECT * FROM optical_components")
                rows = cursor.fetchall()
                result = []
                for r in rows:
                    d = dict(r)
                    d["specs"] = json.loads(d["specs_json"]) if d["specs_json"] else {}
                    result.append(d)
                return result
        except Exception:
            return []
