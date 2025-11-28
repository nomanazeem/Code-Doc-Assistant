import pickle
import os
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer

class RAGPipeline:
    def __init__(self, index_path: str):
        self.index_path = index_path
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_data = self._load_index()
    
    def _load_index(self) -> Dict:
        """Load the code index"""
        index_file = os.path.join(self.index_path, 'code_index.pkl')
        if os.path.exists(index_file):
            with open(index_file, 'rb') as f:
                return pickle.load(f)
        return {'elements': [], 'embeddings': np.array([])}
    
    def get_relevant_context(self, file_path: str, code_content: str, top_k: int = 5) -> List[Dict]:
        """Get relevant context from the codebase for documentation generation"""
        if not self.index_data['elements']:
            return []
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([code_content])
        
        # Calculate similarities
        similarities = np.dot(query_embedding, self.index_data['embeddings'].T)[0]
        
        # Get top-k most similar elements (excluding the current file)
        relevant_indices = np.argsort(similarities)[::-1][:top_k*2]  # Get more to filter
        relevant_elements = []
        
        for idx in relevant_indices:
            element = self.index_data['elements'][idx]
            if element['file_path'] != file_path:  # Exclude current file
                relevant_elements.append(element)
            if len(relevant_elements) >= top_k:
                break
        
        return relevant_elements
    
    def update_index(self, new_elements: List[Dict]):
        """Update the index with new elements"""
        if not new_elements:
            return
        
        # Create embeddings for new elements
        texts_to_embed = [
            f"{elem['type']} {elem['name']}: {elem.get('content_snippet', '')}" 
            for elem in new_elements
        ]
        
        new_embeddings = self.embedding_model.encode(texts_to_embed)
        
        # Update index data
        self.index_data['elements'].extend(new_elements)
        if len(self.index_data['embeddings']) > 0:
            self.index_data['embeddings'] = np.vstack([self.index_data['embeddings'], new_embeddings])
        else:
            self.index_data['embeddings'] = new_embeddings
        
        # Save updated index
        os.makedirs(self.index_path, exist_ok=True)
        with open(os.path.join(self.index_path, 'code_index.pkl'), 'wb') as f:
            pickle.dump(self.index_data, f)