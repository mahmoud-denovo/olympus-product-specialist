import sys
import json
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from olympus_specialist.domain.compatibility.rules import validate_stand_optics
from olympus_specialist.domain.products.catalog import ProductCatalog, ProductCategory

def process_mcp_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Model Context Protocol (MCP) Server Handler for Evident Scientific Catalog & Optics.
    """
    tool_name = request_data.get("tool", "")
    arguments = request_data.get("arguments", {})

    if tool_name == "lookup_catalog_stand":
        stand_name = arguments.get("stand_name", "BX53M")
        catalog = ProductCatalog()
        products = catalog.search_by_model(stand_name)
        return {
            "status": "success",
            "tool": tool_name,
            "result": [p.dict() for p in products] if products else {"error": f"Stand '{stand_name}' not found."}
        }

    elif tool_name == "validate_optical_fit":
        stand_id = arguments.get("stand_id", "BX53M")
        mode = arguments.get("observation_mode", "Darkfield")
        series = arguments.get("objective_series", "MPLFLN-BD")
        res = validate_stand_optics(stand_id, mode, series)
        return {
            "status": "success",
            "tool": tool_name,
            "result": res
        }

    return {
        "status": "error",
        "error": f"Tool '{tool_name}' is not supported by Evident Catalog MCP Server."
    }

if __name__ == "__main__":
    test_req = {
        "tool": "validate_optical_fit",
        "arguments": {"stand_id": "GX53", "observation_mode": "Brightfield", "objective_series": "LMPLFLN-BD"}
    }
    print(json.dumps(process_mcp_request(test_req), indent=2))
