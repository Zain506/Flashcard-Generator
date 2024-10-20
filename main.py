import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shutil
import streamlit as st
from src import *
st.title("Simple Maths Revision Pipeline")
st.page_link("https://snip.mathpix.com/home", label = "MathPix")
pageID = st.text_input("Notion Page URL")
uploaded_file = st.file_uploader("Upload a Markdown", type="md")
sys = st.text_area("(Optional) System Instructions")
run = st.button("Run Pipeline...")
reset = st.button("Reset directories")

def extract_code_from_url(url: str):
    last_question_mark = url.rfind('?')
    code = url[last_question_mark - 32:last_question_mark]
    return code

def pipeline(base_path: str, pageID: str):
    """Runs full pipeline"""
    try:
        docIngest(base_path).run()
        st.success("Docs Ingested")
        mdCombine(base_path).run()
        getChunks(base_path).run()
        st.success("Extracting...Please Wait...")
        Extractor(base_path).run()
        st.success("Exporting to Notion...")
        Notion(base_path, pageID).run()
    except Exception as e:
        st.error(f"An error occurred during pipeline execution: {str(e)}")
        raise e  # Re-raise the exception to see the full error message

root_dir = os.path.dirname(os.path.join(os.path.abspath(__file__)))
# os.makedirs(experiments_dir)
# Create directories
os.makedirs(os.path.join(root_dir, "notes"), exist_ok=True)
os.makedirs(os.path.join(root_dir, "examples"), exist_ok=True)
os.makedirs(os.path.join(root_dir, "experiments", "tmp_file", "output"), exist_ok=True)

if reset:
    dirs: list[str] = ["examples", "experiments", "notes"]
    for file in dirs:
        if os.path.isdir(file):
            shutil.rmtree(file)
    st.write("## Reset!")
if run: # when button is pressed
    if uploaded_file is None:
        st.error("You forgot to upload a file")
    elif pageID is None:
        st.error("Please provide a link to a valid Notion page")
    else: # Start pipeline logic
        # Upload file
        with open(os.path.join(root_dir, "notes", "file.md"), "wb") as f:
            f.write(uploaded_file.getbuffer())
            st.success("File Saved")
        # Upload system instructions if there
        with open(os.path.join(root_dir, "examples", "prompt.txt"), "w") as file:
            if sys:
                file.write(sys)
            else:
                pass
        success_message: str = "System Message Saved" if sys else "Default System Message used"
        st.success(success_message)
        # Run pipeline(file, pageID)
        st.success("Starting pipeline")
        pipeline("tmp_file", extract_code_from_url(pageID))
        dirs: list[str] = ["examples", "experiments", "notes"]
        for file in dirs:
            if os.path.isdir(file):
                shutil.rmtree(file)
        st.success("## Process Complete")