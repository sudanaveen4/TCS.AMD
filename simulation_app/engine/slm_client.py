import requests

class SLMClient:
    def __init__(self, ollama_url="http://localhost:11434/api/generate", model="qwen2:1.5b"):
        self.url = ollama_url
        self.model = model
        
    def generate_alert(self, machine_id, sensor_name, value):
        """
        Uses a local SLM to generate a contextual alert description.
        In a real plant, it would consult the ontology/RAG.
        """
        prompt = f"Industrial Machine '{machine_id}' triggered a critical anomaly. The sensor '{sensor_name}' spiked to {value:.2f}. Write a single brief 1-sentence operational risk warning for the shift operator."
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            # Short timeout to not block the simulation
            response = requests.post(self.url, json=payload, timeout=1.5)
            if response.status_code == 200:
                return response.json().get("response", "").strip()
        except requests.exceptions.RequestException:
            pass
            
        # Fallback if SLM is down
        return f"Warning: Abnormal behavior detected on {sensor_name}. Inspect machine {machine_id} immediately."
        
    # -------------------------------------------------------------------------
    # AMD MI300X SETUP (Large Models >70B Parameters) - COMMENTED
    # -------------------------------------------------------------------------
    # def generate_alert_mi300x(self, machine_id, sensor_name, value):
    #     import openai
    #     client = openai.Client(
    #         base_url="http://<MI300X_VLLM_SERVER_IP>:8000/v1",
    #         api_key="empty"
    #     )
    #     prompt = f"You are an industrial AI agent. Machine {machine_id}..."
    #     response = client.chat.completions.create(
    #         model="meta-llama/Meta-Llama-3-70B-Instruct",
    #         messages=[{"role": "user", "content": prompt}],
    #         max_tokens=50
    #     )
    #     return response.choices[0].message.content
