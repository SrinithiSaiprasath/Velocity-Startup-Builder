from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from state import StartupState
from agent_bridge import AgentBridge
import asyncio

# Initialize Agent Bridge
bridge = AgentBridge()

def market_archeologist_node(state: StartupState) -> StartupState:
    print("--- MARKET ARCHEOLOGIST NODE ---")
    state["current_step"] = "market_archeologist"
    
    # Logic: Call Tavily/Reddit/YT MCPs via Bridge
    research_query = f"market trends and pain points for {state['user_prompt']}"
    res = asyncio.run(bridge.research(research_query))
    
    state["logs"].append(f"Researching market trends for: {state['user_prompt']}")
    if isinstance(res, dict) and "error" not in res:
        state["need_trend_matrix"] = str(res)
    
    return state

def visionary_architect_node(state: StartupState) -> StartupState:
    print("--- VISIONARY ARCHITECT NODE ---")
    state["current_step"] = "visionary_architect"
    # Logic: Map vision and core audience
    state["logs"].append("Distilling vision and target audience profiling...")
    return state

def business_analyst_node(state: StartupState) -> StartupState:
    print("--- BUSINESS ANALYST NODE ---")
    state["current_step"] = "business_analyst"
    # Logic: Market sizing & Risk analysis
    state["logs"].append("Analyzing business strategy and market sizing...")
    return state

def investor_agent_node(state: StartupState) -> StartupState:
    print("--- INVESTOR AGENT NODE ---")
    state["current_step"] = "investor_agent"
    
    # Logic: Financial modeling (Google Sheets) via Bridge
    title = f"Financial Model - {state['user_prompt'][:20]}"
    rows = [{"Category": "Revenue", "Year 1": 100000}, {"Category": "Expenses", "Year 1": 80000}]
    res = asyncio.run(bridge.build_sheet(title, rows))
    
    state["logs"].append(f"Generating financial models and Google Sheets... Result: {res.get('url') if isinstance(res, dict) else 'Check Sheets'}")
    state["financial_model"] = str(res)
    
    return state

def product_owner_node(state: StartupState) -> StartupState:
    print("--- PRODUCT OWNER NODE ---")
    state["current_step"] = "product_owner"
    # Logic: Technical flowcharts & Feature mapping
    state["logs"].append("Mapping technical features and flowcharts...")
    return state

def ui_ux_designer_node(state: StartupState) -> StartupState:
    print("--- UI/UX DESIGNER NODE ---")
    state["current_step"] = "ui_ux_designer"
    
    # Logic: Figma UI creation via Bridge
    comp_name = "LandingPage_Wireframe"
    desc = f"A modern design for {state['user_prompt']}"
    res = asyncio.run(bridge.design_figma(comp_name, desc))
    
    state["logs"].append(f"Creating high-fidelity UI mocks in Figma... Result: {res}")
    state["figma_url"] = str(res)
    
    return state

def growth_hacker_node(state: StartupState) -> StartupState:
    print("--- GROWTH HACKER (MARKETER) NODE ---")
    state["current_step"] = "growth_hacker"
    
    # Logic: Generate Social Content Bundle
    # In a real run, this would be an LLM call using the 'marketer' persona.
    content_bundle = f"""
    -- SOCIAL MEDIA STRATEGY: {state['user_prompt']} --
    
    Platform: LinkedIn
    Post: "We are excited to unveil our new vision for {state['user_prompt']}! Join us in changing the world."
    
    Platform: Twitter/X
    Post: "Say hello to the future of {state['user_prompt']}. 🚀 #Startup #Innovation"
    
    Platform: Instagram
    Caption: "Sustainability meets technology. {state['user_prompt']} is here. 🌿"
    """
    
    file_name = f"Social_Media_Bundle_{state['user_prompt'][:15].replace(' ', '_')}.txt"
    
    # Save to Google Drive via Bridge
    res = asyncio.run(bridge.upload_google_drive(
        folder_name="Marketing_Assets",
        file_name=file_name,
        content=content_bundle
    ))
    
    if isinstance(res, dict) and "error" in res:
        state["errors"].append(f"Marketer failed to upload to Drive: {res['error']}")
        state["logs"].append(f"Growth Hacker: Social bundle generated but GDrive upload failed.")
    else:
        state["logs"].append(f"Growth Hacker: Generated social bundle and saved to Google Drive: {file_name}")
    
    state["social_bundles"] = content_bundle
    return state

# GRAPH DEFINITION
workflow = StateGraph(StartupState)

# Add Nodes
workflow.add_node("archeologist", market_archeologist_node)
workflow.add_node("architect", visionary_architect_node)
workflow.add_node("ba", business_analyst_node)
workflow.add_node("investor", investor_agent_node)
workflow.add_node("po", product_owner_node)
workflow.add_node("designer", ui_ux_designer_node)
workflow.add_node("marketer", growth_hacker_node)

# Add Edges (Linear Flow for Phase 1 base skeleton)
workflow.set_entry_point("archeologist")
workflow.add_edge("archeologist", "architect")
# Add a flag/interrupt point here for HIL 1
workflow.add_edge("architect", "ba")
workflow.add_edge("ba", "investor")
# Add a flag/interrupt point here for HIL 2
workflow.add_edge("investor", "po")
workflow.add_edge("po", "designer")
workflow.add_edge("designer", "marketer")
workflow.add_edge("marketer", END)

# Compile
app = workflow.compile()

if __name__ == "__main__":
    # Test execution
    initial_state: StartupState = {
        "user_prompt": "AI for community-driven sustainable farming",
        "need_trend_matrix": None,
        "core_essence": None,
        "business_model": None,
        "financial_model": None,
        "feature_maps": None,
        "figma_url": None,
        "social_bundles": None,
        "metricool_status": None,
        "logs": [],
        "errors": [],
        "current_step": "START"
    }
    
    # Run through the flow
    final_output = app.invoke(initial_state)
    print("\n--- FINAL LOGS ---")
    for log in final_output["logs"]:
        print(f"Log: {log}")
