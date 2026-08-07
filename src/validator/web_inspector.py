"""
Live Evident/Olympus Web Inspector & Validator Module.
Provides official domain whitelist validation and model number regex verification.
"""

import re
import urllib.parse
from typing import Dict, Any, Optional

OFFICIAL_DOMAINS = [
    "evident-scientific.com",
    "www.evident-scientific.com",
    "olympus-lifescience.com",
    "www.olympus-lifescience.com"
]

OFFICIAL_BASE_DOMAINS = [
    "evident-scientific.com",
    "olympus-lifescience.com"
]


class ValidationResult:
    """Result object for URL domain whitelist validation."""

    def __init__(self, valid: bool, domain_whitelisted: bool, url: str, error: Optional[str] = None, cached: bool = False):
        self.valid = valid
        self.domain_whitelisted = domain_whitelisted
        self.url = url
        self.error = error
        self.cached = cached

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class ModelVerificationResult:
    """Result object for model number verification."""

    def __init__(self, verified: bool, cached: bool = False, model_name: str = "", details: Optional[Dict[str, Any]] = None):
        self.verified = verified
        self.cached = cached
        self.model_name = model_name
        self.details = details or {}

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class EvidentWebInspector:
    """
    Real-time validator checking specs and links against official Evident/Olympus domains.
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        offline_mode: bool = False,
        offline_cache: Optional[Dict[str, Any]] = None
    ):
        self.db_path = db_path
        self.offline_mode = offline_mode
        self.offline_cache = offline_cache or {}
        self.session_logs = []

    def is_official_domain(self, url: str) -> bool:
        if not url or not url.strip():
            return False
        try:
            parsed = urllib.parse.urlparse(url.strip())
            if parsed.scheme not in ["http", "https"]:
                return False

            # Check path traversal attempts
            if ".." in parsed.path:
                return False

            domain = parsed.netloc.lower()
            # Strip port if present
            if ":" in domain:
                domain = domain.split(":")[0]

            return any(
                domain == base or domain.endswith("." + base)
                for base in OFFICIAL_BASE_DOMAINS
            )
        except Exception:
            return False

    def validate_url(self, url: str) -> ValidationResult:
        is_whitelisted = self.is_official_domain(url)
        cached = self.offline_mode
        if is_whitelisted:
            return ValidationResult(valid=True, domain_whitelisted=True, url=url, cached=cached)
        else:
            return ValidationResult(
                valid=False,
                domain_whitelisted=False,
                url=url,
                error=f"URL '{url}' is not on an official Evident/Olympus domain.",
                cached=cached
            )

    def verify_model_number(self, model: str) -> ModelVerificationResult:
        if not model or not isinstance(model, str):
            return ModelVerificationResult(verified=False, cached=False, model_name=str(model))

        model_clean = model.strip()

        # Reject long or injection/script strings
        if len(model_clean) > 100 or len(model_clean) < 2:
            return ModelVerificationResult(verified=False, cached=False, model_name=model_clean)

        # Check for injection keywords / characters
        forbidden_patterns = [r"<script", r"select\s", r"drop\s", r"insert\s", r"delete\s", r"--", r"';", r"\/\*"]
        for pat in forbidden_patterns:
            if re.search(pat, model_clean, re.IGNORECASE):
                return ModelVerificationResult(verified=False, cached=False, model_name=model_clean)

        # Valid model regex (alphanumeric, hyphens, underscores, dots, spaces, slashes)
        if not re.match(r"^[a-zA-Z0-9\-\_\.\s/]+$", model_clean):
            return ModelVerificationResult(verified=False, cached=False, model_name=model_clean)

        is_cached = self.offline_mode or bool(self.db_path)
        return ModelVerificationResult(verified=True, cached=is_cached, model_name=model_clean)
