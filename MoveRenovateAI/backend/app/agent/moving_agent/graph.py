"""搬家规划 Agent 工作流模块"""
from langgraph.graph import StateGraph, END
from app.agent.state import MovingAgentState
from app.agent.moving_agent.nodes import (
    parse_requirements, generate_items, plan_packing,
    calculate_cost, generate_guide, generate_response
)
import logging

logger = logging.getLogger(__name__)

def create_moving_agent_graph():
    """创建搬家规划 Agent 工作流图"""
    graph = StateGraph(MovingAgentState)
    graph.add_node("parse_requirements", parse_requirements)
    graph.add_node("generate_items", generate_items)
    graph.add_node("plan_packing", plan_packing)
    graph.add_node("calculate_cost", calculate_cost)
    graph.add_node("generate_guide", generate_guide)
    graph.add_node("generate_response", generate_response)
    graph.set_entry_point("parse_requirements")
    graph.add_edge("parse_requirements", "generate_items")
    graph.add_edge("generate_items", "plan_packing")
    graph.add_edge("plan_packing", "calculate_cost")
    graph.add_edge("calculate_cost", "generate_guide")
    graph.add_edge("generate_guide", "generate_response")
    graph.add_edge("generate_response", END)
    return graph.compile()

_moving_agent = None

def get_moving_agent():
    global _moving_agent
    if _moving_agent is None:
        _moving_agent = create_moving_agent_graph()
    return _moving_agent

async def run_moving_agent(user_id: str, user_message: str, context: dict = None) -> dict:
    logger.info(f"🚀 [搬家Agent] 开始处理: {user_message[:50]}...")
    initial_state: MovingAgentState = {
        "user_id": user_id, "user_message": user_message,
        "source_address": None, "target_address": None, "source_rooms": [], "target_rooms": [],
        "moving_date": None, "mover_count": None, "vehicle_type": None, "items": [], "boxes": [],
        "estimated_cost": None, "cost_breakdown": {}, "unpacking_guide": [],
        "response": None, "generated_checklist": None, "suggested_actions": [], "error": None
    }
    if context:
        for key, value in context.items():
            if key in initial_state:
                initial_state[key] = value
    agent = get_moving_agent()
    result = await agent.ainvoke(initial_state)
    logger.info(f"✅ [搬家Agent] 处理完成")
    return {"response": result.get("response"), "intent": "create_moving_plan",
            "generated_checklist": result.get("generated_checklist"),
            "suggested_actions": result.get("suggested_actions", [])}
