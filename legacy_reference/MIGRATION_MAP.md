# Legacy Reference Migration Map (Rule B-01)

This document maps legacy laws, concepts, and optical logic from `olympus-workspace-agent` to the modern `olympus-product-specialist` architecture.

## Rule B-01 Guardrail Policy
**Rule B-01 Mandate**: Zero code, calculation logic, or architectural decision from `olympus-workspace-agent` is adopted into `olympus-product-specialist` without explicit prior user presentation and Human-in-the-Loop (HitL) approval.

## Mapped Legacy Concepts

| Concept ID | Legacy Source | Description | Migration Status |
|------------|---------------|-------------|------------------|
| LEGACY_OPTICAL_CALC_RULE_42 | `olympus-workspace-agent/calc.py` | Legacy objective parfocality calculation formula | Pending User Approval |
| LEGACY_LAW_01_CAMERA_MAGNIFICATION | `olympus-workspace-agent/camera.py` | Auto-calculate tube lens factor from legacy DB | Pending User Approval |
| LEGACY_RULE_99 | `olympus-workspace-agent/rules.py` | Legacy adapter matching heuristics | Pending User Approval |

---
*Note: All items are reference concepts only until explicitly approved via Rule B-01 Guardrail.*
