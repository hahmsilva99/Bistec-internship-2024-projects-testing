import streamlit as st

# 1. Initialize session state for the file path
if 'file_path' not in st.session_state:
    st.session_state['file_path'] = None  # Initialize with None if file path is not in session state

# 2. File uploader
uploaded_file = st.file_uploader("Upload your CV", type="pdf")

if uploaded_file is not None:
    # Save the uploaded file path to session state
    st.session_state['file_path'] = uploaded_file.name  # Save just the file name for simplicity

# 3. Show the uploaded file path
if st.session_state['file_path']:
    st.write(f"Uploaded file: {st.session_state['file_path']}")
else:
    st.write("No file uploaded yet.")
