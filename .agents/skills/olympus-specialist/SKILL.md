---
name: olympus-specialist
description: Official Google ADK skill for Evident Scientific / Olympus product specialist queries and optical hardware compatibility validation.
version: 1.0.0
---

# Olympus Specialist Google ADK Skill

This skill extends `agents-cli` and Google ADK with specialized tools for Evident Scientific & Olympus microscopy systems.

## Available Tools
1. `validate_stand_optics(stand_id, observation_mode, objective_series)`: Deterministic optical hardware alignment.
2. `lookup_catalog_stand(stand_name)`: Authorized Evident product catalog lookup.
3. `diagnose_and_repair(session_id, step_index, error, missing_slots)`: Autonomous self-healing remediation.

## Temperature Guidelines
- Optical Matching: `0.0`
- Provenance Scraping: `0.0`
- Interactive Clarification: `0.2`
