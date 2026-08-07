"""
Unit and Integration Tests for EAER (Extraction -> Amplification -> Evaluation -> Redo) Pipeline Engine.
"""

import pytest
from src.olympus_specialist.workflow.eaer_pipeline import EAERPipeline


@pytest.fixture
def eaer_pipeline():
    return EAERPipeline()


def test_eaer_pipeline_success_scenario_1(eaer_pipeline):
    """Test successful 4-stage pipeline execution for metallurgical darkfield scenario."""
    result = eaer_pipeline.run_pipeline(
        session_id="test_sess_001",
        user_request="Metallurgical defect analysis with 50x darkfield imaging.",
        stand_id="BX53M",
        observation_mode="Darkfield",
        objective_series="MPLFLN-BD",
        scenario_id="scenario_001_metallurgical_darkfield"
    )

    assert result["status"] == "SUCCESS"
    assert result["optical_configuration"]["compatible"] is True
    assert result["optical_configuration"]["stand_id"] == "BX53M"
    assert result["scorecard"]["passed"] is True
    assert result["scorecard"]["score"] >= 0.80
    assert "evidentscientific.com" in result["provenance"]


def test_eaer_pipeline_success_scenario_2(eaer_pipeline):
    """Test successful 4-stage pipeline execution for biological fluorescence scenario."""
    result = eaer_pipeline.run_pipeline(
        session_id="test_sess_002",
        user_request="Inverted microscope for live cell fluorescence imaging.",
        stand_id="IX73",
        observation_mode="Fluorescence",
        objective_series="UPLAPO",
        scenario_id="scenario_002_biological_fluorescence"
    )

    assert result["status"] == "SUCCESS"
    assert result["optical_configuration"]["compatible"] is True
    assert result["optical_configuration"]["stand_id"] == "IX73"
    assert result["scorecard"]["passed"] is True
    assert result["scorecard"]["score"] >= 0.80


def test_eaer_pipeline_redo_on_incompatible_optics(eaer_pipeline):
    """Test stage 4 Redo/Remediation trigger when optics are incompatible."""
    result = eaer_pipeline.run_pipeline(
        session_id="test_sess_redo_optics",
        user_request="Educational microscope with darkfield fluorescence",
        stand_id="CX23",  # CX23 only supports Brightfield and Plan Achromat
        observation_mode="Darkfield",
        objective_series="UPLAPO",
        scenario_id="scenario_001_metallurgical_darkfield"
    )

    assert result["status"] == "HEALING_REQUIRED"
    assert "remediation" in result
    assert result["remediation"]["needs_user_clarification"] is False
    assert "scorecard" in result


def test_eaer_pipeline_redo_on_missing_slots(eaer_pipeline):
    """Test stage 4 Redo/Remediation trigger when input slots are missing."""
    result = eaer_pipeline.run_pipeline(
        session_id="test_sess_missing_slots",
        user_request="Need microscope analysis",
        stand_id="",
        observation_mode="",
        objective_series="",
        scenario_id="scenario_001_metallurgical_darkfield"
    )

    assert result["status"] == "HEALING_REQUIRED"
    assert result["remediation"]["needs_user_clarification"] is True
    assert "stand_id" in result["remediation"]["missing_slots"]
    assert "observation_mode" in result["remediation"]["missing_slots"]
    assert "objective_series" in result["remediation"]["missing_slots"]


def test_eaer_pipeline_redo_on_low_score(eaer_pipeline):
    """Test stage 4 Redo/Remediation trigger when LocalJudge score < 0.80."""
    result = eaer_pipeline.run_pipeline(
        session_id="test_sess_low_score",
        user_request="Metallurgical inspection",
        stand_id="BX53M",
        observation_mode="Darkfield",
        objective_series="MPLN",  # MPLN is compatible with BX53M but doesn't match expected MPLFLN-BD in scenario_001
        scenario_id="scenario_001_metallurgical_darkfield"
    )

    assert result["status"] == "HEALING_REQUIRED"
    assert result["scorecard"]["score"] < 0.80
    assert result["scorecard"]["passed"] is False
