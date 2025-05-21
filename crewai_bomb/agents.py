from crewai import Agent, Crew, Task, LLM
from crewai_bomb.tools import ExpertTool, DefuserTool

llm = LLM(
    model="ollama/qwen3:8b",
    base_url="http://localhost:11434",

    temperature=0.3,
    top_p=0.8,

)

# Instantiate DefuserTool
defuserTool = DefuserTool()
expertTool = ExpertTool()

defuser_agent = Agent(
    role='Bomb Defusal Assistant',
    goal='Defuse bombs safely using instructions from the expert.',
    backstory="An AI trained in bomb module decoding and execution.",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    # llm='gpt-4o-mini'
    tools=[defuserTool]
)

expert_agent = Agent(
    role='Bomb Defusal Expert',
    goal='help to defuse bombs safely by comiunincating with defising agent and giving accurate instructions.',
    backstory="An AI trained in bomb module analisys based on manual.",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    # llm='gpt-4o-mini'
    tools=[expertTool]
)