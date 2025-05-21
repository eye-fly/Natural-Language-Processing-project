import asyncio
from typing import Optional
from contextlib import AsyncExitStack, aclosing

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

# from anthropic import Anthropic
import argparse


class BombClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self._streams_context = None
        self._session_context = None
 

    async def connect_to_server(self, server_url: str):
        """Connect to an sse MCP server"""
        self.exit_stack = AsyncExitStack()

        self._streams_context = await self.exit_stack.enter_async_context(sse_client(url=server_url))

        self._session_context = ClientSession(*self._streams_context)
        self.session = await self.exit_stack.enter_async_context(self._session_context)

        await self.session.initialize()

        print("Initialized SSE client...")
        print("Listing tools...")
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, tool_name: str, tool_args: dict[str, str]) -> str:
        result = await self.session.call_tool(tool_name, arguments=tool_args)
        return result.content[0].text if result.content else ""

    async def cleanup(self):
        try:
            await self.exit_stack.aclose()
        except asyncio.CancelledError:
            print("[Client] Cancelled during cleanup — safe to ignore.")
        print("[Client] Session closed")


class Defuser(BombClient):
    async def run(self, action: str) -> str:
        response = await self.process_query("game_interaction", {"command": action})
        # print(f"[Defuser] Server Response:\n{response}")
        return response


class Expert(BombClient):
    async def run(self) -> str:
        response = await self.process_query("get_manual", {})
        # print(f"[Expert] Manual:\n{response}")
        return response


async def main():
    """ Main function to connect to the server, run unit tests and run the choosen client"""
    parser = argparse.ArgumentParser(description="Bomb Defusal Client")
    parser.add_argument("--url", type=str, required=True, help="Server URL (e.g., http://localhost:8080)")
    parser.add_argument("--role", type=str, required=True, choices=["Defuser", "Expert"], help="Role to play")

    args = parser.parse_args()
    
    #tests: 
    client = Defuser()
    await client.connect_to_server(args.url)
    await defuser_test(client)
    await client.cleanup()
    client = Expert()
    await client.connect_to_server(args.url)
    await expert_test(client)
    await client.cleanup()

    if args.role == "Defuser":
        client = Defuser()
    else:
        client = Expert()

    await client.connect_to_server(args.url)

    try:
        if args.role == "Defuser":
            while True:
                action = input("[Defuser] Enter action (or 'help' or 'state'): ").strip()
                if not action:
                    continue
                resp =await client.run(action)
                print(resp)
        else:
            while True:
                cmd = input("[Expert] Press Enter to fetch manual or type 'exit' to quit: ").strip()
                if cmd.lower() == "exit":
                    break
                resp = await client.run()
                print(resp)
    except KeyboardInterrupt:
        print("\n[Client] Interrupted")
    finally:
        await client.cleanup()

async def expert_test(expert_client: Expert):
    """Test the Expert class"""
    result = await expert_client.run()

    possible_outputs = ["BOOM!", "BOMB SUCCESSFULLY DISARMED!", "Regular Wires Module", "The Button Module",
                        "Memory Module", "Simon Says Module"]

    assert any(result.find(output) != -1 for output in possible_outputs), f"Expert test failed"


async def defuser_test(defuser_client: Defuser):
    """Test the Defuser class"""
    result = await defuser_client.run("state")
    
    # print('defuser_test',result)
    possible_outputs = ["BOMB STATE"]

    assert any(result.find(output) != -1 for output in possible_outputs), f"Defuser test failed"
    # print('defuser_test=',any(result.find(output) != -1 for output in possible_outputs), f"Defuser test failed")

if __name__ == "__main__":
    asyncio.run(main())
