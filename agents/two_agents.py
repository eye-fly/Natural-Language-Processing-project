import asyncio

from agents.prompts import expert_prompt, defuser_prompt
from game_mcp.game_client import Defuser, Expert
from agents.models import HFModel, SmollLLM, Cohere


async def run_two_agents(
        defuser_model: HFModel,
        server_url: str = "http://0.0.0.0:8080",
        max_new_tokens: int = 85
) -> None:
    """
    Main coroutine that orchestrates two LLM agents (Defuser and Expert)
    interacting with the bomb-defusal server.

    :param defuser_model: The HFModel for the Defuser's role.
    :param expert_model: The HFModel for the Expert's role.
    :param server_url: The URL where the bomb-defusal server is running.
    :param max_new_tokens: Max tokens to generate for each LLM response.
    """
    defuser_client = Defuser()
    expert_client = Expert()

    try:
        # 1) Connect both clients to the same server
        await defuser_client.connect_to_server(server_url)
        await expert_client.connect_to_server(server_url)
        
        i = 0
        while True:
            if i > 5:
                break
            i += 1

            # Get bomb state
            bomb_state = await defuser_client.run("state")
            print("[DEFUSER sees BOMB STATE]:")
            print(bomb_state)

            if "Bomb disarmed!" in bomb_state or "Bomb exploded!" in bomb_state:
                break

            # Get manual
            manual_text = await expert_client.run()
            print("[EXPERT sees MANUAL]:")
            print(manual_text)

            # Create prompt: manual + bomb state → expected output: action
            messages = defuser_prompt(bomb_state,manual_text)

            # Generate final action from expert_model
            raw_response = defuser_model.generate_response(
                messages,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                do_sample=True
            )

            print("\n[MODEL RESPONSE]:")
            print(raw_response)

            # Extract action from the model's response
            action = "help"
            for line in raw_response.splitlines():
                line = line.strip().lower()
                if line.startswith(("cut", "press", "hold", "release", "help", "state")):
                    action = line.strip()
                    break

            print("\n[ACTION DECIDED]:", action)

            # Execute action
            result = await defuser_client.run(action)
            print("[SERVER RESPONSE]:")
            print(result)
            print("-" * 60)

            if "BOMB SUCCESSFULLY DISARMED" in result or "BOMB HAS EXPLODED" in result:
                break
    finally:
        try:
            await defuser_client.cleanup()
            await expert_client.cleanup()
        except asyncio.CancelledError:
            print("[run_single_agent] Cancelled during cleanup — safe to ignore.")


if __name__ == "__main__":

    defuser_checkpoint = "HuggingFaceTB/SmolLM-135M-Instruct"
    # expert_checkpoint = "Qwen/Qwen2.5-1.5B"

    # defuser_model = SmollLLM(defuser_checkpoint, device="cpu")
    expert_model = Cohere()
    asyncio.run(
        run_two_agents(
            defuser_model=expert_model,
            server_url="http://0.0.0.0:8080",
            max_new_tokens=50
        )
    )
