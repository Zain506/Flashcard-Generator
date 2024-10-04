"""
User-friendly way to import and organise respective files.
Allows for clean document upload and proper experimentation by automatically loading into new folder
"""

import shutil
class docIngest:
    """
    In the local directory we will have /notes and /questions
    We load them in and store them into the experiments folder
    """
    def __init__(self, folder: str):
        self.folder = folder
    def run(self) -> None:
        """
        Run complete process
        """
        self._notesLoad()
    def _notesLoad(self):
        src_dir = 'notes'
        dst_dir = f"experiments/{self.folder}/notes"
        q_dir = "questions"
        dst_dir2 = f"experiments/{self.folder}/questions"
        shutil.copytree(src_dir, dst_dir)
        shutil.copytree(q_dir, dst_dir2)