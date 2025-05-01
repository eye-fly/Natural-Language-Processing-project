import asyncio

from agents.prompts import expert_prompt, defuser_prompt
from game_mcp.game_client import Defuser, Expert
from agents.models import HFModel, SmollLLM, Cohere
from datetime import datetime
import os
import logging
from httpx import HTTPStatusError, Response

# Create logs/results directory
os.makedirs("results", exist_ok=True)

# Setup logging
logging.basicConfig(
    filename="run_log.txt",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

async def generate_with_backoff(model, messages, **gen_args) -> str:
    """Retry model call with exponential backoff on 429 errors."""
    max_retries = 5
    delay = 61
    for attempt in range(max_retries):
        try:
            return model.generate_response(messages, **gen_args)
        except HTTPStatusError as e:
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("retry-after", delay))
                print(f"[429] Rate limit hit. Retrying after {retry_after} seconds.")
                await asyncio.sleep(retry_after)
            else:
                raise
        except Exception as e:
            if "429" in str(e):
                print(f"[429 fallback] {e}. Waiting {delay}s.")
                await asyncio.sleep(delay)
            else:
                raise
    raise RuntimeError("Too many retries due to rate limits.")


async def run_single_agent(
    expert_model: HFModel,
    server_url: str = "http://0.0.0.0:8080",
    max_new_tokens: int = 100,
    temperature: float = 0.4,
    top_p: float = 0.9,
    top_k: int = 50,
) -> None:
    defuser_client = Defuser()
    expert_client = Expert()

    temperatures = [0.1, 0.7, 0.92]
    temperatures = [temperature]
    top_ps = [0.8, 0.9, 1.0]
    top_ps = [top_p]

    top_ks = [20, 50, 100]
    # top_ks = [top_k]

    try:
        await defuser_client.connect_to_server(server_url)
        await expert_client.connect_to_server(server_url)

        for temp in temperatures:
            for top_p in top_ps:
                for top_k in top_ks:
                    # Initialize stats for this config
                    bombs_disarmed = 0
                    bombs_exploded = 0
                    correct_actions = 0
                    incorrect_actions = 0

                    print(f"\n Running config: temp={temp}, top_p={top_p}, top_k={top_k}")
                    logging.info(f"\n Running config: temp={temp}, top_p={top_p}, top_k={top_k}")
                    logging.info('='*100)
                    # Start bomb defusal loop
                    i =0
                    while True:
                        i +=1
                        if i >10:
                            break
                        bomb_state = await defuser_client.run("state")
                        # logging.info("[BOMB STATE]\n" + bomb_state)

                        manual_text = await expert_client.run()
                        # logging.info("[MANUAL TEXT]\n" + manual_text)

                        messages = defuser_prompt(bomb_state,manual_text)
                        raw_response = await generate_with_backoff(
                                expert_model,
                                messages,
                                max_new_tokens=max_new_tokens,
                                temperature=temp,
                                top_p=top_p,
                                top_k=top_k,
                                do_sample=True
                            )
                        logging.info("[MODEL RESPONSE]\n" + raw_response)

                        action = "help"
                        for line in raw_response.splitlines():
                            line = line.strip().lower()
                            if line.startswith(("cut", "press", "hold", "release", "help", "state")):
                                action = line.strip()
                                break

                        if action == "help":
                            incorrect_actions += 1

                        logging.info(f"[ACTION DECIDED] {action}")

                        result = await defuser_client.run(action)
                        logging.info("[SERVER RESPONSE]\n" + result)

                        if "BOMB SUCCESSFULLY DISARMED" in result:
                            bombs_disarmed += 1
                            correct_actions += 1
                            print("Bomb Disarmed")
                            await defuser_client.run("restart")

                        elif "BOOM! THE BOMB HAS EXPLODED" in result:
                            bombs_exploded += 1
                            print("Bomb Exploded")
                            await defuser_client.run("restart")
                        elif action != "help":
                            correct_actions += 1

                    # === SAVE RESULTS ===
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    model_name = expert_model.__class__.__name__
                    result_path = f"results/{model_name}_runlog.csv"

                    result_line = (
                        f"{timestamp},{model_name},{max_new_tokens},{temp},{top_p},{top_k},"
                        f"{bombs_disarmed},{bombs_exploded},{correct_actions},{incorrect_actions}\n"
                    )
                    if not os.path.exists(result_path):
                        header = (
                            "timestamp,model,max_tokens,temperature,top_p,top_k,"
                            "bombs_disarmed,bombs_exploded,correct_actions,incorrect_actions\n"
                        )
                        with open(result_path, "w") as f:
                            f.write(header)

                    with open(result_path, "a") as f:
                        f.write(result_line)

                    print(f"Logged to: {result_path}")
                    print(f"Disarmed: {bombs_disarmed}, Exploded: {bombs_exploded}, "
                          f"Correct: {correct_actions}, Incorrect: {incorrect_actions}")

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
    # expert_model = SmollLLM(defuser_checkpoint, device="cpu")
    expert_model = Cohere()
    asyncio.run(
        run_single_agent(
            expert_model=expert_model,
            server_url="http://0.0.0.0:8080",
            max_new_tokens=50
        )
    )
