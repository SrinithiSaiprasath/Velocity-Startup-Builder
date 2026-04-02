import os
import sys
import asyncio
import json
from tavily import TavilyClient
from dotenv import load_dotenv

# Google API Imports
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    HAS_GOOGLE_SDK = True
except ImportError:
    HAS_GOOGLE_SDK = False

# Use local bridge if available, otherwise direct SDK
try:
    from registry import MCPRegistry
    HAS_REGISTRY = True
except ImportError:
    HAS_REGISTRY = False

load_dotenv()

class AgentBridge:
    """Unified bridge for all startup agents to access research, social, finance, and design tools."""
    
    def __init__(self):
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.registry = MCPRegistry() if HAS_REGISTRY else None
        self.agents_dir = os.path.join(os.path.dirname(__file__), "agents")

    def get_agent_prompt(self, agent_name: str) -> str:
        """Reads the system prompt from the agent's folder."""
        path = os.path.join(self.agents_dir, agent_name, "prompts.txt")
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read()
        return f"Standard {agent_name} persona."

    async def upload_google_drive(self, folder_name: str, file_name: str, content: str):
        """Marketer: Store marketing assets/captions in Google Drive instead of scheduling."""
        print(f"--- BRIDGE: Uploading to Google Drive '{file_name}' ---")
        if HAS_REGISTRY:
            try:
                # Updated to use @piotr-agier/google-drive-mcp tool names
                # First, ensure the folder exists or just create the file in root if not specified
                return await self.registry.call_tool("google_drive", "createTextFile", {
                    "name": file_name,
                    "content": content
                })
            except Exception as e:
                print(f"⚠️  [MCP] Google Drive Upload Failed: {e}")
                return {"error": f"Google Drive upload failed: {e}"}
        return {"error": "Registry required for Google Drive."}

    async def run_orchestration(self, user_input: str):
        """
        Orchestrator: Analyzes user input using the Orchestrator Persona 
        and determines if it needs a specific agent, specific phase, or full workflow.
        """
        orchestrator_persona = self.get_agent_prompt("orchestrator")
        print(f"\n--- ORCHESTRATOR LOGIN: System Prompt Loaded ---")
        prompt_lower = user_input.lower()
        
        # 1. Routing Logic driven by Orchestrator Persona
        if any(word in prompt_lower for word in ["figma", "design", "ui", "wireframe"]):
            persona = self.get_agent_prompt("designer")
            print(f"-> Routing to DESIGNER Agent\nPersona: {persona[:50]}...")
            return await self.design_figma("User_Requested_Component", user_input)
            
        elif any(word in prompt_lower for word in ["market", "research", "trends", "ba", "strategy"]):
            persona = self.get_agent_prompt("business_analyst")
            print(f"-> Routing to BA Agent\nPersona: {persona[:50]}...")
            return await self.research(user_input)
            
        elif any(word in prompt_lower for word in ["finance", "investor", "money", "sheet", "projection"]):
            persona = self.get_agent_prompt("investor")
            print(f"-> Routing to INVESTOR Agent\nPersona: {persona[:50]}...")
            return await self.build_sheet("Financial_Model", [{"input": user_input}])

        elif any(word in prompt_lower for word in ["marketing", "social", "post", "brand", "growth"]):
            persona = self.get_agent_prompt("marketer")
            print(f"-> Routing to MARKETER Agent\nPersona: {persona[:50]}...")
            # Route to Google Drive storage instead of Metricool scheduling
            return await self.upload_google_drive(
                folder_name="Marketing_Assets",
                file_name=f"SocialPost_{json.dumps(user_input)[:10]}.txt",
                content=user_input
            )
        
        elif any(word in prompt_lower for word in ["product", "feature", "requirements", "po", "priority"]):
            persona = self.get_agent_prompt("po")
            print(f"-> Routing to PRODUCT OWNER Agent\nPersona: {persona[:50]}...")
            # PO-specific tool call logic would go here
            return {"status": "PO Task Acknowledged", "context": persona[:50]}

        # 2. Routing Logic for the Full LangGraph Workflow (main.py)
        else:
            print(f"-> No specific task found. Orchestrator initiating FULL WORKFLOW via main.py...")
            return {"status": "Full Workflow Initialized", "prompt": user_input}

    async def research(self, query: str, depth="advanced"):
        """Archeologist & BA: Market research and trend discovery."""
        print(f"--- BRIDGE: Researching '{query}' ---")
        
        # 1. Prioritize Registry/MCP for Unified Tooling
        if HAS_REGISTRY:
            try:
                print("✅ [MCP] Calling Tavily via Registry...")
                # Updated tool name to 'tavily-search' for @toolsdk.ai/tavily-mcp
                return await self.registry.call_tool("tavily", "tavily-search", {"query": query})
            except Exception as e:
                print(f"⚠️  [MCP] Failed: {e}. Falling back to Direct SDK...")

        # 2. Fallback to Direct Python SDK if Registry fails
        if self.tavily_key:
            try:
                from tavily import TavilyClient
                client = TavilyClient(api_key=self.tavily_key)
                # Run in thread to not block async loop if needed, but SDK is fast
                result = client.search(query=query, search_depth=depth)
                print("✅ [TAVILY SDK] Research successful.")
                return result
            except Exception as e:
                print(f"⚠️  [TAVILY SDK] Failed: {e}.")
            
        return {"error": "No Tavily API key or Registry found."}

    async def social_post(self, platform: str, content: str):
        """Marketer: Post to social media via Metricool."""
        print(f"--- BRIDGE: Posting to {platform} ---")
        if HAS_REGISTRY:
            return await self.registry.call_tool("metricool", "post", {"platform": platform, "content": content})
        return {"error": "Registry required for Metricool."}

    async def build_sheet(self, title: str, rows: list):
        """Investor & BA: Create financial models in Google Sheets."""
        print(f"--- BRIDGE: Creating Sheet '{title}' ---")
        
        # 1. Prioritize Registry/MCP for Unified Tooling
        if HAS_REGISTRY:
            try:
                print("✅ [MCP] Calling Google Sheets via Registry...")
                # Try create_spreadsheet (Standard MCP) or createGoogleSheet (@piotr-agier)
                try:
                    return await self.registry.call_tool("google_sheets", "create_spreadsheet", {"title": title, "data": rows})
                except:
                    return await self.registry.call_tool("google_sheets", "createGoogleSheet", {"title": title, "rows": rows})
            except Exception as e:
                print(f"⚠️  [MCP] Google Sheets Creation Failed: {e}. Falling back to Direct SDK...")

        # 2. Fallback to Direct Google SDK (Bypasses npx/MCP connectivity issues)
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if HAS_GOOGLE_SDK and creds_path and os.path.exists(creds_path):
            try:
                from google_auth_oauthlib.flow import InstalledAppFlow
                from google.auth.transport.requests import Request
                import pickle
                
                scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
                creds = None
                token_path = 'token.pickle'
                
                if os.path.exists(token_path):
                    with open(token_path, 'rb') as token:
                        creds = pickle.load(token)
                
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
                        creds = flow.run_local_server(port=0)
                    with open(token_path, 'wb') as token:
                        pickle.dump(creds, token)
                
                service = build('sheets', 'v4', credentials=creds)
                
                # Create the spreadsheet
                spreadsheet = {'properties': {'title': title}}
                spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
                spreadsheet_id = spreadsheet.get('spreadsheetId')
                
                # Update the sheet with data (simple rows implementation)
                values = []
                for row in rows:
                    if isinstance(row, dict):
                        values.append(list(row.values()))
                    elif isinstance(row, list):
                        values.append(row)
                    else:
                        values.append([str(row)])
                
                if values:
                    body = {'values': values}
                    service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id, range="Sheet1!A1",
                        valueInputOption="USER_ENTERED", body=body).execute()
                
                print(f"✅ [GOOGLE SDK] Spreadsheet created: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
                return {"spreadsheetId": spreadsheet_id, "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"}
            except Exception as e:
                print(f"⚠️ [GOOGLE SDK] Failed: {e}.")

        return {"error": "Registry required for Google Sheets."}

    async def design_figma(self, component: str, description: str):
        """Designer: Push wireframe descriptions to Figma."""
        file_key = os.getenv("FIGMA_FILE_KEY", "DEFAULT_BOARD_KEY")
        pat = os.getenv("FIGMA_PERSONAL_ACCESS_TOKEN")
        
        print(f"--- BRIDGE: Pushing to Figma File '{file_key}' | Component: '{component}' ---")
        
        # 1. Prioritize Registry/MCP for Unified Tooling
        if HAS_REGISTRY:
            try:
                print("✅ [MCP] Calling Figma via Registry...")
                # Try create_component first (often a custom MCP tool for this repo)
                return await self.registry.call_tool("figma", "create_component", {
                    "fileKey": file_key,
                    "name": component, 
                    "description": description
                })
            except Exception as e:
                print(f"⚠️  [MCP] Failed: {e}. Falling back to Direct REST API...")

        # 2. Fallback to Direct REST API only if Registry fails
        if pat and file_key:
            try:
                import requests
                # Creating a comment as a 'design request' or placeholder for agentic designs
                url = f"https://api.figma.com/v1/files/{file_key}/comments"
                headers = {"X-Figma-Token": pat}
                payload = {"message": f"AGENT DESIGN REQUEST\nComponent: {component}\nDescription: {description}"}
                response = requests.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    print(f"✅ [FIGMA REST] Design Request pushed successfully.")
                    return response.json()
                else:
                    print(f"⚠️ [FIGMA REST] API error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"⚠️ [FIGMA REST] Failed: {e}.")

        return {"error": "Registry required for Figma."}

# CLI Interface
async def main():
    bridge = AgentBridge()

    if len(sys.argv) > 1:
        # Use terminal arguments if provided
        user_input = " ".join(sys.argv[1:])
        print(f"--- RUNNING COMMAND: {user_input} ---")
        res = await bridge.run_orchestration(user_input)
        print(json.dumps(res, indent=2))
        return

    # Interactive Terminal Experience
    print("\n" + "="*50)
    print("🚀 STARTUP BUILDER OS: ORCHESTRATOR ACTIVE")
    print("="*50)
    print("What would you like to build today?")
    print("Examples: 'build a figma template', 'research rural fintech', 'money flow', 'marketing social posts'")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("USER > ")
        if user_input.lower() in ["exit", "quit"]:
            print("Shutting down Startup Builder system. See you at IPO!")
            break
        
        res = await bridge.run_orchestration(user_input)
        # Displaying the "Persona" used and the action taken
        print(f"\n[SYSTEM RESPONSE] -> {res}")
        print("-"*50)

if __name__ == "__main__":
    asyncio.run(main())
