from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os

class LLMInterface:
    """
    Minimal wrapper to send a system + user prompt to Google Gemini (via LangChain)
    and return the LLM response.
    """

    def __init__(self, model_name: str, temperature: float = 0.7, api_key: str = None):
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("Google API Key is missing.")

        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=self.api_key
        )

    def run(self, system_prompt: str, user_prompt: str, input_values: dict):
        """
        Sends the system + user prompt to the LLM and returns the response.
        
        Args:
            system_prompt (str): Instructions for the model.
            user_prompt (str): The user query template.
            input_values (dict): Values to fill into the user prompt.

        Returns:
            str: LLM-generated text response.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        chain = prompt | self.llm
        result = chain.invoke(input_values)

        # Handle different possible outputs
        if isinstance(result, str):
            return result
        if hasattr(result, "content"):
            return result.content
        return str(result)
