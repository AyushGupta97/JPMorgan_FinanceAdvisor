from typing import Dict, List
import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class KnowledgeStore:
    def __init__(self, db_path="knowledge_store.json", embedding_dim=384):
        self.db_path = db_path
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.texts = []
        self.store = {"clients": {}}

        if os.path.exists(self.db_path):
            with open(self.db_path, "r") as f:
                self.store = json.load(f)

    def save_session(self, client_name: str, session_id: str,
                     profile: Dict, qa_transcript: List[Dict],
                     tasks: List[Dict], final_recommendation: str):
        if client_name not in self.store["clients"]:
            self.store["clients"][client_name] = {"sessions": []}

        session_data = {
            "session_id": session_id,
            "profile": profile,
            "qa_transcript": qa_transcript,
            "tasks": tasks,
            "final_recommendation": final_recommendation
        }

        session_text = self._session_to_text(session_data)
        embedding = self.embedding_model.encode([session_text])
        self.index.add(np.array(embedding, dtype="float32"))
        self.texts.append((client_name, session_id, session_text))

        self.store["clients"][client_name]["sessions"].append(session_data)
        self._commit()

    def retrieve_similar_sessions(self, query_text: str, top_k=3):
        if len(self.texts) == 0:
            return []
        query_embedding = self.embedding_model.encode([query_text])
        D, I = self.index.search(np.array(query_embedding, dtype="float32"), top_k)
        results = []
        for idx in I[0]:
            if idx < len(self.texts):
                client_name, session_id, session_text = self.texts[idx]
                results.append({"client_name": client_name, "session_id": session_id, "text": session_text})
        return results

    def _session_to_text(self, session_data: Dict) -> str:
        qa_text = "\n".join([f"Q: {q['question']} A: {q['answer']}" for q in session_data["qa_transcript"]])
        task_text = "\n".join([f"{t['task_description']}: {t['result']}" for t in session_data["tasks"]])
        profile_text = json.dumps(session_data["profile"])
        final_advice_text = session_data["final_recommendation"]
        return f"Profile:\n{profile_text}\nQA:\n{qa_text}\nTasks:\n{task_text}\nAdvice:\n{final_advice_text}"

    def _commit(self):
        with open(self.db_path, "w") as f:
            json.dump(self.store, f, indent=2)
