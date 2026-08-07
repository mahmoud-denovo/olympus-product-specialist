"""
Hierarchical Token Usage & Agent Telemetry Tracker.
Tracks token consumption, estimated costs, and agent invocation hierarchies.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class TokenUsage:
    """Represents token usage statistics and cost."""
    prompt_tokens: int = 0
    candidates_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0

    def add(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            candidates_tokens=self.candidates_tokens + other.candidates_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            cost_usd=self.cost_usd + other.cost_usd
        )


@dataclass
class PromptRecord:
    prompt_text: str = ""
    timestamp: str = ""


@dataclass
class ResponseRecord:
    response_text: str = ""
    timestamp: str = ""


@dataclass
class ToolCallRecord:
    tool_name: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = ""


@dataclass
class AgentNode:
    agent_id: str
    agent_name: str
    role: str
    parent_agent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    token_usage: TokenUsage = field(default_factory=TokenUsage)


MODEL_PRICING = {
    "gemini-2.5-flash": {"prompt_per_1m": 0.075, "candidates_per_1m": 0.30},
    "gemini-3.6-flash": {"prompt_per_1m": 0.075, "candidates_per_1m": 0.30},
    "gemini-1.5-pro": {"prompt_per_1m": 1.25, "candidates_per_1m": 5.00}
}


class HierarchicalTokenTracker:
    """
    Hierarchical token spend & response telemetry tracker across agent trees.
    """

    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        self.nodes: Dict[str, AgentNode] = {}
        self._hierarchy_store: Dict[str, Dict[str, Any]] = {}

        # Initialize root agent node
        root_node = AgentNode(
            agent_id="root_specialist",
            agent_name="Root Olympus Specialist",
            role="Primary Orchestrator"
        )
        self.nodes["root_specialist"] = root_node

    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        role: str,
        parent_agent_id: Optional[str] = "root_specialist"
    ) -> AgentNode:
        """Registers a sub-agent in the telemetry hierarchy."""
        node = AgentNode(
            agent_id=agent_id,
            agent_name=agent_name,
            role=role,
            parent_agent_id=parent_agent_id
        )
        self.nodes[agent_id] = node

        if parent_agent_id and parent_agent_id in self.nodes:
            if agent_id not in self.nodes[parent_agent_id].children_ids:
                self.nodes[parent_agent_id].children_ids.append(agent_id)

        return node

    def calculate_cost(
        self,
        model_name: str,
        prompt_tokens: int,
        candidates_tokens: int
    ) -> float:
        """Calculates USD cost based on token counts and model pricing."""
        pricing = MODEL_PRICING.get(model_name, MODEL_PRICING["gemini-2.5-flash"])
        prompt_cost = (prompt_tokens / 1_000_000.0) * pricing["prompt_per_1m"]
        candidates_cost = (candidates_tokens / 1_000_000.0) * pricing["candidates_per_1m"]
        return prompt_cost + candidates_cost

    def record_usage(
        self,
        agent_id: str,
        model_name: str,
        prompt_tokens: int,
        candidates_tokens: int
    ) -> TokenUsage:
        """Records token usage for a specific agent node."""
        cost = self.calculate_cost(model_name, prompt_tokens, candidates_tokens)
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            candidates_tokens=candidates_tokens,
            total_tokens=prompt_tokens + candidates_tokens,
            cost_usd=cost
        )

        if agent_id in self.nodes:
            self.nodes[agent_id].token_usage = self.nodes[agent_id].token_usage.add(usage)

        return usage

    def get_hierarchy_telemetry() -> Dict[str, Any]:
        """Returns structured hierarchy telemetry summary."""
        total_tokens = sum(n.token_usage.total_tokens for n in self.nodes.values())
        total_cost = sum(n.token_usage.cost_usd for n in self.nodes.values())

        return {
            "session_id": self.session_id,
            "total_agents": len(self.nodes),
            "session_token_usage": {
                "prompt_tokens": sum(n.token_usage.prompt_tokens for n in self.nodes.values()),
                "candidates_tokens": sum(n.token_usage.candidates_tokens for n in self.nodes.values()),
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
                for agent_id, node in self.nodes.items()
            }
        }

    def log_invocation(
        self,
        session_id: str,
        agent_role: str,
        parent_agent: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        estimated_cost_usd: float
    ) -> Dict[str, Any]:
        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "agent_role": agent_role,
            "parent_agent": parent_agent,
            "model_name": model_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost_usd": round(estimated_cost_usd, 6)
        }

        if session_id not in self._hierarchy_store:
            self._hierarchy_store[session_id] = {
                "session_id": session_id,
                "total_session_tokens": 0,
                "total_session_cost_usd": 0.0,
                "agent_invocations": []
            }

        self._hierarchy_store[session_id]["agent_invocations"].append(record)
        self._hierarchy_store[session_id]["total_session_tokens"] += record["total_tokens"]
        self._hierarchy_store[session_id]["total_session_cost_usd"] = round(
            self._hierarchy_store[session_id]["total_session_cost_usd"] + estimated_cost_usd, 6
        )

        return self._hierarchy_store[session_id]

    def get_session_telemetry(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._hierarchy_store.get(session_id)


tracker = HierarchicalTokenTracker()
