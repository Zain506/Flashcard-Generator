from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from typing import List
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
class getChunks:
    """
    Get a LLM to extract useful info in dictionary format (flashcards)
    """
    def __init__(self, file:str):
        self.folder = file

    def run(self):
        text: str = self._loadMD()
        chunks: List[Document] = self._chunk(text)
        self._toVecDB(chunks)
    
    def _loadMD(self) -> str:
        markdown_path = f"experiments/{self.folder}/combined_notes.md"
        loader = UnstructuredMarkdownLoader(markdown_path)
        data: List[Document] = loader.load()
        text: str = data[0].page_content
        return text
    
    # Chunk MD
    def _chunk(self, text: str) -> List[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 20000,
            chunk_overlap = 2000,
        )
        chunks: List[Document] = text_splitter.create_documents([text])
        return chunks
    
    def _toVecDB(self, text: List[Document]):
        """Store as FAISS DB"""
        embeddings = OpenAIEmbeddings(
            model = "text-embedding-3-small"
            )
        db = FAISS.from_documents(text, embeddings)
        db.save_local(f"experiments/{self.folder}/faiss_db")