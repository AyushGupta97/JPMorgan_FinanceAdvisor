from src.agents.client_agent import ClientAgent
from src.agents.advisor_agent import AdvisorAgent
from src.agents.analyst_agent import AnalystAgent
from src.tools.knowledge_store import KnowledgeStore
from datetime import datetime
import json

client = ClientAgent(mode="deterministic")
knowledge_store = KnowledgeStore()
advisor = AdvisorAgent(client, knowledge_store=knowledge_store)
analyst = AnalystAgent()

profile = advisor.get_client_profile()
print("=== Client Profile ===")

print(json.dumps(profile, indent=2))
questions = advisor.generate_clarifying_questions(profile)
qa_pairs = advisor.ask_client(questions)

tasks_list = advisor.generate_analyst_tasks(profile, qa_pairs)  
task_results = []
for task in tasks_list:
    print(f"Executing task: {task}")
    result = analyst.execute_task(task)
    task_results.append(result)

final_advice = advisor.generate_final_advice(task_results)

session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
knowledge_store.save_session(
    client_name=client.profile.name,
    session_id=session_id,
    profile=profile,
    qa_transcript=qa_pairs,
    tasks=task_results,
    final_recommendation=final_advice
)

print("=== Profile ===")
print(json.dumps(profile, indent=2))
print("\n=== QA Pairs ===")
print(json.dumps(qa_pairs, indent=2))
print("\n=== Task Results ===")
print(json.dumps(task_results, indent=2))
print("\n=== Final Advice ===")
print(final_advice)
