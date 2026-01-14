import logging
import json
import httpx
import asyncio
import os
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
        # Initialize sub-services
        self.embedding_service = EmbeddingService()
        self.search_service = SearchService(db, self.embedding_service)
        
        # Production API Configuration
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ GEMINI_API_KEY is missing! RAG Service will fail.")

        # Use the stable alias or the specific preview if needed
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash") 
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

    async def _call_llm_with_retry(self, system_prompt: str, user_query: str, retries: int = 3) -> str:
        """Calls Gemini API with exponential backoff for production stability."""
        
        # Proper Gemini 1.5/2.5 Payload Structure
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"Context:\n{system_prompt}\n\nQuestion:\n{user_query}"}]
                }
            ],
            # System Instructions are supported in v1beta for Flash models
            "systemInstruction": {
                "parts": [{"text": "You are ZYRA, the first AI Teacher in Nepal. Be helpful, academic, and precise. Use LaTeX for math."}]
            },
            "generationConfig": {
                "temperature": 0.3,  # Lower temperature for more factual academic answers
                "maxOutputTokens": 1024
            }
        }

        async with httpx.AsyncClient() as client:
            for i in range(retries):
                try:
                    response = await client.post(self.base_url, json=payload, timeout=45.0)
                    
                    if response.status_code != 200:
                        logger.error(f"Gemini API Error {response.status_code}: {response.text}")
                        response.raise_for_status()

                    result = response.json()
                    
                    # specific safe extraction for Gemini response structure
                    try:
                        return result["candidates"][0]["content"]["parts"][0]["text"]
                    except (KeyError, IndexError) as e:
                        logger.error(f"Unexpected JSON structure: {result}")
                        return "I processed the documents but couldn't generate a clear answer."

                except Exception as e:
                    if i == retries - 1:
                        logger.error(f"LLM Final Failure after {retries} attempts: {e}")
                        return "I'm having trouble connecting to my brain right now. Please try again in a moment."
                    
                    wait_time = (2 ** i)
                    logger.info(f"LLM retry {i+1}/{retries} in {wait_time}s...")
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
            # Access attributes safely
            content = getattr(chunk, 'content', str(chunk))
            
            context_text += f"\n[Source {i+1}]:\n{content}\n"
            sources.append({
                "source_index": i + 1,
                "chunk_id": getattr(chunk, 'id', 'unknown'),
                "doc_id": getattr(chunk, 'document_id', 'unknown'),
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