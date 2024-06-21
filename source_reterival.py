from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader
import os

# def load_pdf_excluding_pages(pdf_path, pages_to_skip):
#     loader = PyPDFLoader(pdf_path)
#     all_pages = loader.load_and_split()
#     filtered_pages = [page for i, page in enumerate(all_pages) if i not in pages_to_skip]
#     return filtered_pages

def parse_page_skip(pages_to_skip_input):
    # Parse pages_to_skip_input string (st.text_box) into a list of ranges
    pages_to_skip = []
    parts = pages_to_skip_input.split(',')
    for part in parts:
        part = part.strip()
        if part:  # Check if part is not empty
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages_to_skip.append((start, end))
            else:
                page = int(part)
                pages_to_skip.append(page)
    return pages_to_skip

def load_pdf_excluding_pages(pdf_path, pages_to_skip):
    # Load the PDF file
    loader = PyPDFLoader(pdf_path)
    all_pages = loader.load_and_split()
    pages_to_skip_list = parse_page_skip(pages_to_skip)
    # Create a set of pages to skip for faster lookup
    skip_pages_set = set()
    for item in pages_to_skip_list:
        if isinstance(item, tuple):
            skip_pages_set.update(range(item[0] - 1, item[1]))  # Convert to 0-indexed
        else:
            skip_pages_set.add(item - 1)  # Convert to 0-indexed
    # Filter pages
    filtered_pages = [page for i, page in enumerate(all_pages) if i not in skip_pages_set]
    return filtered_pages

def initialize_retriever(embeddings_model_name, child_chunk_size, parent_chunk_size, cache_dir=None):
    # Set cache directory if specified
    if cache_dir:
        os.environ['TRANSFORMERS_CACHE'] = cache_dir
    
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=child_chunk_size)
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=parent_chunk_size)
    vectorstore = Chroma(collection_name="split_parents", embedding_function=embeddings)
    store = InMemoryStore()
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )
    return retriever

def add_documents_to_retriever(retriever, documents):
    retriever.add_documents(documents)

def get_relevant_documents(retriever, query, top_k=1):
    retrieved_docs = retriever.invoke(query)
    return retrieved_docs[:top_k]
    

def get_relevant_sources(filtered_pages, user_query):
    cache_dir = "./huggingface_cache"  # Specify the cache directory

    retriever = initialize_retriever(
        embeddings_model_name="all-MiniLM-L6-v2",
        child_chunk_size=400,
        parent_chunk_size=2000,
        cache_dir=cache_dir
    )
    add_documents_to_retriever(retriever, filtered_pages)
    relevant_docs = get_relevant_documents(retriever, user_query)

    most_relevant_doc = relevant_docs[0]
    
    return len(most_relevant_doc.page_content), most_relevant_doc.page_content

pdf_path = "raw_data/History_of_India_2nd_ed.pdf"
pages_to_skip = "1-3, 5, 7-10"
query = "rajasthan"
pages_filtered = load_pdf_excluding_pages(pdf_path, pages_to_skip)
print("pdf loaded")
print(pages_filtered[0])
print("gets sources")
user_query = "rajasthan"
top_doc_len, top_doc = get_relevant_sources(pages_filtered, user_query)
print("reterival")
print(top_doc_len)
print(top_doc)



