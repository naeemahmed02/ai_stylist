from llm_interface import LLMInterface

from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env into os.environ


# Initialize
llm = LLMInterface(model_name="gemini-2.5-flash")

system_prompt = "You are an AI stylist assistant. Answer clearly and concisely."
user_prompt = "Given the user preferences {input}, suggest a fashion outfit."

input_values = {
    "input": "Body shape: hourglass, Styles: elegant/minimal, Occasion: party, Budget: $120"
}

response = llm.run(system_prompt, user_prompt, input_values)
print(response)
