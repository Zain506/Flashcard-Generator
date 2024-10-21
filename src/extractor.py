from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
import os
import json
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
class Extractor:
    """New Extractor: Searches FAISS DB and constructs message"""
    def __init__(self, folder):
        self.folder = folder
    def run(self):
        db = self._getDB()
        prompt = self._getPrompt()
        resp = self._chain(prompt, db)
        self._storeResp(resp)
    # Load FAISS DB
    def _getDB(self):
        embeddings = OpenAIEmbeddings(
            model = "text-embedding-3-small"
            )
        new_df = FAISS.load_local(
            f"experiments/{self.folder}/faiss_db", 
            embeddings = embeddings, 
            allow_dangerous_deserialization = True
            )
        return new_df.as_retriever()
    # Load Prompt message (for what to create flashcard of)
    def _getPrompt(self):
        """Load prompt from prompt.txt file"""
        with open(f"experiments/{self.folder}/examples/prompt.txt", "r") as f:
            content = f.read()
            return content
    # Construct system and message prompts to query
    def _chain(self, prompt: str, db):
        plate: str = """
Answer the question based only on the following context:

{context}

Format your response as a flashcard (Q&A style)

Provide the response in JSON format, where the front of the card is the key (i.e. the question Q&A revision style) and the back is the value (i.e. the answer Q&A Revision Style)

Ensure the back AND the front of the cards (i.e. all key-value pairs) are strings. NOT lists, dictionaries, integers or any other data type

Where there is LaTeX mathematical notation, use the syntax from the markdown text and enclose it in $ symbols.

For example: "We define a probability space $(\\Omega, \\mathcal F, \\mathbb P)$

Question: {question}

Answer:
"""
        template = ChatPromptTemplate.from_template(plate)
        llm = ChatOpenAI(model_name = "gpt-4o-mini", temperature = 0, model_kwargs={"response_format": {"type": "json_object"}})
        chain = (
            {"context": db, "question": RunnablePassthrough()}
            | template
            | llm
            | StrOutputParser()
        )
        response = chain.invoke(prompt)
        return response
    # Store as .txt in /self.folder/output
    def _storeResp(self, content: str):
        os.makedirs(f"experiments/{self.folder}/output")
        with open(f"experiments/{self.folder}/output/response.json", "w") as file:
            json.dump(json.loads(content), file, indent = 4)