from crewai.tools import BaseTool
from pydantic import Field
from typing import Any
from game_mcp.game_client import Defuser, Expert

# Feel free to import any libraries you need - if needed change requirements.txt
# In this file it also applies to classes and functions :)


class DefuserTool(BaseTool):
    # YOUR CODE STARTS HERE
    name: str = "DefuserTool"
    description: str = "DefuserTool that can provide current bomb state and allows to executes choosen command on a bomb."
    defuser_client:Defuser 
    
    class Config:
        arbitrary_types_allowed = True 

    # def __init__(self, defuser_client, **kwargs):
    #     super().__init__(**kwargs)  # Call BaseTool constructor
    #     defuser_client = defuser_client  # Store custom client
    
    async def _run(self, command: str) -> str:
        bomb_state = await self.defuser_client.run(command)
        print(bomb_state[0])
        return bomb_state 
    # YOUR CODE ENDS HERE


class ExpertTool(BaseTool):
    # YOUR CODE STARTS HERE
    pass
    # YOUR CODE ENDS HERE
