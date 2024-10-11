"""Notion API toggle uploading class"""
from dotenv import load_dotenv
import os
from notion_client import Client
from typing import List
import json
import re
load_dotenv()

class Notion:
    """Add a toggle block to Notion page with a given ID"""
    def __init__(self, folder: str, pageID: str):
        self.folder = folder
        self.id = pageID
    def run(self):
        data: list[dict] = self._loadDict()
        for chunk in data:
            form: List[dict] = self._makeBlocks()
            for key, value in chunk.items():
                toggle: dict = self._template(key, value)
                form.append(toggle)
        # form is the list of blocks
        # self._setup(form)
            newform: List[List[dict]] = self._splitBlocks(form)
            for tmp in newform:
                self._setup(tmp)
    def _loadDict(self) -> list[dict]:
        myList: list[dict] = []
        for chunk in os.listdir(f"experiments/{self.folder}/output/"):
            myDict: dict = {}
            with open(f"experiments/{self.folder}/output/{chunk}", "r") as json_file:
                content = json_file.read()
                dictionary: str = json.loads(content)
                dictionary = dictionary.replace('\\', '\\\\')
                dictionary = json.loads(dictionary)
                for key, value in dictionary.items():
                    myDict[key] = value
                myList.append(myDict)
        return myList
    def _template(self, front: str, back: str) -> dict:
        back = back.replace("\\\\", "\\").replace("{{", "{").replace("}}", "}")
        chars: list[str] = re.split(r'(\$\$.*?\$\$)', back)
        text = {
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"type": "text", "text": {"content": front}}],
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": []
                            }
                        }
                    ]
                }
            }
        for char in chars:
            # print(char)
            try:
                if char[0] == "$" and len(char) > 4:
                    text["toggle"]["children"][0]["paragraph"]["rich_text"].append(
                        {"type": "equation", "equation": {"expression": char[2:-2]}}
                    )
                else:
                    text["toggle"]["children"][0]["paragraph"]["rich_text"].append(
                        {"type": "text", "text": {"content": char}}
                    )
            except:
                continue
        return text
        
    def _makeBlocks(self) -> List[dict]:
        """Create initial list to add to Notion blocks"""
        return []
    def _splitBlocks(self, blocks: List[dict], max_length: int = 99) -> List[List[dict]]:
        """If there are more than 100 blocks in list, split"""
        return [blocks[i:i + max_length] for i in range(0, len(blocks), max_length)]
    def _setup(self, blocks: List[dict]):
        """Make API call to Notion"""
        NOTION_TOKEN = os.getenv("NOTION_TOKEN")
        notion = Client(auth=NOTION_TOKEN)
        notion.blocks.children.append(
        block_id=self.id,
        children=blocks
    )