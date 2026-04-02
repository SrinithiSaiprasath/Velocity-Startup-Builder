import os
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class MCPRegistry:
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.server_configs = {
            "tavily": {
                "command": "npx",
                "args": ["-y", "@toolsdk.ai/tavily-mcp@latest"],
                "env": {"TAVILY_API_KEY": os.getenv("TAVILY_API_KEY")}
            },
            "reddit": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-reddit"],
                "env": {
                    "REDDIT_CLIENT_ID": os.getenv("REDDIT_CLIENT_ID"),
                    "REDDIT_CLIENT_SECRET": os.getenv("REDDIT_CLIENT_SECRET")
                }
            },
            "figma": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-figma"],
                "env": {
                    "FIGMA_ACCESS_TOKEN": os.getenv("FIGMA_PERSONAL_ACCESS_TOKEN"),
                    "FIGMA_FILE_KEY": os.getenv("FIGMA_FILE_KEY")
                }
            },
            "google_drive": {
                "command": "npx",
                "args": ["-y", "@piotr-agier/google-drive-mcp"],
                "env": {
                    "GOOGLE_DRIVE_OAUTH_CREDENTIALS": "c:/Users/srisai/Startupb/client_secret_261615823958-v312hifp2pj1umfk4p19sh8ll4tc1abp.apps.googleusercontent.com.json"
                }
            },
            "google_sheets": {
                "command": "npx",
                "args": ["-y", "@piotr-agier/google-drive-mcp"],
                "env": {
                    "GOOGLE_DRIVE_OAUTH_CREDENTIALS": "c:/Users/srisai/Startupb/client_secret_261615823958-v312hifp2pj1umfk4p19sh8ll4tc1abp.apps.googleusercontent.com.json"
                }
            },
            "figma_console": {
                "command": "node",
                "args": ["c:/Users/srisai/Startupb/figma-console-mcp/dist/local.js"],
                "env": {
                    "PORT": "3001"
                }
            }
        }

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]):
        config = self.server_configs.get(server_name)
        if not config:
            return {"error": f"No configuration found for MCP server: {server_name}"}
        
        server_params = StdioServerParameters(
            command=config["command"],
            args=config["args"],
            env={**os.environ, **config.get("env", {})}
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result.content[0].text if hasattr(result, 'content') else str(result)

    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """Return the list of available tools for a given MCP server."""
        config = self.server_configs.get(server_name)
        if not config:
            return []
        
        server_params = StdioServerParameters(
            command=config["command"],
            args=config["args"],
            env={**os.environ, **config.get("env", {})}
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_result = await session.list_tools()
                    # tools_result is typically a ListToolsResult object with a 'tools' attribute
                    return [{"name": t.name, "description": t.description} for t in tools_result.tools]
        except Exception as e:
            print(f"Error listing tools for {server_name}: {e}")
            return []

if __name__ == "__main__":
    if len(sys.argv) > 3:
        server, tool, args_str = sys.argv[1], sys.argv[2], sys.argv[3]
        args = json.loads(args_str)
        print(asyncio.run(MCPRegistry().call_tool(server, tool, args)))
