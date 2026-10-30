from typing import List, Tuple
from langchain_core.documents import Document
from src.retrieval.vector_store import VectorStoreService
from src.config import settings


class SupportRetriever:
    def __init__(self):
        self.vector_store = VectorStoreService().create_or_load_vector_store()

    def retrieve_with_relevance_gate(self, query: str) -> Tuple[List[Document], bool]:
        """Returns (docs, is_refusal). Docs below SCORE_THRESHOLD similarity are dropped."""
        results = self.vector_store.similarity_search_with_relevance_scores(query, k=settings.RETRIEVAL_K)
        valid_docs = [doc for doc, score in results if score >= settings.SCORE_THRESHOLD]
        if not valid_docs:
            return [], True
        return valid_docs, False
