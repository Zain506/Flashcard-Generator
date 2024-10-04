import os
class mdCombine:
    """
    Convert several .md files into 1 .md file within the {self.folder}/notes folder
    """
    def __init__(self, folder: str):
        self.folder = folder
    
    def run(self) -> None:
        """
        Run entire pipeline
        """
        self._tmp()
    def _tmp(self):
        md_files = [f for f in os.listdir(f"experiments/{self.folder}/notes") if f.endswith('.md')]
        print(md_files)
        combined_content = ""

        for file in md_files:
            with open("experiments/" + self.folder + "/notes/" + file, 'r', encoding='utf-8') as f:
                combined_content += f.read() + "\n\n"
        
        with open(f"experiments/{self.folder}/combined_notes.md", 'w', encoding='utf-8') as f:
            f.write(combined_content)