from google import genai
from langchain_openai import ChatOpenAI  # or any other LLM provider
import os

#Load env files
from dotenv import load_dotenv
load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


gemini_imagen3_client = genai.Client(api_key=GEMINI_API_KEY)
openai_41_mini_client = ChatOpenAI(model="gpt-4.1-mini")
