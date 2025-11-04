from typing import List, Dict, Any
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from ..tools.web_search import InternetSearchTool
import json

class AnalystAgent:
    def __init__(self, model: str = "llama2"):
        self.llm = OllamaLLM(model=model)
        self.search_tool = InternetSearchTool()
    
    def search_web(self, query: str, max_results: int = 5) -> List[str]:
        return self.search_tool.search(query, max_results)

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("task_type", "research")
        task_desc = task.get("task_description", "")
        context = task.get("context", "")

        if task_type in ["research", "compare", "summarize"]:
            search_results = self.search_web(task_desc)
            result_summary = self.summarize_results(task_desc, search_results, task_type, context)
        else:
            result_summary = "Unsupported task type"

        return {
            "task_description": task_desc,
            "task_type": task_type,
            "context": context,
            "result": result_summary
        }

    def summarize_results(self, task_desc: str, search_results: List[str], task_type: str, context: str) -> str:
        prompt = PromptTemplate.from_template("""
        You are an analyst tasked with summarizing web research.

        Task description:
        {task_desc}

        Context:
        {context}

        Search Results:
        {search_results}

        Task Type:
        {task_type}

        Output:
        Write a concise summary (3-5 sentences) highlighting key points, comparisons, or recommendations as appropriate.
        Respond in plain text, suitable for Advisor to use.
        """)

        response = self.llm.invoke(prompt.format(
            task_desc=task_desc,
            context=context,
            search_results=json.dumps(search_results, indent=2),
            task_type=task_type
        ))
        return response

    def run_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for task in tasks:
            res = self.execute_task(task)
            results.append(res)
        return results

if __name__ == "__main__":
    sample_tasks = [
        {
            "task_description": "Find top-performing medium-risk index funds suitable for a 35-year-old client.",
            "task_type": "research",
            "context": "Client has medium risk tolerance, 100k assets, interested in retirement savings."
        },
        {
            "task_description": "Compare average returns of 401(k) vs Roth IRA over the past 5 years.",
            "task_type": "compare",
            "context": "Client wants retirement planning guidance."
        }
    ]

    analyst = AnalystAgent()
    results = analyst.run_tasks(sample_tasks)
    print(json.dumps(results, indent=2))
