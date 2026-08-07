from typing import Dict, Any, List

# Deterministic Optical Matching Rules ($0 Cost - No LLM)
STAND_COMPATIBILITY_MATRIX = {
    "BX53M": {
        "type": "Upright Metallurgical",
        "supported_modes": ["Brightfield", "Darkfield", "Polarized", "DIC"],
        "compatible_objectives": ["MPLFLN-BD", "LMPLFLN-BD", "MPLN"],
        "recommended_software": "PRECiV"
    },
    "GX53": {
        "type": "Inverted Metallurgical",
        "supported_modes": ["Brightfield", "Darkfield", "DIC"],
        "compatible_objectives": ["LMPLFLN-BD", "MPLFLN-BD"],
        "recommended_software": "PRECiV"
    },
    "IX73": {
        "type": "Inverted Biological",
        "supported_modes": ["Brightfield", "Fluorescence", "Phase Contrast"],
        "compatible_objectives": ["UPLAPO", "LUCPLFLN", "UPLFLN"],
        "recommended_software": "cellSens / PRECiV"
    },
    "CX23": {
        "type": "Educational / Clinical Upright",
        "supported_modes": ["Brightfield"],
        "compatible_objectives": ["Plan Achromat"],
        "recommended_software": "Basic EP50 Camera"
    }
}

def validate_stand_optics(stand_id: str, observation_mode: str, objective_series: str) -> Dict[str, Any]:
    """Validates optical compatibility deterministically without LLM calls."""
    stand = STAND_COMPATIBILITY_MATRIX.get(stand_id)
    if not stand:
        return {
            "compatible": False,
            "reason": f"Unknown stand model '{stand_id}'."
        }
        
    if observation_mode not in stand["supported_modes"]:
        return {
            "compatible": False,
            "reason": f"Stand '{stand_id}' does not support observation mode '{observation_mode}'."
        }
        
    if objective_series not in stand["compatible_objectives"]:
        return {
            "compatible": False,
            "reason": f"Objective series '{objective_series}' is incompatible with stand '{stand_id}'."
        }
        
    return {
        "compatible": True,
        "stand_id": stand_id,
        "type": stand["type"],
        "mode": observation_mode,
        "objective_series": objective_series,
        "recommended_software": stand["recommended_software"]
    }
