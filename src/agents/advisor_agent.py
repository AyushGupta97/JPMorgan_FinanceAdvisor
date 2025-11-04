from typing import List, Dict, Any
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
import json
import re

class AdvisorAgent:
    def __init__(self, client, knowledge_store=None, model: str = "llama2"):
        self.client = client
        self.knowledge_store = knowledge_store
        self.llm = OllamaLLM(model=model)
        self.transcript: List[Dict[str, Any]] = []


    def get_client_profile(self):
        return self.client.profile.dict()


    def generate_clarifying_questions(self, profile: Dict[str, Any], user_questions: list = None) -> list:
        risk = profile.get("risk_aversion", "medium")
        user_context = ""
        if user_questions:
            user_context = "\nUser follow-up questions:\n" + "\n".join(user_questions)

        prompt = f"""
        You are a financial advisor. Generate 1-3 clarifying questions based on the client profile and any follow-up questions.
        Client Profile:
        {json.dumps(profile)}
        Risk Aversion: {risk}
        {user_context}
        Respond in JSON array of questions only.
        """

        response = self.llm.invoke(prompt)
        import re
        try:
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                questions = json.loads(match.group(0))
            else:
                raise ValueError("No JSON array found.")
        except Exception:
            questions = [
                "Can you tell me more about your investment time horizon?",
                "Do you have any major upcoming expenses?",
                "How comfortable are you with short-term market fluctuations?"
            ]
        return questions



    def ask_client(self, questions: List[str]) -> List[Dict[str, str]]:
        qa_pairs = []
        for q in questions:
            a = self.client.ask_question(q)
            qa_pairs.append({"question": q, "answer": a})
        self.transcript.extend(qa_pairs)
        return qa_pairs


    def generate_analyst_tasks(self, profile: Dict[str, Any], transcript: List[Dict[str, str]], user_questions: list = None) -> List[Dict[str, Any]]:
        default_tasks = [
                {
                    "task_description": "Research medium-risk index funds.",
                    "task_type": "research",
                    "context": "Client wants balanced growth."
                },
                {
                    "task_description": "Compare 401(k) vs Roth IRA returns.",
                    "task_type": "compare",
                    "context": "Client focused on retirement savings."
                }
            ]
        
        user_context = ""
        if user_questions:
            user_context = "\nUser follow-up questions:\n" + "\n".join(user_questions)
        
        prompt = f"""
        You are a senior financial advisor preparing tasks for an Analyst Agent.

        Client Profile:
        {json.dumps(profile, indent=2)}

        Clarifying Q&A:
        {json.dumps(transcript, indent=2)}
                                              
        User Questions:
        {user_context}

        Output STRICTLY as a list of JSON and make sure to formart it correctly
        
        Task:
        Generate 3 to 5 actionable research tasks for an Analyst Agent. Each task should include:
        - task_description (string)
        - task_type (research, compare, summarize) - these are the only task types allowed
        - context (brief string explaining why this task is needed)
        STRICTLY Provide the tasks as a JSON array, without any additional commentary or text outside the array

        Example Tasks:
        {json.dumps(default_tasks, indent=2)}
        ]
        """
        response = self.llm.invoke(prompt)
        print(response)
        try:
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                tasks = json.loads(match.group(0))
            else:
                raise ValueError("No JSON array found in LLM response.")
        except Exception as e:
            print(f"[Error parsing Analyst tasks: {e}] Falling back to default tasks.")
            tasks = default_tasks

        return tasks


    def generate_final_advice(self, task_results: List[Dict[str, str]]) -> str:
        profile = self.client.profile.dict()
        tasks_summary = "\n".join([f"- {t['task_description']}: {t['result']}" for t in task_results])
        past_sessions_texts = []

        if self.knowledge_store:
            query_text = f"Profile: {profile}, QA: {self.transcript}"
            similar_sessions = self.knowledge_store.retrieve_similar_sessions(query_text, top_k=2)
            for s in similar_sessions:
                past_sessions_texts.append(s["text"])

        context_text = "\n\n".join(past_sessions_texts) if past_sessions_texts else "No past similar sessions."

        prompt = f"""
        You are a financial advisor. Based on profile, Q&A, task results, and past sessions, give one actionable recommendation.
        Profile: {profile}
        QA: {self.transcript}
        Task Results: {tasks_summary}
        Context from past sessions: {context_text}
        """
        return self.llm.invoke(prompt)
