from src.ingestion.loaders import DocumentLoaderService
from src.ingestion.chunking import ChunkingService
from src.retrieval.vector_store import VectorStoreService

def build_kb_index(force_rebuild: bool = True):
    loader = DocumentLoaderService()
    raw_docs = loader.load_documents()
    chunker = ChunkingService()
    chunks = chunker.split_documents(raw_docs)
    vector_service = VectorStoreService()
    vector_service.create_or_load_vector_store(chunks=chunks, force_rebuild=force_rebuild)

if __name__ == "__main__":
    build_kb_index(force_rebuild=True)
