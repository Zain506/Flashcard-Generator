import re
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
            data: list[str] = self._loadInfo(path) # list of extracted data from .txt
            myDicts: list[dict] = self._template(data)
            splitDicts: list[list[dict]] = self._splitBlocks(myDicts)
            self._call(splitDicts)
    
    def _loadInfo(self, filepath: str) -> list[str]:
        """Given 1 .txt file, perform regex to extract text"""
        result: list[str] = []
        with open(filepath) as file:
            text = file.read()
            pattern = r'"((?:[^"\\]|\\.)*)"'
            matches: list[str] = re.findall(pattern, text)
            for match in matches:
                result.append(match.replace("\\\\", "\\"))
            return result
    
    def _template(self, entities: list[str]) -> list[dict]: # entities: list[str] is a list with alternating between front and back
        """Parse text as equation and place into JSON format"""
        text = {
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [], # Front of flashcard is appended to rich_text
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [] # Back of flashcard is appended to rich_text list
                            }
                        }
                    ]
                }
            }
        result: list[dict] = []
        def __sort(text: dict, chars: str, back: bool) -> dict: # Adds singular entity to notion JSON object
            """Function for singular entity"""
            # Turn chars into list[str] separated by whether contains $$ or not
            chars: list[str] = re.split(r'(\$\$.*?\$\$)', chars)
            if back:
                position = text["toggle"]["children"][0]["paragraph"]["rich_text"]
            else:
                position = text["toggle"]["rich_text"]
            for char in chars:
                if "$" in char and len(char) > 4: # Equation
                    char = char.strip()
                    char = char[2:-2]
                    char = char.strip()
                    if char == "":
                        continue
                    position.append({"type": "equation", "equation": {"expression": char}})
                else: # Text
                    position.append({"type": "text", "text": {"content": char}})
            return text 
        for index in range(0, len(entities), 2):
            card = copy.deepcopy(text)
            card = __sort(card, entities[index], back = False)
            if index + 1 < len(entities):
                card = __sort(card, entities[index + 1], back = True)
            result.append(card)
        return result
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