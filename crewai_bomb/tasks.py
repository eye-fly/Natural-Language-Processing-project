from crewai import Agent, Crew, Task, LLM
# from crewai_bomb.agents import defuser_agent, expert_agent
from crewai_bomb.agents import *

# Tasks are performed in a sequential manner
# Dividing the process into small tasks helps the model understand exactly what it is supposed to do
# and greatly reduces the number of misuses of the provided tools
bomb_state_task = Task(
    description="Use the DefuserTool to check bomb state.",
    expected_output="bomb state provided by running DefuserTool state",
    agent=defuser_agent,
    verbose=True,
    allow_delegation=False,
    tools=[defuserTool],
    function_args={"command": "state"}
)

ask_relevat_question_task = Task(
    description="Use the ExpertTool to get bomb manaual and ask bomb agent a queston to help you decide wich case is relevant and what action shoud he later take.",
    expected_output="Question about bomb current state.",
    agent=expert_agent,
    verbose=True,
    allow_delegation=False,
    tools=[expertTool],

)

bomb_state__anwser_task = Task(
    description="use bomb state to provided anwser accuretly what is you current bomb state and what are you currently doing to help the expert deduce correct case/version of the module.",
    expected_output="a anwser to a question from the expert about the bomb state, and currently performed actions if any",
    agent=defuser_agent,
    verbose=True,
    context=[ask_relevat_question_task,bomb_state_task] 
)

action_proposition_task = Task(
    description="Use the ExpertTool to get bomb manaual and based on agent anwser deduce correct case and what action should he take to defuse a modlue. It's very important to not make a mistake and choose a correct action. Think carefully.",
    expected_output="Instruction what action should be taken.",
    agent=expert_agent,
    verbose=True,
    allow_delegation=False,
    tools=[expertTool],
    context=[bomb_state__anwser_task] 
)

action_exec_task = Task(
    description="execute action(from the list provided in bomb state) recommended by the bomb expert using DefuserTool. Only issue a command from the available ones listed in current bomb state and use exatly the same format as listed dont replace spaces with _. Use provided tool.",
    expected_output="The changed bomb state **after** performing **ALL* action recommended by the expert on the bomb with defuserTool. if bomb EXPLODED during that peoccess return that information",
    agent=defuser_agent,
    tools=[defuserTool],
    context=[bomb_state_task, action_proposition_task] 
)