import streamlit as st
# import openai
from PyPDF2 import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from source_reterival import load_pdf_excluding_pages, get_relevant_sources 
import io
import tempfile
# import langchain

# Define your retrieval and generation functions
def retrieve_from_pdf(pdf_content, user_input):
    # Placeholder for your retrieval function
    return "Extracted content from PDF"

def generate_response(query, openai_key):
    # Placeholder for your generation function
    # openai.api_key = openai_key
    # response = openai.Completion.create(
    #     engine="davinci",
    #     prompt=query,
    #     max_tokens=150
    # )
    # return response.choices[0].text.strip()
    return "hello"

# Initialize session state for storing chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Title of the app
st.title("RAG-based Chat Application")

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
    filtered_pdf = load_pdf_excluding_pages(tmp_file_path, pages_to_skip_input)
    st.session_state.pdf_content = filtered_pdf
    st.success("PDF content loaded successfully!")


# Feature 2: Input OpenAI Key
st.header("Enter Your OpenAI Key")
openai_key = st.text_input("OpenAI Key", type="password")

# Feature 3: Chat Interface
st.header("Chat Interface")

if "pdf_content" in st.session_state:
    st.write("PDF Content Loaded. You can now ask questions based on this content.")
    user_input = st.text_input("Your message", key="user_input")
    
    if st.button("Send"):
        if user_input and openai_key:
            pdf_content = st.session_state.pdf_content
            relevant_sources = get_relevant_sources(pdf_content, user_input)
            query = f"Based on the following content: {relevant_sources} \n\n {user_input}"
            response = generate_response(query, openai_key)
            st.session_state.messages.append((user_input, response))
        else:
            st.error("Please provide both your message and OpenAI key.")

# Display chat history
if st.session_state.messages:
    st.header("Chat History")
    for user_msg, bot_msg in st.session_state.messages:
        st.write(f"You: {user_msg}")
        st.write(f"Bot: {bot_msg}")

