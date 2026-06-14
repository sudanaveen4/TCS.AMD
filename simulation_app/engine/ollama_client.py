import json
import urllib.request
import urllib.error
from engine.logger import get_system_logger

class OllamaClient:
    def __init__(self, host="http://127.0.0.1:11434", model="qwen2.5:1.5b"):
        self.host = host
        self.model = model

    def generate(self, prompt, system="", format=None, timeout=30):
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False
        }
        if format == "json":
            payload["format"] = "json"

        logger = get_system_logger()
        logger.debug(f"[Ollama Request] Model: {self.model} | System: {system}")
        logger.debug(f"[Ollama Prompt]\n{prompt}\n")

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                resp_text = result.get("response", "")
                logger.debug(f"[Ollama Response]\n{resp_text}\n")
                return resp_text
        except urllib.error.URLError as e:
            logger.error(f"Ollama Connection Error: {e}. Returning fallback mock.")
            return self._fallback_mock(prompt, format)
        except Exception as e:
            logger.error(f"Ollama Error: {e}")
            return self._fallback_mock(prompt, format)

    def _fallback_mock(self, prompt, format):
        """Robust fallback if Ollama is down so the hackathon demo doesn't crash"""
        if format == "json":
            # Mock SIPOC JSON response
            return json.dumps([
                {"id": "t1", "title": "Acknowledge Failure", "type": "automated", "status": "pending", "depends_on": [], "sipoc": {"Supplier": "System", "Input": "Alert", "Process": "Log", "Output": "Ack", "Customer": "Manager"}},
                {"id": "t2", "title": "Visual Inspection", "type": "manual", "status": "pending", "depends_on": ["t1"], "sipoc": {"Supplier": "Technician", "Input": "Sight", "Process": "Inspect", "Output": "Report", "Customer": "Agent"}},
                {"id": "t3", "title": "Generate RCA", "type": "automated", "status": "pending", "depends_on": ["t2"], "sipoc": {"Supplier": "Agent", "Input": "Timeline", "Process": "Analyze", "Output": "RCA", "Customer": "Database"}}
            ])
        return "I am the Fallback Agent. Ollama is currently unreachable, but I am here to assist with your query based on plant protocols."

# Singleton
_client = OllamaClient()
def get_ollama():
    return _client
