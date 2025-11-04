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

conversation_history = {
    "qa_pairs": [],
    "task_results": [],
    "user_questions": []
}

conversation_active = True

while conversation_active:
    user_input = input("\nDo you have a follow up question or info for the Advisor? (leave blank if none): ").strip()
    if user_input:
        conversation_history["user_questions"].append(user_input)
    
    questions = advisor.generate_clarifying_questions(
        profile,
        user_questions=conversation_history["user_questions"]
    )
    new_qa_pairs = advisor.ask_client(questions)
    conversation_history["qa_pairs"].extend(new_qa_pairs)
    
    tasks_list = advisor.generate_analyst_tasks(
        profile,
        conversation_history["qa_pairs"],
        user_questions=conversation_history["user_questions"]
    )
    
    new_task_results = []
    for task in tasks_list:
        print(f"Executing task: {task}")
        result = analyst.execute_task(task)
        new_task_results.append(result)
    conversation_history["task_results"].extend(new_task_results)
    
    final_advice = advisor.generate_final_advice(conversation_history["task_results"])
    
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    knowledge_store.save_session(
        client_name=client.profile.name,
        session_id=session_id,
        profile=profile,
        qa_transcript=conversation_history["qa_pairs"],
        tasks=conversation_history["task_results"],
        final_recommendation=final_advice
    )
    
    print("\n=== Final Advice ===")
    print(final_advice)
    
    user_continue = input("\nDo you want to continue the conversation? (yes/no): ").strip().lower()
    if user_continue not in ["yes", "y"]:
        conversation_active = False
        print("Conversation ended. Session saved.")
    else:
        print("\nContinuing conversation with accumulated history and user questions...\n")
