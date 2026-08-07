"""
Tier 1 Feature Tests: FI-R3.1, FI-R3.2, FI-R3.3
Testing Live Evident/Olympus Web Inspector & Local SQLite Knowledge Graph.
"""

import pytest


def test_fi_r3_1_web_inspector_domain_whitelist_and_regex():
    """
    FI-R3.1: Verify live Evident/Olympus web inspector domain whitelist
    (evident-scientific.com, olympus-lifescience.com) and model number regex validation.
    """
    try:
        from src.validator.web_inspector import EvidentWebInspector
    except ImportError as e:
        pytest.fail(f"FI-R3.1 Implementation missing: {e}")

    inspector = EvidentWebInspector(offline_mode=True)  # Using whitelist verification mode

    # Valid official domain URLs
    valid_urls = [
        "https://www.evident-scientific.com/en/microscopes/inverted/ix73/",
        "https://www.olympus-lifescience.com/en/objectives/uplsapo60xo/"
    ]
    for url in valid_urls:
        res = inspector.validate_url(url)
        valid = res.valid if hasattr(res, 'valid') else res.get('valid')
        whitelisted = res.domain_whitelisted if hasattr(res, 'domain_whitelisted') else res.get('domain_whitelisted')
        assert valid is True
        assert whitelisted is True

    # Invalid / non-whitelisted domain URLs (hallucination prevention)
    invalid_urls = [
        "https://www.fake-olympus-store.com/products/ix73",
        "https://random-site.net/microscope/uplsapo"
    ]
    for url in invalid_urls:
        res = inspector.validate_url(url)
        valid = res.valid if hasattr(res, 'valid') else res.get('valid')
        whitelisted = res.domain_whitelisted if hasattr(res, 'domain_whitelisted') else res.get('domain_whitelisted')
        assert valid is False
        assert whitelisted is False

    # Model number verification via regex patterns
    model_ver = inspector.verify_model_number("UPLSAPO60XO")
    verified = model_ver.verified if hasattr(model_ver, 'verified') else model_ver.get('verified')
    assert verified is True


def test_fi_r3_2_sqlite_knowledge_graph_optical_rules(initialized_db):
    """
    FI-R3.2: Verify local SQLite Knowledge Graph schema & optical compatibility rules
    (UIS2 standard, thread matching RMS/M25/M32, parfocality, vignetting lockouts).
    """
    try:
        from src.db.knowledge_graph import KnowledgeGraph
    except ImportError as e:
        pytest.fail(f"FI-R3.2 Implementation missing: {e}")

    kg = KnowledgeGraph(db_path=initialized_db)

    # Test 1: Compatible components (RMS frame + RMS thread objective)
    comp_frame = {"id": "IX73", "category": "frame", "thread_type": "RMS", "optical_standard": "UIS2"}
    comp_obj_rms = {"id": "PLN4X", "category": "objective", "thread_type": "RMS", "optical_standard": "UIS2"}

    res1 = kg.check_optical_compatibility(comp_frame, comp_obj_rms)
    compatible1 = res1.compatible if hasattr(res1, 'compatible') else res1.get('compatible')
    assert compatible1 is True

    # Test 2: Incompatible thread requiring adapter (RMS frame + M25 thread objective)
    comp_obj_m25 = {"id": "UPLSAPO60XO", "category": "objective", "thread_type": "M25", "optical_standard": "UIS2"}

    res2 = kg.check_optical_compatibility(comp_frame, comp_obj_m25)
    compatible2 = res2.compatible if hasattr(res2, 'compatible') else res2.get('compatible')
    required_adapters = res2.required_adapters if hasattr(res2, 'required_adapters') else res2.get('required_adapters')

    assert compatible2 is False or len(required_adapters) > 0
    assert any("M25" in adapter for adapter in required_adapters)


def test_fi_r3_3_web_inspector_offline_cache_fallback(initialized_db):
    """
    FI-R3.3: Verify offline cache & fallback mechanism for web validator using local SQLite knowledge database.
    """
    try:
        from src.validator.web_inspector import EvidentWebInspector
    except ImportError as e:
        pytest.fail(f"FI-R3.3 Implementation missing: {e}")

    # Initialize web inspector in offline mode connected to knowledge graph
    inspector = EvidentWebInspector(db_path=initialized_db, offline_mode=True)

    # Query cached / offline model number verification
    res = inspector.verify_model_number("IX73")
    verified = res.verified if hasattr(res, 'verified') else res.get('verified')
    cached = res.cached if hasattr(res, 'cached') else res.get('cached')

    assert verified is True
    assert cached is True
