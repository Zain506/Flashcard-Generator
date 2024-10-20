import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "OpenAIApp"

class Extractor:
    """Given example text and extraction, query all chunks of text and collect as JSON. Store in experiments folder"""
    def __init__(self, folder: str):
        self.folder = folder
    def run(self):
        sys: str = self._createPrompt()
        num: int = self._getLenChunks()
        for i in range(num):
            text: str = self._readChunk(i)
            response: dict = self._queryLang(sys, text)
            response = self._parseText(response)
            self._storeText(response, f"chunk{i}.txt")

    def _createPrompt(self) -> str:
        """Use list of 2 texts to form system message"""
        # Search to find prompt.txt - if not there, then return the standard examples prompt
        file_path: str = f"experiments/{self.folder}/examples/prompt.txt"
        # prompt.txt must ask for a JSON-formatted response
        content: str = """
        Using the provided information in the user message, create flashcards for a student trying to learn this topic.

        Provide the solution in JSON format, where the front of the card is the key (i.e. the question) and the back is the value (i.e. the answer)

        Ensure the back AND the front of the cards (i.e. all key-value pairs) are strings. NOT lists, dictionaries, integers or any other data type

        Where there is LaTeX mathematical notation, use the syntax from the markdown text and enclose it in $ symbols.

        For example: "We define a probability space $(\\Omega, \\mathcal F, \\mathbb P)$"
        """
        with open(file_path, 'r') as file:
            prompt = file.read()
            if prompt:
                return prompt + content
        
        return content
    
    def _getLenChunks(self) -> int:
        """Return how many times to read chunks"""
        return len(os.listdir(f"experiments/{self.folder}/chunks/"))
    
    def _readChunk(self, chunk: int) -> str:
        """Read in chunk of text"""
        with open(f"experiments/{self.folder}/chunks/chunk{chunk}.txt", "r", encoding = "utf-8") as file:
            content = file.read()
            return content
    
    def _queryLang(self, sys: str, user: str) -> str:
        """Query Langchain and return json of response"""
        # print(sys)
        # print(type(user))
        llm = ChatOpenAI(model = "gpt-4o-mini")
        md: str = rf"""{sys}"""
        md = json.dumps(md.replace("$", "$$"), indent = 4) # replace("{", "{{").replace("}", "}}").
        usermd: str = rf"""{user}"""
        usermd = json.dumps(usermd.replace("$", "$$"), indent = 4) # .replace("{", "{{").replace("}", "}}")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", md),
                ("user", "{input}")
            ]
        )
        chain = prompt|llm # combines both
        response = chain.invoke({"input": usermd})
        return response.content
    
    def _parseText(self, myDict: str) -> dict:
        """Where the text values contain escape characters, remove and fix"""
        return myDict.replace("\\(", "$$").replace("\\)", "$$")# replace("\\\\", "\\").
    
    def _storeText(self, text: str, filename: str) -> None:
        """Temporarily store as text"""
        os.makedirs(f"experiments/{self.folder}/output/", exist_ok = True)
        with open(f"experiments/{self.folder}/output/{filename}", "w", encoding="utf-8") as file:
            start = text.index("{")
            end = text.rindex("}") + 1
            data = text[start:end]
            file.write(data)