import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import openai
from google import genai

class BaseAgent(ABC):
    """
    Abstract base class for all data agents.
    """
    def __init__(self, model: str = "gpt-4o", provider: str = "openai"):
        self.provider = os.getenv("LLM_PROVIDER", provider)
        self.model = os.getenv("LLM_MODEL", model)
        self.client = None
        
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = openai.OpenAI(api_key=api_key)
        elif self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                self.client = genai.Client(api_key=api_key)
        elif self.provider == "ollama":
            self.client = openai.OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            )

    @abstractmethod
    async def process(self, prompt: str, dataset_metadata: Dict[str, Any], provider: str = None, model: str = None) -> Dict[str, Any]:
        pass

    async def get_completion(self, system_prompt: str, user_prompt: str, provider: str = None, model: str = None) -> str:
        """
        Generic completion helper.
        """
        # Runtime override
        target_provider = provider or self.provider
        target_model = model or self.model
        
        # Determine client
        client = self.client
        if provider and provider != self.provider:
            # Temporary client for this request if provider differs from default
            if provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                client = openai.OpenAI(api_key=api_key) if api_key else None
            elif provider == "gemini":
                api_key = os.getenv("GEMINI_API_KEY")
                client = genai.Client(api_key=api_key) if api_key else None
            elif provider == "ollama":
                client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

        if not client:
            return f"Error: AI client for {target_provider} not initialized. Check API keys."
            
        try:
            if target_provider == "gemini":
                response = client.models.generate_content(
                    model=target_model,
                    contents=f"{system_prompt}\n\n{user_prompt}"
                )
                return response.text
            else:
                response = client.chat.completions.create(
                    model=target_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"Error calling {target_provider}: {str(e)}"
