from crewai import Agent, Crew, Task, LLM
from crewai_bomb.tools import ExpertTool, DefuserTool
from crewai_bomb.agents import defuser, expert
from crewai_bomb.tasks import *
import os
from game_mcp.game_client import Defuser, Expert
from typing import Optional, List




# Instantiate the crew with a sequential process and execute the task
crew = Crew(
    agents=[defuser,expert],
    tasks=[ask_relevat_question_task,bomb_state_task, bomb_state__anwser_task,action_proposition_task,action_exec_task], #,,bomb_state__anwser_task
    # process=Process.sequential,
    verbose=True
)


def check_bomb_state() -> bool|bool:
        result = defuserTool._run("state")

        return ("defused" in str(result).lower()), ("exploded" in str(result).lower() or "error" in str(result).lower())



def run_continuous_defusal():
        """Run the defusal process until resolution with max 5 retrys"""
        bomb_defused, bomb_exploded= check_bomb_state()

        # Necessary check to see if the bomb is still "active", as the server runs independently
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


if __name__ == '__main__':
     
    result = run_continuous_defusal()
    print("finished "+("#"*100))
    print(result)
