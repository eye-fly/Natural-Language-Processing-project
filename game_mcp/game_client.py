import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

# from anthropic import Anthropic
from dotenv import load_dotenv
import argparse


# Feel free to import any libraries you need - if needed change requirements.txt


class BombClient:
    def __init__(self):
        # YOUR CODE STARTS HERE
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        # self.anthropic = Anthropic()
        # YOUR CODE ENDS HERE

    async def connect_to_server(self, server_url: str):
        """Connect to an sse MCP server"""
        # YOUR CODE STARTS HERE
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        # Initialize
        await self.session.initialize()

        # List available tools to verify connection
        print("Initialized SSE client...")
        print("Listing tools...")
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
        # YOUR CODE ENDS HERE

    async def process_query(self, tool_name: str, tool_args: dict[str, str]) -> str:
        """Process a query using the game_interaction tool"""
        # YOUR CODE STARTS HERE
        result = await self.session.call_tool(tool_name, arguments=tool_args)
        return result.content[0].text if result.content else ""
        # YOUR CODE ENDS HERE

    async def cleanup(self):
        """Properly clean up the session and streams"""
        # YOUR CODE STARTS HERE
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)
        print("[Client] Session closed")
        # YOUR CODE ENDS HERE


class Defuser(BombClient):
    async def run(self, action: str) -> str:
        """Run a defuser action"""
        # YOUR CODE STARTS HERE
        response = await self.process_query("game_interaction", {"command": action})
        print(f"[Defuser] Server Response:\n{response}")
        return response
        # YOUR CODE ENDS HERE


class Expert(BombClient):
    async def run(self) -> str:
        """Run an expert action"""
        # YOUR CODE STARTS HERE
        response = await self.process_query("get_manual", {})
        print(f"[Expert] Manual:\n{response}")
        return response
        # YOUR CODE ENDS HERE


async def main():
    """ Main function to connect to the server and run the clients """
    # YOUR CODE STARTS HERE
    parser = argparse.ArgumentParser(description="Bomb Defusal Client")
    parser.add_argument("--url", type=str, required=True, help="Server URL (e.g., http://localhost:8080)")
    parser.add_argument("--role", type=str, required=True, choices=["Defuser", "Expert"], help="Role to play")

    args = parser.parse_args()
    
    # #test:
    # client = Defuser()
    # await client.connect_to_server(args.url)
    # await defuser_test(client)
    # await client.cleanup()
    # client = Expert()
    # await client.connect_to_server(args.url)
    # await expert_test(client)
    # await client.cleanup()

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
                await client.run(action)
        else:
            while True:
                cmd = input("[Expert] Press Enter to fetch manual or type 'exit' to quit: ").strip()
                if cmd.lower() == "exit":
                    break
                await client.run()
    except KeyboardInterrupt:
        print("\n[Client] Interrupted")
    finally:
        await client.cleanup()
    # YOUR CODE ENDS HERE


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
