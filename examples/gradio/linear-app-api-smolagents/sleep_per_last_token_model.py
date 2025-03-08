import time
from typing import List, Optional, Dict

from smolagents import OpenAIServerModel, LiteLLMModel, ChatMessage, Tool


class SleepPerLastTokenModelLiteLLM(LiteLLMModel):
    def __init__(self, sleep_factor: float = 0.01, **kwargs):
        super().__init__(**kwargs)
        self.sleep_factor = sleep_factor

    def __call__(
        self,
        messages: List[Dict[str, str]],
        stop_sequences: Optional[List[str]] = None,
        grammar: Optional[str] = None,
        tools_to_call_from: Optional[List[Tool]] = None,
        **kwargs,
    ) -> ChatMessage:
        if self.last_input_token_count is not None:
            sleep_time = (
                self.last_input_token_count + self.last_output_token_count
            ) * self.sleep_factor
            print(f"Sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

        return super().__call__(
            messages, stop_sequences, grammar, tools_to_call_from, **kwargs
        )


# smolagents 1.9.2 not working
# Error value must be a string ?
"""
class SleepPerLastTokenModelOpenAI(OpenAIServerModel):
    def __init__(self, sleep_factor: float = 0.01, **kwargs):
        super().__init__(**kwargs)
        self.sleep_factor = sleep_factor

    def __call__(
        self,
        messages: List[Dict[str, str]],
        stop_sequences: Optional[List[str]] = None,
        grammar: Optional[str] = None,
        tools_to_call_from: Optional[List[Tool]] = None,
        **kwargs,
    ) -> ChatMessage:
        if self.last_input_token_count is not None:
            sleep_time = self.last_input_token_count * self.sleep_factor
            print(f"Sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

        return super().__call__(
            messages, stop_sequences, grammar, tools_to_call_from, **kwargs
        )
"""
