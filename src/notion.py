import re
import json
from dotenv import load_dotenv
import os
from notion_client import Client
import copy
class Notion:
    """Transfer the text directly from the .yaml files to Notion"""
    def __init__(self, folder: str, pageID: str):
        self.folder = folder
        self.id = pageID
    
    def run(self):
        for chunk in os.listdir(f"experiments/{self.folder}/output/"):
            print(f"Processing {chunk}")
            path = f"experiments/{self.folder}/output/{chunk}"
            data: dict = self._loadInfo(path) # list of extracted data from .txt
            myDicts: list[dict] = self._template(data)
            splitDicts: list[list[dict]] = self._splitBlocks(myDicts)
            self._call(splitDicts)
    
    def _loadInfo(self, filepath: str) -> dict:
        """Given 1 .txt file, perform regex to extract text"""
        with open(filepath) as file:
            info = json.load(file)
            return info
    def _dictToList(self, myDict: dict) -> list[str]:
        """Plug loadInfo into template function"""
        myList: list[str] = []
        for key, value in myDict.items():
            myList.append(key)
            myList.append(value)
        
        return myList
    def _template(self, entities: dict) -> list[dict]: # entities: list[str] is a list with alternating between front and back
        """Parse text as equation and place into JSON format"""
        myDicts: list[dict] = []
        def __split(text) -> list[str]:
            pattern = r'\$([^$]*)\$|([^$]+)'
            return [match.group(1) or match.group(2) for match in re.finditer(pattern, text)]
        # Front: block["toggle"]["rich_text"]
        # Back: block["toggle"]["children"][0]["paragraph"]["rich_text"]
        __toLatex = lambda char: {"type": "equation", "equation": {"expression": char}}
        __toText = lambda char: {"type": "text", "text": {"content": char}}
        for key, value in entities.items():
            key: list[str] = __split(key)
            value: list[str] = __split(value)
            block = {
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [__toText(item) if (i % 2 == 0 if key[0] != "$" else i % 2 == 1) else __toLatex(item) for i, item in enumerate(key)], # Front of flashcard is appended to rich_text
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [__toText(item) if (i % 2 == 0 if value[0] != "$" else i % 2 == 1) else __toLatex(item) for i, item in enumerate(value)] # Back of flashcard is appended to rich_text list
                            }
                        }
                    ]
                }
            }
            myDicts.append(block)
        
        return myDicts
    def _splitBlocks(self, blocks: list[dict], max_length: int = 99) -> list[list[dict]]:
        """If there are more than 100 blocks in list, split"""
        return [blocks[i:i + max_length] for i in range(0, len(blocks), max_length)]

    def _call(self, blocks: list[list[dict]]):
        """Make API call to Notion"""
        for block in blocks:
            load_dotenv()
            NOTION_TOKEN = os.getenv("NOTION_TOKEN")
            notion = Client(auth=NOTION_TOKEN)
            notion.blocks.children.append(
            block_id=self.id,
            children=block
            )