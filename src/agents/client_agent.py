from pydantic import BaseModel, Field
from typing import Dict, Any, List
import random
import json

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate


class ClientProfile(BaseModel):
    name: str
    age: int = Field(..., ge=18, le=100)
    risk_aversion: str  # "low", "medium", "high"
    assets: float 
    investments: Dict[str, float]
    financial_goals: List[Dict[str, Any]]


class ClientAgent:
    def __init__(self, name: str = "John Doe", mode: str = "deterministic"):
        self.name = name
        self.mode = mode
        if mode == "deterministic":
            self.profile = self.generate_static_profile()
        else:
            self.profile = self.generate_llm_profile()

    def generate_static_profile(self) -> ClientProfile:
        age = random.randint(25, 65)
        risk_aversion = random.choice(["low", "medium", "high"])
        assets = round(random.uniform(5000, 500000), 2)
        investments = {
            "stocks": round(assets * random.uniform(0.2, 0.6), 2),
            "bonds": round(assets * random.uniform(0.1, 0.3), 2),
            "cash": round(assets * random.uniform(0.1, 0.3), 2)
        }
        goals = [
            {"title": random.choice([
                "Save for retirement", "Buy a house",
                "Start a business", "Children's education"
            ]), "amount": round(random.uniform(20000, 300000), 2),
               "timeline": random.choice(["5 years", "10 years", "15 years"])
            }
        ]
        return ClientProfile(
            name=self.name,
            age=age,
            risk_aversion=risk_aversion,
            assets=assets,
            investments=investments,
            financial_goals=goals
        )

    def generate_llm_profile(self) -> ClientProfile:
        llm = OllamaLLM(model="llama2")
        prompt = PromptTemplate.from_template("""
        You are simulating a financial client profile.
        Generate a JSON object with these fields:
        - name (string)
        - age (integer)
        - risk_aversion (low/medium/high)
        - assets (float)
        - investments (object: stocks, bonds, cash)
        - financial_goals (list of objects with 'title', 'amount', and 'timeline' in years), 
        financial goals can be about savings goal for retirement, buying a house, education, children's education fund, etc.
        Output valid JSON only.
        """)

        response = llm.invoke(prompt.format())
        print(response)

        try:
            profile_data = json.loads(response)
            return ClientProfile(**profile_data)
        except Exception as e:
            print(f"[Error parsing LLM output: {e}] Falling back to deterministic profile.")
            return self.generate_static_profile()
        
    def ask_question(self, question) -> str:
        print("Question:", question)
        return input("Client's answer: ")
    
# Demo purpose to see the generated profile
if __name__ == "__main__":
    print("=== LLM Generated Profile ===")
    agent = ClientAgent(mode="llm")
    print(agent.profile)

    print("\n=== Static Profile ===")
    agent_det = ClientAgent(mode="deterministic")
    print(agent_det.profile)