# BRIEFING — 2026-08-05T08:24:00Z

## Mission
Discover and document technical specifications, product lines, optical compatibility rules, SQLite Knowledge Graph schema, and web inspector validation rules for Evident/Olympus microscopy products.

## 🔒 My Identity
- Archetype: Survey Spec Miner 3
- Roles: Specification Miner
- Working directory: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_spec_miner_survey_3
- Original parent: acb84067-edb8-4ea2-aeb4-195071969a6c
- Milestone: Technical Specification Discovery & Schema Definition

## 🔒 Key Constraints
- Read-only on implementation (do not write application code outside agent metadata directory).
- Discover and document features in table format.
- Output findings to `analysis.md` and `handoff.md` in agent metadata directory.
- No shortcuts or cheating — probe actual specs, standards, domain knowledge, and web sources if necessary.

## Current Parent
- Conversation ID: acb84067-edb8-4ea2-aeb4-195071969a6c
- Updated: 2026-08-05T08:24:00Z

## Task Summary
- **What was mined**:
  1. Technical specifications for Evident/Olympus microscopy products & configurations (Frame, Light Source, Objectives, Camera Adapters, Software).
  2. Evident/Olympus product lines (IX, BX, SZX, CX series, DP series cameras, cellSens/OlyVIA software, UIS2 optical system standards, C-mount adapters, filter cubes, lamp houses).
  3. Data schema and rule structure for local SQLite Knowledge Graph to enforce optical compatibility.
  4. Web inspector validation rules for URL domain checking and model number verification.
- **Success criteria**:
  - Comprehensive `analysis.md` detailing product lines, optical rules, SQLite schema, web inspector rules, edge cases, feature tables.
  - Complete 5-component `handoff.md`.
- **Interface contracts**: ORIGINAL_REQUEST.md & DISPATCH.md

## Key Decisions Made
- Structured Knowledge Graph schema with normalized relational tables (`components`, `mount_interfaces`, `component_mounts`, `optical_paths`, `software_compatibility`, `compatibility_rules`, `configuration_presets`).
- Defined explicit SQL-based rule evaluation logic for objective thread compatibility (RMS vs M25 vs M32), parfocality (45mm vs 60mm), optical tube length (infinity f=180mm), filter cube generation lockouts (U-MF2 vs U-FF), camera sensor vs coupler magnification matching, and software driver version constraints.
- Defined Web Inspector domain whitelist and category-specific regex rules for model number validation.

## Artifact Index
- `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_spec_miner_survey_3/DISPATCH.md` — Prompt assignment log
- `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_spec_miner_survey_3/BRIEFING.md` — Briefing document
- `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_spec_miner_survey_3/progress.md` — Progress log
- `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_spec_miner_survey_3/analysis.md` — Detailed spec analysis report
- `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_spec_miner_survey_3/handoff.md` — 5-component handoff report
