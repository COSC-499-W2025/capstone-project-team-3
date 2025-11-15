# Import the Google Generative AI Python client
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class GeminiLLMClient:
    """
    Client for interacting with Google's Gemini LLM via the Generative AI API.
    """

    def __init__(self, api_key, model="gemini-2.5-flash"):
        """
        Initialize the Gemini client with an API key and model name.
        :param api_key: Your Gemini API key as a string.
        :param model: The model name to use (default: 'gemini-2.5-flash').
        """
        genai.configure(api_key=api_key)
        self.model = model

    def generate(self, prompt):
        """
        Generate a response from the Gemini model given a prompt.
        :param prompt: The prompt string to send to the model.
        :return: The model's response text.
        """
        try:
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"Gemini API error: {e}"