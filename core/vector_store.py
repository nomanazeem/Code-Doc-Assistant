# core/vector_store.py
import numpy as np
from typing import List, Dict, Any
import pickle
import os
from sentence_transformers import SentenceTransformer
import faiss

class CodeVectorStore:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.metadata = []
        self.dimension = 384  # Default for all-MiniLM-L6-v2

    def index_codebase(self, parsed_data: Dict[str, Any]):
        """Index the parsed codebase into vector embeddings."""
        documents = self._prepare_documents(parsed_data)

        if not documents:
            raise ValueError("No documents to index")

        # Generate embeddings
        texts = [doc['text'] for doc in documents]
        embeddings = self.model.encode(texts)

        # Create FAISS index
        self.dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings.astype('float32'))

        # Store metadata
        self.metadata = documents

    def _prepare_documents(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare code elements for indexing."""
        documents = []

        # Index functions
        for func in parsed_data.get('functions', []):
            doc_text = f"""
            Function: {func['name']}
            File: {func['file_path']}
            Arguments: {', '.join(func.get('args', []))}
            Existing Docstring: {func.get('docstring', 'None')}
            Type: {func['type']}
            """
            documents.append({
                'text': doc_text,
                'type': 'function',
                'metadata': func
            })

        # Index classes
        for cls in parsed_data.get('classes', []):
            doc_text = f"""
            Class: {cls['name']}
            File: {cls['file_path']}
            Methods: {', '.join(cls.get('methods', []))}
            Existing Docstring: {cls.get('docstring', 'None')}
            Type: {cls['type']}
            """
            documents.append({
                'text': doc_text,
                'type': 'class',
                'metadata': cls
            })

        return documents

    def search_similar(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar code elements."""
        if self.index is None:
            raise ValueError("Index not initialized. Call index_codebase first.")

        query_embedding = self.model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_embedding, k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                results.append({
                    'metadata': self.metadata[idx]['metadata'],
                    'distance': distances[0][i],
                    'text': self.metadata[idx]['text']
                })

        return results

    def save(self, path: str):
        """Save the vector store to disk."""
        if self.index is None:
            raise ValueError("No index to save")

        os.makedirs(path, exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, os.path.join(path, 'index.faiss'))

        # Save metadata
        with open(os.path.join(path, 'metadata.pkl'), 'wb') as f:
            pickle.dump(self.metadata, f)

    def load(self, path: str):
        """Load the vector store from disk."""
        # Load FAISS index
        self.index = faiss.read_index(os.path.join(path, 'index.faiss'))

        # Load metadata
        with open(os.path.join(path, 'metadata.pkl'), 'rb') as f:
            self.metadata = pickle.load(f)