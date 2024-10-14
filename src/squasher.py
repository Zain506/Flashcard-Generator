import os
import json
class Squasher:
    """Combine JSON output from 3 .json files in 'output' folder into 1"""
    def __init__(self, folder: str):
        self.folder = folder
    def run(self):
        myDict = self._loadJsons()
        self._toJson(myDict)
    def _loadJsons(self) -> dict:
        myDict: dict = {}
        for file in os.listdir(f"experiments/{self.folder}/output/"):
            with open(f"experiments/{self.folder}/output/{file}", "r") as json_file:
                content = json_file.read()
                dictionary: str = json.loads(content)
                dictionary = dictionary.replace('\\', '\\\\')
                dictionary = json.loads(dictionary)
                for key, value in dictionary.items():
                    myDict[key] = value
        # print(json.dumps(myDict, indent = 4))
        return myDict
    def _toJson(self, myDict: dict) -> None:
        """Load dictionary to JSON"""
        with open(f"experiments/{self.folder}/output.txt", "w") as file:
            json.dump(myDict, file, indent = 4)