import asyncio
import os
import json
from contextlib import AsyncExitStack
from typing import Any

from google import genai
from google.genai import types
from client import MCPClient
from dotenv import load_dotenv
import ssl
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()

class ChatHost:
    def __init__(self):
        self.mcp_clients: list[MCPClient] = [
            MCPClient("./weather_USA.py"),
            MCPClient("./weather_Israel.py"),
        ]
        self.tool_clients: dict[str, tuple[MCPClient, str]] = {}
        self.clients_connected = False
        self.exit_stack = AsyncExitStack()
        
        # הגדרת מפתח ה-API של Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
            
        self.client = genai.Client(api_key=api_key)
        
        # אתחול המודל עם תמיכה בכלים (יוגדר סופית בתוך process_query)
        self.model_name = "gemini-2.0-flash"# מודל מהיר וחינמי יחסית

    async def connect_mcp_clients(self):
        if self.clients_connected: return
        for client in self.mcp_clients:
            if client.session is None:
                await client.connect_to_server()
        self.clients_connected = True

    async def get_available_tools(self):
        """המרת כלי ה-MCP לפורמט ש-Gemini מבין"""
        await self.connect_mcp_clients()
        self.tool_clients = {}
        gemini_tools = []

        for client in self.mcp_clients:
            if client.session is None: continue
            try:
                response = await client.session.list_tools()
                for tool in response.tools:
                    exposed_name = f"{client.client_name}__{tool.name}"
                    self.tool_clients[exposed_name] = (client, tool.name)
                    
                    # בניית הגדרת הכלי עבור Gemini
                    gemini_tools.append({
                        "name": exposed_name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    })
            except Exception as e:
                print(f"Warning: Tool fetch error: {e}")
        
        return gemini_tools

    async def process_query(self, query: str) -> str:
        tools_list = await self.get_available_tools()

        # המרת כלי MCP לפורמט של Gemini החדש
        gemini_tools = []
        for t in tools_list:
            params = t.get("parameters", t.get("input_schema", {}))
            params.pop("title", None)
            for prop in params.get("properties", {}).values():
                prop.pop("title", None)
            gemini_tools.append(types.Tool(
                function_declarations=[types.FunctionDeclaration(
                    name=t["name"],
                    description=t["description"],
                    parameters=params
                )]
            ))

        contents = [types.Content(role="user",
                    parts=[types.Part(text=query)])]
        final_text = []

        while True:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(tools=gemini_tools)
            )

            candidate = response.candidates[0]
            contents.append(types.Content(
                role="model",
                parts=candidate.content.parts
            ))

            tool_calls = [p for p in candidate.content.parts
                        if hasattr(p, "function_call") and p.function_call]

            if not tool_calls:
                for p in candidate.content.parts:
                    if hasattr(p, "text") and p.text:
                        final_text.append(p.text)
                break

            tool_results = []
            for p in tool_calls:
                fn = p.function_call
                tool_name = fn.name
                args = dict(fn.args)
                print(f"[*] Calling: {tool_name}")
                client, original = self.tool_clients[tool_name]
                result = await client.session.call_tool(original, args)
                result_text = " ".join(
                    r.text for r in result.content
                    if hasattr(r, "text")
                )
                tool_results.append(types.Part.from_function_response(
                    name=tool_name,
                    response={"result": result_text}
                ))

            contents.append(types.Content(role="tool", parts=tool_results))

        return "\n".join(final_text)

    async def chat_loop(self):
        print("\nMCP Host with Gemini Started!")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit': break
                if not query: continue
                
                response = await self.process_query(query)
                print(f"\nAssistant: {response}")
            except Exception as e:
                print(f"\nError: {e}")

    async def cleanup(self):
        for client in reversed(self.mcp_clients):
            await client.cleanup()

async def main():
    host = ChatHost()
    try:
        await host.chat_loop()
    finally:
        await host.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

    