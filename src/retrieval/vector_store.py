import os
from typing import List, Optional
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from src.config import settings


class VectorStoreService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL_NAME, openai_api_key=settings.OPENAI_API_KEY)
        self.persist_directory = settings.VECTOR_STORE_PATH
        self.collection_name = settings.COLLECTION_NAME

    def _open(self) -> Chroma:
        # Cosine space so relevance scores are a true 0-1 similarity.
        return Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=self.collection_name,
            collection_metadata={"hnsw:space": "cosine"},
        )

    def create_or_load_vector_store(self, chunks: Optional[List[Document]] = None, force_rebuild: bool = False) -> Chroma:
        store = self._open()
        if chunks is None:
            if store._collection.count() == 0:
                raise RuntimeError("Vector store is empty. Run `python -m src.ingestion.build_index` or click 'Rebuild Index'.")
            return store
        if not chunks:
            raise RuntimeError("No documents found in data/knowledge_base - nothing to index.")
        if force_rebuild:
            store.delete_collection()  # avoid duplicate chunks on rebuild
            store = self._open()
        store.add_documents(chunks)
        return store
