import streamlit as st
import io
import tempfile
from PyPDF2 import PdfReader
from langchain.document_loaders import PyPDFLoader

def load_pdf_excluding_pages(pdf_path, pages_to_skip):
    # Load the PDF file
    loader = PyPDFLoader(pdf_path)
    all_pages = loader.load_and_split()
    
    # Create a set of pages to skip for faster lookup
    skip_pages_set = set()
    for item in pages_to_skip:
        if isinstance(item, tuple):
            skip_pages_set.update(range(item[0] - 1, item[1]))  # Convert to 0-indexed
        else:
            skip_pages_set.add(item - 1)  # Convert to 0-indexed
    
    # Filter pages
    filtered_pages = [page for i, page in enumerate(all_pages) if i not in skip_pages_set]
    
    return filtered_pages[0]

# Streamlit UI for uploading PDF and specifying pages to skip
st.header("Upload a PDF")
pdf_file = st.file_uploader("Choose a PDF file", type="pdf")

pages_to_skip_input = st.text_input("Enter pages to skip (e.g., 1-3, 5, 7-10)")

if pdf_file is not None:
    
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(pdf_file.read())
        tmp_file_path = tmp_file.name
    
    # Load and process the PDF
    text_content = load_pdf_excluding_pages(tmp_file_path, pages_to_skip_input)
    st.session_state.pdf_content = text_content
    print(st.session_state.pdf_content)
    st.success("PDF content loaded successfully!")
