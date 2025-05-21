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
# llm=ChatCohere(temperature=0.4)
# llm = LLM(
#     model="gpt-4o-mini",
    # temperature=0.3,    
#     timeout=120,        
    # max_tokens=100,      
    # top_p=0.8,           
#     seed=42               # For reproducible results
# )
from langchain_community.llms import Ollama

# Instantiate local Ollama LLM (qwen2:1.5b)
llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434",

    temperature=0.3,
    # num_predict=100,
    top_p=0.8,
)

llm = LLM(
    model="ollama/qwen3:8b",
    base_url="http://localhost:11434",

    temperature=0.3,
    top_p=0.8,

)
# 
# llm = LLM(
#     model="ollama/deepseek-r1:7b",
#     base_url="http://localhost:11434"

#     # temperature=0.4,
#     # # timeout=120,           # Ollama doesn't use timeout parameter
#     # # max_tokens=100,       # Control response length with num_predict instead
#     # num_predict=100,        # Equivalent to max_tokens
#     # top_p=0.9,
#     # repeat_penalty=1.1,     # Ollama's parameter for reducing repetition (similar to frequency_penalty)
#     # seed=42               # Not all local models support seeding
# )

# Instantiate DefuserTool
defuserTool = DefuserTool()
expertTool = ExpertTool()

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

expert = Agent(
    role='Bomb Defusal Expert',
    goal='help to defuse bombs safely by comiunincating with defising agent and giving accurate instructions.',
    backstory="An AI trained in bomb module analisys based on manual.",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    # llm='gpt-4o-mini'
    tools=[expertTool]
)

bomb_state_task = Task(
    description="Use the DefuserTool to check bomb state.",
    expected_output="bomb state provided by running DefuserTool state",
    agent=defuser,
    verbose=True,
    allow_delegation=False,
    tools=[defuserTool],
    function_args={"command": "state"}
)

ask_relevat_question_task = Task(
    description="Use the ExpertTool to get bomb manaual and ask bomb agent a queston to help you decide wich case is relevant and what action shoud he later take.",
    expected_output="Question about bomb current state.",
    agent=expert,
    verbose=True,
    allow_delegation=False,
    tools=[expertTool],
    # context=[ExpertTool] 
    # function_args={"command": "state"}
)

bomb_state__anwser_task = Task(
    description="use bomb state to provided anwser accuretly what is you current bomb state and what are you currently doing to help the expert deduce correct case/version of the module.",
    expected_output="a anwser to a question from the expert about the bomb state, and currently performed actions if any",
    agent=defuser,
    verbose=True,
    # tools=[defuserTool],
    context=[ask_relevat_question_task,bomb_state_task] 
)

action_proposition_task = Task(
    description="Use the ExpertTool to get bomb manaual and based on agent anwser deduce correct case and what action should he take to defuse a modlue. It's very important to not make a mistake and choose a correct action. Think carefully.",
    expected_output="Instruction what action should be taken.",
    agent=expert,
    verbose=True,
    allow_delegation=False,
    tools=[expertTool],
    context=[bomb_state__anwser_task] 
    # function_args={"command": "state"}
)

action_exec_task = Task(
    description="execute action(from the list provided in bomb state) recommended by the bomb expert using DefuserTool. Only issue a command from the available ones listed in current bomb state and use exatly the same format as listed dont replace spaces with _. Use provided tool.",
    expected_output="The changed bomb state **after** performing **ALL* action recommended by the expert on the bomb with defuserTool. if bomb EXPLODED during that peoccess return that information",
    agent=defuser,
    tools=[defuserTool],
    context=[bomb_state_task, action_proposition_task] 
    # function_args={"command": "state"}
)

# Instantiate the crew with a sequential process and execute the task
crew = Crew(
    agents=[defuser,expert],
    tasks=[ask_relevat_question_task,bomb_state_task, bomb_state__anwser_task,action_proposition_task,action_exec_task], #,,bomb_state__anwser_task
    # process=Process.sequential,
    verbose=True
)

def check_bomb_state() -> bool|bool:
        result = defuserTool._run("state")
        """Check the bomb state from the last task result"""
        return ("defused" in str(result).lower()), ("exploded" in str(result).lower() or "error" in str(result).lower())



def run_continuous_defusal():
        """Run the defusal process until resolution"""
        bomb_defused, bomb_exploded= check_bomb_state()
        if(bomb_exploded or bomb_defused):
              defuserTool._run("restart")
        bomb_defused, bomb_exploded= check_bomb_state()
        attempt=0
        while (not bomb_defused and 
               not bomb_exploded):
            if(attempt>5):
                 break
            
            # print(f"\n=== Attempt {attempt + 1} ===")
            
            # Execute all tasks sequentially
            _ = crew.kickoff()
            bomb_defused, bomb_exploded= check_bomb_state()
            
            attempt += 1
            
            if bomb_defused:
                print("Bomb successfully defused!")
                return True
            elif bomb_exploded:
                print("Bomb exploded!")
                return False
            
        print(f"Reached maximum attempts without resolution")
        return False

# YOUR CODE ENDS HERE

import asyncio

if __name__ == '__main__':
    # YOUR CODE STARTS HERE
     

    result = run_continuous_defusal()
    print("######################")
    print(result)
    # YOUR CODE ENDS HERE
