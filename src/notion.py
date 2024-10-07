"""Notion API toggle uploading class"""

from dotenv import load_dotenv
import os
from notion_client import Client

load_dotenv()

class Notion:
    """Add a toggle block to Notion page with a given ID"""
    def __init__(self, front: str, back: str, pageID: str):
        self.front = front
        self.back = back
        self.id = pageID
    def run(self):
        blocks: list = self.makeBlocks()
        self.setup(blocks)
    def makeBlocks(self) -> list:
        """Parse input to create Notion blocks"""
        new_blocks = [
            {
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"type": "text", "text": {"content": self.front}}],
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": self.back}}]
                            }
                        }
                    ]
                }
            }
        ]
        return new_blocks
    def setup(self, blocks: list):
        """Make API call to Notion"""
        NOTION_TOKEN = os.getenv("NOTION_TOKEN")
        notion = Client(auth=NOTION_TOKEN)
        notion.blocks.children.append(
        block_id=self.id,
        children=blocks
    )
