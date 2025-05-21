from abc import ABC, abstractmethod
from typing import List, Dict, Any
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
import os
import cohere
import openai

class HFModel(ABC):
    """
    Abstract base class for Hugging Face language models.
    Subclasses must implement 'generate_response'.
    """

    def __init__(self, checkpoint: str, device: str = "cpu") -> None:
        """
        Initialize a Hugging Face model and tokenizer.

        :param checkpoint: The model checkpoint name or path (from Hugging Face Hub).
        :param device: The device on which to load the model ('cpu' or 'cuda').
        """
        self.checkpoint = checkpoint
        self.device = device
        self.tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained(checkpoint)
        self.model: PreTrainedModel = AutoModelForCausalLM.from_pretrained(checkpoint).to(device)

    @abstractmethod
    def generate_response(
            self,
            messages: List[Dict[str, str]],
            max_new_tokens: int = 100,
            temperature: float = 0.2,
            top_p: float = 0.9,
            top_k: int = 50,
            do_sample: bool = True,
            **kwargs: Any
    ) -> str:
        """
        Subclasses must define how to build input data from 'messages' wich is defined in prompts.py
        and produce a response string.

        """
        pass


class SmollLLM(HFModel):

    def generate_response(
            self,
            messages: List[Dict[str, str]],
            max_new_tokens: int = 50,
            temperature: float = 0.7,
            top_p: float = 0.9,
            top_k: int = 50,
            do_sample: bool = True,
            **kwargs: Any
    ) -> str:
        #  add_generation_prompt is necessary to include the response starting token
        input_text: str = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        inputs = self.tokenizer.encode(input_text, return_tensors="pt").to(self.device)

        # Generate output
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                do_sample=do_sample,
                **kwargs
            )

        return self.tokenizer.decode(outputs[0])


class Cohere():
    def __init__(self, checkpoint: str = "chat", device: str = "remote") -> None:
        self.client = cohere.Client(os.environ["COHERE_API_KEY"])

    def generate_response(
            self,
            messages: List[Dict[str, str]],
            max_new_tokens: int = 50,
            temperature: float = 0.7,
            top_p: float = 0.9,
            top_k: int = 50,
            do_sample: bool = True,
            **kwargs: Any
    ) -> str:

        # translete message to string as its only format suppoeted by Cohere
        chat_messages = []
        message=""
        for m in messages:
            if m["role"] == "user":
                message = m["content"]
            elif m["role"] == "assistant":
                chat_messages.append({"role": "chatbot", "message": m["content"]})
            elif m["role"] == "system":
                kwargs["preamble"] = m["content"]

        # get response from API
        response = self.client.chat(
            message=message, 
            # chat_history=chat_messages,
            temperature=temperature,
            max_tokens=max_new_tokens,
            p=top_p,
            **kwargs
        )

        return response.text.strip()


class OpenAIModel:
    def __init__(self, model: str = "gpt-3.5-turbo", device: str = "remote") -> None:
        """
        :param model: OpenAI model name (e.g., "gpt-3.5-turbo", "gpt-4")
        :param device: Ignored, for interface compatibility
        """
        self.model = model
        openai.api_key = os.environ["OPENAI_API_KEY"]

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 50,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,  # Ignored
        do_sample: bool = True,  # OpenAI always samples unless temp=0
        **kwargs: Any
    ) -> str:

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        return response["choices"][0]["message"]["content"].strip()

# Simple main loop for debugging purposes only
if __name__ == "__main__":
    checkpoint: str = "HuggingFaceTB/SmolLM-135M-Instruct"
    device: str = "cpu"  # or "cpu"

    llm: HFModel = SmollLLM(checkpoint, device=device)

    messages: List[Dict[str, str]] = [
        {"role": "user", "content": "What is the capital of France?"}
    ]

    response: str = llm.generate_response(
        messages,
        max_new_tokens=50,
        temperature=0.2,
        top_p=0.9,
        top_k=50,
        do_sample=True
    )

    print("\n===== Model Response =====")
    print(response)
