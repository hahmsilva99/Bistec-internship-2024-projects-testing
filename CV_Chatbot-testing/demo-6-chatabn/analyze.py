import streamlit as st
import requests
import os

DATA_DIR = './data'

def save_uploaded_file(uploaded_file):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    file_path = os.path.join(DATA_DIR, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path


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
        .sidebar-upload-section {
            background-color: #d1e7dd;
            padding: 5px; 
            border-radius: 10px;
            margin-bottom: 5px;
            margin-top: 2px; 
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

def display_message(text, is_user):
    if is_user:
        return f"<div class='user-message'><strong>❓ You:</strong> {text}</div>"
    else:
        return f"<div class='bot-message'><strong>🤖 Bot:</strong> {text}</div>"

st.title("CV Analysis Chatbot - Phase_01")

# Sidebar for CV upload
with st.sidebar:
    st.write("#### Upload Your CVs", key="upload")
    
    # Allow multiple file uploads
    uploaded_files = st.file_uploader("#### Upload CVs (PDF)", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed", key="upfile")

    # Submit button
    if st.button("Submit CVs", key="sub"):
        if uploaded_files:
            file_paths = []
            
            # Process each uploaded file
            for uploaded_file in uploaded_files:
                file_path = save_uploaded_file(uploaded_file)
                file_paths.append(file_path)
            
            # Save all file paths to session state
            st.session_state.file_paths = file_paths
            st.success("All CVs submitted successfully!")
        else:
            st.warning("Please upload at least one CV.")

    st.markdown("<hr>", unsafe_allow_html=True)

# Main Section for Chatbot Responses and Question Input
st.write("### Chatbot Responses:")

# Display chat history
if st.session_state.messages:
    for message in st.session_state.messages:
        st.markdown(message, unsafe_allow_html=True)  

# Form for question input in the main section
st.write("### Ask a Question")
with st.form(key='question_form'):
    prompt = st.text_area("Ask your questions here:", placeholder="Enter your question....", key="prompt")
    submit_button = st.form_submit_button(label="Ask")

# Handle form submission
if submit_button and prompt:
    if 'file_paths' in st.session_state:  
        file_paths = st.session_state.file_paths
        response = requests.post("http://127.0.0.1:8000/api/data_handle", json={"file_paths": file_paths, "prompt": prompt})

        if response.status_code == 200:
            data = response.json()
            chatbot_response = data['message']

            st.session_state.messages.append(display_message(prompt, is_user=True))
            st.session_state.messages.append(display_message(chatbot_response, is_user=False))
        else:
            st.error("Error fetching response from backend.")
    else:
        st.warning("Please upload a CV before asking questions.")

# Clear Chat button under the Ask Question section
if st.button("Clear Chat"):
    st.session_state.messages = []
