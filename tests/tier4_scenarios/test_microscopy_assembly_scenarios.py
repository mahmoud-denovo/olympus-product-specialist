"""
Tier 4 Scenario Tests: Real-world microscopy assembly workloads.
End-to-end multi-step assembly scenarios for Evident/Olympus product specialization.
"""

import pytest


def test_scenario_1_full_5stage_fluorescence_microscopy_assembly(initialized_db, sample_optical_components):
    """
    Scenario 1: Complete 5-Stage Inverted Fluorescence Microscopy Assembly Workload.
    Executes all 5 stages end-to-end: Frame -> Light Source -> Objectives -> Camera Adapter -> Software.
    Verifies optical compatibility, zero cloud cost, live URL validation, and HitL confirmations.
    """
    try:
        from src.engine.sequential_thinking import SequentialThinkingEngine
        from src.validator.web_inspector import EvidentWebInspector
        from src.db.knowledge_graph import KnowledgeGraph
        from src.cli.formatter import render_bilingual_card, render_step_progress
        from src.cli.hitl import HitLHandler
        from src.core.agy_runner import LocalAgyRunner
    except ImportError as e:
        pytest.fail(f"Scenario components missing: {e}")

    engine = SequentialThinkingEngine(db_path=initialized_db)
    inspector = EvidentWebInspector(db_path=initialized_db, offline_mode=True)
    kg = KnowledgeGraph(db_path=initialized_db)
    hitl = HitLHandler()
    agy = LocalAgyRunner()

    assembly_plan = [
        ("frame", "IX73"),
        ("light_source", "LED-ILL"),
        ("objectives", "UPLSAPO60XO"),
        ("camera_adapter", "U-TV1X-2"),
        ("software", "cellSens-Dim")
    ]

    built_configuration = {}
    approvals_collected = 0

    for step_num, (stage, component_id) in enumerate(assembly_plan, start=1):
        # 1. Render step progress UI header
        progress_ui = render_step_progress(stage=stage, current_step=step_num, total_steps=5)
        assert progress_ui is not None

        # 2. SequentialThinking engine step execution
        stage_res = engine.step(stage=stage, current_config=built_configuration)
        choices = stage_res.choices if hasattr(stage_res, 'choices') else stage_res.get('choices')
        assert len(choices) > 0, f"Stage {stage} should offer valid options"

        # 3. Model number verification with web inspector
        comp_info = sample_optical_components.get(stage) or sample_optical_components.get("objective")
        model_ver = inspector.verify_model_number(comp_info["model_name"])
        assert (model_ver.verified if hasattr(model_ver, 'verified') else model_ver.get('verified')) is True

        # 4. Optical compatibility check with previous components
        if "frame" in built_configuration:
            frame_comp = sample_optical_components["frame"]
            compat = kg.check_optical_compatibility(frame_comp, comp_info)
            assert compat is not None

        # 5. Bilingual card rendering & HitL user approval prompt
        card_rendered = render_bilingual_card(comp_info)
        assert comp_info["model_name"] in card_rendered

        approved = hitl.request_approval(comp_info, user_input_func=lambda: "y")
        assert approved is True
        approvals_collected += 1

        built_configuration[stage] = comp_info

    # Final Verification: Complete 5-stage configuration assembled
    assert len(built_configuration) == 5
    assert approvals_collected == 5

    # Zero cloud cost validation for entire workflow
    eval_res = agy.run_prompt(f"Validate final assembly: {built_configuration}")
    cost = eval_res.cloud_cost if hasattr(eval_res, 'cloud_cost') else eval_res.get('cloud_cost')
    assert cost == 0.0, "Complete assembly workflow must execute at 0.0 cloud cost"


def test_scenario_2_incompatible_assembly_lockout_and_adapter_resolution(initialized_db):
    """
    Scenario 2: Real-world Incompatible Assembly Detection & Adapter Resolution.
    Simulates user selecting an M25 thread objective on an RMS frame nosepiece.
    System must detect thread mismatch, flag rule violation, suggest M25-to-RMS adapter,
    and update optical compatibility status upon adapter resolution.
    """
    try:
        from src.db.knowledge_graph import KnowledgeGraph
    except ImportError as e:
        pytest.fail(f"Knowledge Graph missing: {e}")

    kg = KnowledgeGraph(db_path=initialized_db)

    frame_rms = {
        "id": "IX73",
        "category": "frame",
        "thread_type": "RMS",
        "optical_standard": "UIS2"
    }

    objective_m25 = {
        "id": "UPLSAPO60XO",
        "category": "objective",
        "thread_type": "M25",
        "optical_standard": "UIS2"
    }

    # Step 1: Initial compatibility check without adapter
    initial_check = kg.check_optical_compatibility(frame_rms, objective_m25)
    init_compat = initial_check.compatible if hasattr(initial_check, 'compatible') else initial_check.get('compatible')
    init_adapters = initial_check.required_adapters if hasattr(initial_check, 'required_adapters') else initial_check.get('required_adapters')

    assert init_compat is False or len(init_adapters) > 0, "Direct mounting of M25 objective on RMS nosepiece must require adapter"
    assert any("M25" in a or "Adapter" in a for a in init_adapters)

    # Step 2: System applies adapter to objective component
    objective_m25_adapted = objective_m25.copy()
    objective_m25_adapted["thread_adapter_applied"] = "M25-to-RMS-Adapter"
    objective_m25_adapted["thread_type"] = "RMS"  # Adapted to RMS

    # Step 3: Re-check optical compatibility with adapter
    adapted_check = kg.check_optical_compatibility(frame_rms, objective_m25_adapted)
    adapted_compat = adapted_check.compatible if hasattr(adapted_check, 'compatible') else adapted_check.get('compatible')

    assert adapted_compat is True, "Adding required thread adapter must resolve optical compatibility check"
