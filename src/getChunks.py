from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document
from typing import List
import re
import os

class getChunks:
    """
    Get a LLM to extract useful info in dictionary format (flashcards)
    """
    def __init__(self, file:str):
        self.folder = file

    def run(self):
        text: str = self._loadMD()
        chunks: List[str] = self._chunk(text)
        self._store(chunks)
    
    def _loadMD(self) -> str:
        markdown_path = f"experiments/{self.folder}/combined_notes.md"
        loader = UnstructuredMarkdownLoader(markdown_path)
        data: List[Document] = loader.load()
        text: str = data[0].page_content
        return text
    
    # Chunk MD
    def _chunk(self, text: str) -> List[str]:
        pattern = r'\n\d+\.\d+\s'
        chunks = re.split(pattern, text)
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        return chunks
    # Store each chunk into a .txt file
    def _store(self, chunks: List[str]) -> None:
        os.makedirs(f"experiments/{self.folder}/chunks", exist_ok=True)
        n = len(chunks)
        for i in range(n):
            file: str = f"experiments/{self.folder}/chunks/chunk{i}.txt"
            text: str = chunks[i]
            with open(file, "w", encoding = "utf-8") as file:
                file.write(text)