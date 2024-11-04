import streamlit as st
import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from dotenv import load_dotenv


load_dotenv()
OpenAI_Key = os.getenv("OpenAI_Key")
os.environ["OPENAI_API_KEY"] = OpenAI_Key


DATA_DIR = './data'
PERSIST_DIR = "./storage"


if 'index' not in st.session_state:
    st.session_state.index = None
if 'file_path' not in st.session_state:
    st.session_state.file_path = None
if 'messages' not in st.session_state:
    st.session_state.messages = []


#------------------------PDF SAVE PART (FRONT_END)----------------------------

def save_uploaded_file(uploaded_file):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    file_path = os.path.join(DATA_DIR, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

#--------------------------------Styling Part----------------------------------

st.markdown(
    """
    <style>
        .user-message {
            background-color: #faeabe;
            color: black;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            text-align: left;
        }
        .bot-message {
            background-color: #fffaed;
            color: black;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            text-align: right;
        }
    </style>
    """,
    unsafe_allow_html=True
)

#--------------------Front_End Chat Part------------------------------------------------

def display_message(text, is_user):
    if is_user:
        return f"<div class='user-message'><strong>❓ You:</strong> {text}</div>"
    else:
        return f"<div class='bot-message'><strong>🤖 Bot:</strong> {text}</div>"
    



#-------------------- Function to rebuild or load the index (MODEL PART)-----------------

def rebuild_index():
    global index

    if not os.listdir(DATA_DIR):
        st.write("Data directory is empty. No files to index.")
        if os.path.exists(PERSIST_DIR):
            st.write("Loading index from persisted storage.")
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            try:
                st.session_state.index = load_index_from_storage(storage_context)
                st.write("Index successfully loaded from persisted storage.")
            except Exception as e:
                st.error(f"Failed to load index from storage: {e}")
        else:
            st.write("No index found in persisted storage.")
            st.session_state.index = None
    else:
        st.write("Data directory is not empty. Creating or loading the index.")
        if not os.path.exists(PERSIST_DIR):
            documents = SimpleDirectoryReader(DATA_DIR).load_data()
            st.session_state.index = VectorStoreIndex.from_documents(documents)
            st.session_state.index.storage_context.persist(persist_dir=PERSIST_DIR)
            st.write("Index created and persisted.")
        else:
            st.write("Attempting to load existing index from persisted storage.")
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            try:
                st.session_state.index = load_index_from_storage(storage_context)
                st.write("Index successfully loaded from storage.")
            except Exception as e:
                st.error(f"Error while loading index: {e}")


#--------------------------Function to query the CV using the loaded index (MODEL PART)-------------------

def query_cv(file_path, prompt):
    if not os.path.exists(file_path):
        raise FileNotFoundError("The specified CV file was not found.")

    if st.session_state.index is None:
        raise ValueError("Index has not been initialized. Please check the data directory or persisted storage.")

    query_engine = st.session_state.index.as_query_engine()
    response = query_engine.query(prompt)

    return str(response)

#---------------------------Front_End UI Components------------------------------------

st.title("CV Analysis Chatbot - Phase_01")


with st.sidebar:
    st.write("# Upload Your CV")
    uploaded_file = st.file_uploader("Upload CV (PDF)", type=["pdf"], label_visibility="collapsed")

    if st.button("Submit CV"):
        if uploaded_file is not None:
            file_path = save_uploaded_file(uploaded_file)
            st.session_state.file_path = file_path  
            st.success("CV submitted successfully!")
            rebuild_index()  

    st.markdown("<hr>", unsafe_allow_html=True)


    st.write("# Ask a Question")
    with st.form(key='question_form'):
        prompt = st.text_area("Ask your questions here:", placeholder="Enter your question....", key="prompt")
        submit_button = st.form_submit_button(label="Ask")

    if st.button("Clear Chat"):
        st.session_state.messages = []

st.write("### Chatbot Responses:")


if submit_button and prompt:
    if 'file_path' in st.session_state:  
        file_path = st.session_state.file_path
        try:
            chatbot_response = query_cv(file_path, prompt)

            st.session_state.messages.append(display_message(prompt, is_user=True))
            st.session_state.messages.append(display_message(chatbot_response, is_user=False))
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please upload a CV before asking questions.")

#------------------------------Display chat history------------------------------

if st.session_state.messages:
    for message in st.session_state.messages:
        st.markdown(message, unsafe_allow_html=True)
