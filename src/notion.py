"""Notion API toggle uploading class"""
import json
from dotenv import load_dotenv
import os
from notion_client import Client
from typing import List
load_dotenv()

class Notion:
    """Add a toggle block to Notion page with a given ID"""
    def __init__(self, folder: str, pageID: str):
        self.folder = folder
        self.id = pageID
    def run(self):
        data: dict = self._loadDict()
        form: List[dict] = self._makeBlocks()
        for key, value in data.items():
            toggle: dict = self._template(key, value)
            form.append(toggle)
        self._setup(form)
    def _loadDict(self) -> dict:
        with open(f"experiments/{self.folder}/output.json", "r") as json_file:
            data = json.load(json_file)
        return data
    def _template(self, front: str, back: str):
        return {
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"type": "text", "text": {"content": front}}],
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": back}}]
                            }
                        }
                    ]
                }
            }
    def _makeBlocks(self) -> List[dict]:
        """Parse input to create Notion blocks"""
        new_blocks = []
        
        return new_blocks
    def _setup(self, blocks: List[dict]):
        """Make API call to Notion"""
        NOTION_TOKEN = os.getenv("NOTION_TOKEN")
        notion = Client(auth=NOTION_TOKEN)
        notion.blocks.children.append(
        block_id=self.id,
        children=blocks
    )
