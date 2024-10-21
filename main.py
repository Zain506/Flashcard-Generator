import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shutil
import streamlit as st
from src import *
st.title("Simple Maths Revision Pipeline")
st.page_link("https://snip.mathpix.com/home", label = "Click here to go to MathPix")

uploaded_file = st.file_uploader("Upload a Markdown", type="md")
reset = st.button("Reset")
if reset:
    dirs: list[str] = ["examples", "experiments", "notes"]
    for file in dirs:
        if os.path.isdir(file):
            shutil.rmtree(file)
    st.write("## Reset!")

base_path: str = "tmp"

def extract_code_from_url(url: str):
    last_question_mark = url.rfind('?')
    code = url[last_question_mark - 32:last_question_mark]
    return code

root_dir = os.path.dirname(os.path.join(os.path.abspath(__file__)))
# os.makedirs(experiments_dir)
# Create directories
def clean(dir: str):
    if os.path.exists(os.path.join(root_dir, dir)):
        shutil.rmtree(os.path.join(root_dir, dir))
    os.makedirs(os.path.join(root_dir, dir))

clean("notes")
clean("examples")
clean("experiments")



if uploaded_file:
    with open(os.path.join(root_dir, "notes", "file.md"), "wb") as f:
        f.write(uploaded_file.getbuffer())
    docIngest(base_path).run()
    mdCombine(base_path).run()
    getChunks(base_path).run()
    st.success("File successfully uploaded")
    pageID = st.text_input("Notion Page URL")
    question = st.text_area("Query")
    if pageID and question:
        with open(os.path.join(root_dir, "experiments", base_path, "examples", "prompt.txt"), "w") as file:
            file.write(question)
        run = st.button("Run")
        
        if run: # Run pipeline when button pressed
            code = extract_code_from_url(pageID)
            Extractor(base_path).run()
            with open(f"experiments/{base_path}/output/response.json", "r") as file:
                st.write(json.dumps(file, indent = 4))
            Notion(base_path, code).run()
            dirs: list[str] = ["examples", "experiments", "notes"]
            for file in dirs:
                if os.path.isdir(file):
                    shutil.rmtree(file)
            st.write("## Process Complete")
