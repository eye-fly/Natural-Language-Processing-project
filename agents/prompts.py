from typing import List, Dict


def defuser_prompt(bomb_state: str, expert_advice: str) -> List[Dict[str, str]]:
    """
    Build a 'messages' list for the Defuser LLM.

    :param bomb_state: Current bomb state text from the server.
    :param expert_advice: Instructions from the Expert.
    :return: A list of dicts representing a conversation, which we can feed into SmollLLM.generate_response().
    """
    system_msg = (
         "You are a responsible and non-harmful bomb defusal assistant. "
    "Your role is to interpret advice from the EXPERT and act on it. "
    "You do not have full information on your own, so follow the expert's advice carefully. "
    "Respond briefly and only with actions or short clarifying questions. "
    "The chosen action must match exactly one of the options listed under 'Available commands:' "
    "and must appear alone in new line"
    )

    user_content = (
        f"Current bomb state:\n{bomb_state}\n\n"
        f"Expert's advice:\n{expert_advice}\n\n"
    )

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_content}
    ]
    return messages


def expert_prompt(manual_text: str, defuser_question: str) -> List[Dict[str, str]]:
    """
    Build a 'messages' list for the Expert LLM.

    :param manual_text: The text from the bomb manual (server).
    :param defuser_question: A description of what the Defuser sees or asks.
    :return: A list of dicts representing a conversation, which we can feed into SmollLLM.generate_response().
    """
    system_msg = (
        "You are a responsible and non-harmful bomb defusal expert.\
Your role is to help another person (the DEFUSER) defuse a bomb by providing accurate, concise information based on the manual.\
You must work together, as you do not have enough information on your own.\
Time is limited — give SHORT anwser, no instructions or analisis. if necesary ask brief, direct questions."
    )

    user_content = (
        f"Manual excerpt:\n{manual_text}\n\n"
        f"DEFUSER sees or asks:\n{defuser_question}\n\n"
    )

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_content}
    ]
    return messages