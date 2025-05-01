from crewai import Agent, Crew, Task, LLM
from crewai_bomb.tools import ExpertTool, DefuserTool
import cohere
from langchain_cohere import ChatCohere
import os
from game_mcp.game_client import Defuser, Expert
from typing import Optional, List

# Feel free to import any libraries you need - if needed change requirements.txt
# In this file it also applies to classes and functions :)

# YOUR CODE STARTS HERE
# class Cohere(LLM):
#     def __init__(self, checkpoint: str = "command-r", stop: Optional[List[str]] = None):
#         self.client = cohere.Client(os.environ["COHERE_API_KEY"])
#         self.checkpoint = checkpoint
#         self.stop = stop or [] 
#         self.model_name = checkpoint  

#     def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
#         # Merge external stop with internal
#         stop_sequences = list(set((stop or []) + self.stop))
#         response = self.client.generate(
#             model=self.checkpoint,
#             prompt=prompt,
#             max_tokens=300,
#             temperature=0.5,
#             stop_sequences=stop_sequences if stop_sequences else None
#         )
#         return response.generations[0].text.strip()

#     @property
#     def _llm_type(self) -> str:
#         return "custom-cohere"

class LoggingChatCohere(ChatCohere):
    def __call__(self,messages, callbacks):
        print("\n=== MODEL INPUT ===")
        if isinstance(messages, list):
            for msg in messages:
                print(f"[{msg.type.upper()}] {msg.content}")
        else:
            print(messages)
        print("=== END INPUT ===\n")
        return self.super(messages, callbacks=callbacks)
    
# Instantiate LLM
llm=LoggingChatCohere(temperature=0.4)
# llm = LLM(
#     model="gpt-4o-mini",
#     temperature=0.5,        # Higher for more creative outputs
#     timeout=120,           # Seconds to wait for response
#     max_tokens=100,       # Maximum length of response
#     top_p=0.9,            # Nucleus sampling parameter
#     frequency_penalty=0.1, # Reduce repetition
#     presence_penalty=0.1,  # Encourage topic diversity
#     # response_format={"type": "json"},  # For structured outputs
#     seed=42               # For reproducible results
# )

# Initialize defuser_client for the tool
defuser_client = Defuser()

# Instantiate DefuserTool
defuserTool = DefuserTool(defuser_client=defuser_client)

defuser = Agent(
    role='Bomb Defusal Assistant',
    goal='Defuse bombs safely using instructions from the expert.',
    backstory="An AI trained in bomb module decoding and execution.",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    # llm='gpt-4o-mini'
    tools=[defuserTool]
)

bomb_state_task = Task(
    description="Use the DefuserTool to inspect the bomb..",
    expected_output="The bomb state provided by DefuserTool",
    agent=defuser,
    verbose=True,
    tools=[defuserTool],
    function_args={"command": "state"}
)

defuse_task = Task(
    description="Use the DefuserTool to inspect and act on the bomb. Only issue a command from the available ones.",
    expected_output="The bomb should be disarmed without triggering an explosion.",
    agent=defuser,
    tools=[defuserTool],
    context=[bomb_state_task] 
    # function_args={"command": "state"}
)

# Instantiate the crew with a sequential process and execute the task
crew = Crew(
    agents=[defuser],
    tasks=[bomb_state_task],
    # process=Process.sequential,
    verbose=True
)
# YOUR CODE ENDS HERE


if __name__ == '__main__':
    # YOUR CODE STARTS HERE
    result = crew.kickoff()
    print("######################")
    print(result)
    # YOUR CODE ENDS HERE
