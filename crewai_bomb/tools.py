from crewai.tools import BaseTool
from pydantic import Field
from typing import Any
from game_mcp.game_client import Defuser, Expert
import asyncio
from asyncio import AbstractEventLoop
from typing import Optional
from pydantic import BaseModel
from typing import Type

# A class used to define or explain arguments for a given tool to the agent. 
# However, with the (relatively small) LLMs used,
# the format of the generated message based on this class often confused the models.
class MyToolInput(BaseModel):
    command: str = Field(..., description="a command to run on defuser tool. Cannot be empty, run \"state\" for bomb state")

    
class DefuserTool(BaseTool):
    name: str = "DefuserTool"
    description: str = "DefuserTool that can provide current bomb state and allows to executes choosen command on a bomb."
    args_schema: Type[BaseModel] = MyToolInput
    defuser_client:Defuser = None
    loop: Optional[AbstractEventLoop] = None
    
    class Config:
        arbitrary_types_allowed = True 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.defuser_client = Defuser()
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self.defuser_client.connect_to_server('http://localhost:8080/'))

    
    def _run(self, command: str) -> str:
        bomb_state = self.loop.run_until_complete(self.defuser_client.run(command))
        if "Unknown command" in bomb_state:
            # Get available commands by running 'help'
            bomb_state = self.loop.run_until_complete(self.defuser_client.run('state'))
            return f"Invalid command '{command}'.\n crr bomb state:\n{bomb_state}"
        
        if command == 'help':
            bomb_state+="\n[Defuser] Enter action (or 'help' or 'state'):"

        return bomb_state 



class ExpertTool(BaseTool):
    name: str = "ExpertTool"
    description: str = "Tool that can provide manual for current bomb module that has all the information necesary to defuse it."
    expert_client:Expert = None
    loop: Optional[AbstractEventLoop] = None
    class Config:
        arbitrary_types_allowed = True 


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expert_client = Expert()
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self.expert_client.connect_to_server('http://localhost:8080/'))

    
    def _run(self) -> str:
        bomb_state = self.loop.run_until_complete(self.expert_client.run())
        # print(bomb_state)
        return bomb_state 

