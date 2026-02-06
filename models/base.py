from abc import ABC, abstractmethod

class BaseModel(ABC):
    """Abstract base class for all AI models."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        """
        Generates a response from the model asynchronously.
        
        Args:
            prompt (str): The input prompt.
            
        Returns:
            str: The model's response.
        """
        pass
