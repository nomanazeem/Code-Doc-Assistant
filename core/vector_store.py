import chromadb
from typing import List, Dict
import uuid

class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name="code_documentation")
    
    def add_code_elements(self, elements: List[Dict]):
        """Add code elements to vector store"""
        documents = []
        metadatas = []
        ids = []
        
        for elem in elements:
            doc_text = f"""
            Type: {elem['type']}
            Name: {elem['name']}
            File: {elem['file_path']}
            Content: {elem.get('content_snippet', '')}
            Docstring: {elem.get('docstring', '')}
            """
            
            documents.append(doc_text)
            metadatas.append({
                'type': elem['type'],
                'name': elem['name'],
                'file_path': elem['file_path'],
                'line_start': elem.get('line_start', 0)
            })
            ids.append(str(uuid.uuid4()))
        
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    def search_similar_code(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar code elements"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        similar_elements = []
        for i in range(len(results['documents'][0])):
            similar_elements.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if results['distances'] else 0
            })
        
        return similar_elements