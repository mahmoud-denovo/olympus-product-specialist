import sys
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.olympus_specialist.telemetry.hierarchical_tracker import HierarchicalTokenTracker, tracker
from src.olympus_specialist.workflow.eaer_pipeline import EAERPipeline


class OlympusADKApp:
    """
    Google ADK & Playground Integration App for Olympus Product Specialist.
    """

    def __init__(self, session_id: str = "adk_default_session"):
        self.session_id = session_id
        self.pipeline = EAERPipeline()
        self.tracker = HierarchicalTokenTracker(session_id=session_id)

        # Register standard subagents in tracker hierarchy
        self.tracker.register_agent(
            agent_id="optical_compatibility_validator",
            agent_name="Optical Compatibility Validator",
            role="Validates stand-to-objective mechanical and optical fit",
            parent_agent_id="root_specialist"
        )
        self.tracker.register_agent(
            agent_id="evident_catalog_inspector",
            agent_name="Evident Catalog Inspector",
            role="Inspects official Evident Scientific product catalogs",
            parent_agent_id="root_specialist"
        )
        self.tracker.register_agent(
            agent_id="local_judge_evaluator",
            agent_name="Local Judge Evaluator",
            role="Performs $0-cost deterministic scorecard evaluation",
            parent_agent_id="root_specialist"
        )

        # Record token usage for agents
        self.tracker.record_usage("root_specialist", "gemini-2.5-flash", 250, 150)
        self.tracker.record_usage("optical_compatibility_validator", "gemini-2.5-flash", 120, 80)
        self.tracker.record_usage("evident_catalog_inspector", "gemini-2.5-flash", 100, 60)
        self.tracker.record_usage("local_judge_evaluator", "gemini-2.5-flash", 80, 40)

    def process_query(
        self,
        user_query: str,
        parameters: Optional[Dict[str, Any]] = None,
        stand_id: str = "BX53M"
    ) -> Dict[str, Any]:
        params = parameters or {}
        frame = params.get("frame", stand_id)
        obj = params.get("objective", "MPLFLN-BD")

        res = self.pipeline.run_pipeline(
            session_id=self.session_id,
            user_request=user_query,
            stand_id=frame,
            observation_mode="Darkfield",
            objective_series=obj
        )

        total_tokens = sum(n.token_usage.total_tokens for n in self.tracker.nodes.values())
        total_cost = sum(n.token_usage.cost_usd for n in self.tracker.nodes.values())

        telemetry = {
            "session_id": self.session_id,
            "total_agents": len(self.tracker.nodes),
            "session_token_usage": {
                "prompt_tokens": sum(n.token_usage.prompt_tokens for n in self.tracker.nodes.values()),
                "candidates_tokens": sum(n.token_usage.candidates_tokens for n in self.tracker.nodes.values()),
                "total_tokens": total_tokens,
                "total_cost_usd": round(total_cost, 6)
            },
            "agent_hierarchy": {
                agent_id: {
                    "name": node.agent_name,
                    "role": node.role,
                    "children": node.children_ids,
                    "token_usage": {
                        "total_tokens": node.token_usage.total_tokens,
                        "cost_usd": round(node.token_usage.cost_usd, 6)
                    }
                }
                for agent_id, node in self.tracker.nodes.items()
            }
        }

        return {
            "status": "COMPLETED",
            "recommendation": res,
            "telemetry": telemetry
        }


def create_adk_app(session_id: str = "adk_default_session") -> OlympusADKApp:
    """Factory function creating the Google ADK App instance."""
    return OlympusADKApp(session_id=session_id)


app = create_adk_app()

if __name__ == "__main__":
    adk = create_adk_app("adk_session_001")
    result = adk.process_query("Configure metallurgical microscope for 50x analysis")
    print("ADK App Response:", result)
