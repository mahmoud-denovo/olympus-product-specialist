import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from olympus_specialist.domain.compatibility.rules import validate_stand_optics
from olympus_specialist.domain.products.catalog import ProductCatalog
from olympus_specialist.self_healing.remediation import SelfHealingEngine
from olympus_specialist.telemetry.hierarchical_tracker import HierarchicalTokenTracker

def test_direct_subagent_invocations():
    print("==================================================================")
    print("TESTING DIRECT SUBAGENT INVOCATIONS IN ISOLATION")
    print("==================================================================")
    
    tracker = HierarchicalTokenTracker(session_id="direct_subagent_test_session")

    # 1. Directly invoke: Optical Hardware Compatibility Subagent ($0 Local)
    print("\n[1] Directly Invoking: Optical Hardware Compatibility Subagent...")
    optics_res = validate_stand_optics(stand_id="BX53M", observation_mode="Darkfield", objective_series="MPLFLN-BD")
    tracker.register_agent("optical_compatibility_validator", "Optical Hardware Compatibility Subagent", "L1 Rules Engine", "root")
    tracker.record_usage("optical_compatibility_validator", "local-agy-pool", 150, 80)
    print("-> Response:", json.dumps(optics_res, indent=2))

    # 2. Directly invoke: Evident Catalog Provenance Subagent
    print("\n[2] Directly Invoking: Evident Catalog Provenance Subagent...")
    catalog = ProductCatalog()
    products = catalog.search_by_model("BX53M")
    tracker.register_agent("evident_catalog_provenance", "Evident Catalog Provenance Subagent", "Catalog Lookup", "root")
    tracker.record_usage("evident_catalog_provenance", "gemini-2.5-flash-lite", 180, 100)
    print(f"-> Response: Found {len(products)} matching product(s).")
    if products:
        print("-> Primary Product Details:", json.dumps(products[0].dict(), indent=2, default=str))

    # 3. Directly invoke: HitL Interactive Clarification & Self-Healing Subagent
    print("\n[3] Directly Invoking: Self-Healing & Clarification Subagent...")
    healing = SelfHealingEngine()
    remediation_res = healing.diagnose_and_repair(
        session_id="direct_subagent_test_session",
        step_index=1,
        error=ValueError("Missing required input slots"),
        missing_slots=["observation_mode", "objective_series"]
    )
    tracker.register_agent("hitl_clarification", "HitL Clarification Subagent", "Clarification Engine", "root")
    tracker.record_usage("hitl_clarification", "gemini-2.5-flash", 120, 90)
    print("-> Response:", json.dumps(remediation_res, indent=2))

    print("\n==================================================================")
    print("DIRECT SUBAGENT INVOCATION SUMMARY & TELEMETRY")
    print("==================================================================")
    print("Recorded Agents in Session:", list(tracker.nodes.keys()))

if __name__ == "__main__":
    test_direct_subagent_invocations()
