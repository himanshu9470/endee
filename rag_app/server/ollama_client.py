import requests
import json

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "gemma3"):
        self.base_url = base_url
        self.model = model

    def generate_response(self, prompt: str, system_prompt: str = ""):
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"
