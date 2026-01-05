import logging
import json
import httpx
import asyncio
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
   
from app.services.embeddings.search_service import SearchService
from app.services.embeddings.embeding_services import EmbeddingService

logger = logging.getLogger(__name__)

class RAGService:
    """
    The Brain of ZYRA. Handles the full RAG pipeline:
    Search -> Rank -> Build Prompt -> LLM Call -> Final Answer.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.search_service = SearchService(db, self.embedding_service)
        # Production API Configuration
        self.api_key = "" # Environment injects this at runtime
        self.model_name = "gemini-2.5-flash-preview-09-2025"
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

    async def _call_llm_with_retry(self, system_prompt: str, user_query: str, retries: int = 5) -> str:
        """Calls Gemini API with exponential backoff for production stability."""
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_prompt}\n\nUser Question: {user_query}"}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": "You are ZYRA, the first AI Teacher in Nepal. Be helpful, academic, and precise."}]
            }
        }

        async with httpx.AsyncClient() as client:
            for i in range(retries):
                try:
                    response = await client.post(self.base_url, json=payload, timeout=30.0)
                    response.raise_for_status()
                    result = response.json()
                    return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "I couldn't generate an answer.")
                except Exception as e:
                    if i == retries - 1:
                        logger.error(f"LLM Final Failure: {e}")
                        return "I'm having trouble connecting to my brain right now. Please try again in a moment."
                    wait_time = (2 ** i)
                    await asyncio.sleep(wait_time)

    async def answer_question(
        self, 
        query: str, 
        document_id: Optional[str] = None,
        subject_filter: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Full Pipeline Implementation
        """
        logger.info(f"RAG Query received: {query}")

        # 1. SEARCH & RANK
        # SearchService handles vector similarity and returns ranked (Chunk, Score) tuples
        search_results = await self.search_service.search(
            query=query, 
            top_k=top_k, 
            document_id=document_id
        )

        if not search_results:
            return {
                "answer": "I don't have any documents related to that topic in my database yet. Please upload a relevant PDF so I can help you!",
                "sources": [],
                "status": "no_context"
            }

        # 2. BUILD PROMPT (Augmentation)
        context_text = ""
        sources = []
        for i, (chunk, score) in enumerate(search_results):
            context_text += f"\n[Source {i+1}]:\n{chunk.content}\n"
            sources.append({
                "source_index": i + 1,
                "chunk_id": chunk.id,
                "doc_id": chunk.document_id,
                "relevance_score": round(float(score), 4)
            })

        system_prompt = f"""
        You are an expert Academic Assistant. Use the provided context to answer the user's question.
        
        RULES:
        1. Only use the information in the context below. 
        2. If the answer is not in the context, say: "I couldn't find specific information about this in your documents, but based on general knowledge..." 
        3. Use LaTeX for all mathematical formulas (e.g., $E=mc^2$).
        4. Always cite your sources using [Source X] notation where X is the source index.
        5. Keep responses structured with headings if the answer is long.

        CONTEXT:
        {context_text}
        """

        # 3. CALL LLM
        answer = await self._call_llm_with_retry(system_prompt, query)

        # 4. RETURN FINAL ANSWER
        return {
            "answer": answer,
            "sources": sources,
            "query": query,
            "status": "success"
        }