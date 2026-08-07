"""
Rule B-01 Guardrail Module.
Enforces zero unapproved adoption of legacy rules/code from olympus-workspace-agent.
"""

from typing import Dict, Any, Optional, Callable


class UserApprovalRequest:
    """Represents a pending request for user approval before adopting legacy logic."""

    def __init__(self, concept_id: str, details: Dict[str, Any]):
        self.concept_id = concept_id
        self.details = details

    def render_prompt_and_wait(self, user_input_func: Optional[Callable[[], str]] = None) -> bool:
        if user_input_func is not None:
            raw_response = user_input_func()
        else:
            prompt_str = f"[Rule B-01 Guardrail] Approve adoption of legacy concept '{self.concept_id}'? (yes/no): "
            raw_response = input(prompt_str)

        response = str(raw_response).strip().lower()
        # Strictly approve ONLY on explicit affirmative answers
        return response in ["y", "yes", "true", "1", "approve"]


class RuleB01Guardrail:
    """
    Enforces Rule B-01: No legacy code or rule is adopted without explicit prior user presentation and approval.
    """

    def __init__(self, migration_map_path: str = "legacy_reference/MIGRATION_MAP.md"):
        self.migration_map_path = migration_map_path
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.approved_rules: Dict[str, Dict[str, Any]] = {}

    def check_legacy_adoption(self, concept_id: str, details: Dict[str, Any]) -> UserApprovalRequest:
        """Generates an approval request for a legacy concept or rule before adoption."""
        return UserApprovalRequest(concept_id, details)

    def register_legacy_proposal(self, rule_id: str, title: str, description: str, legacy_source: str) -> Dict[str, Any]:
        proposal = {
            "rule_id": rule_id,
            "title": title,
            "description": description,
            "legacy_source": legacy_source,
            "status": "PENDING_USER_APPROVAL",
            "requires_user_prompt": True
        }
        self.pending_approvals[rule_id] = proposal
        return proposal

    def process_user_approval(self, rule_id: str, user_decision: bool, feedback: str = "") -> Dict[str, Any]:
        if rule_id not in self.pending_approvals:
            return {"status": "REJECTED", "reason": f"Rule ID {rule_id} not found in pending proposals."}

        proposal = self.pending_approvals.pop(rule_id)
        if user_decision:
            proposal["status"] = "APPROVED"
            proposal["feedback"] = feedback
            self.approved_rules[rule_id] = proposal
            return proposal
        else:
            proposal["status"] = "REJECTED"
            proposal["feedback"] = feedback
            return proposal

    def is_rule_approved(self, rule_id: str) -> bool:
        return rule_id in self.approved_rules
