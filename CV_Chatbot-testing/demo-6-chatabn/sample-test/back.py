from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import pdfplumber
import openai
import os
from typing import List

# Initialize FastAPI app
app = FastAPI()

# Directory to store uploaded CVs
DATA_DIR = './data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure this environment variable is set

# Data model for request
class ChatRequest(BaseModel):
    file_paths: List[str]
    chat_history: List[dict]

# Extract text from PDF
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

# Function to generate response using OpenAI
def generate_response(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for analyzing CVs."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm sorry, there was an error processing your request."

# Endpoint to handle CVs and chat history
@app.post("/api/data_handle")
async def handle_data(request: ChatRequest):
    # Read all CVs and create a combined text for processing
    combined_text = ""
    for file_path in request.file_paths:
        combined_text += extract_text_from_pdf(file_path) + "\n"

    # Prepare prompt based on chat history and combined CV text
    chat_prompt = f"Here is the combined CV data:\n{combined_text}\n"
    for message in request.chat_history:
        if message["role"] == "user":
            chat_prompt += f"\nUser: {message['message']}"
        elif message["role"] == "bot":
            chat_prompt += f"\nBot: {message['message']}"

    # Generate a response based on the prompt
    chatbot_response = generate_response(chat_prompt)
    return {"message": chatbot_response}

# Endpoint to upload CVs
@app.post("/upload_cv/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(DATA_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"file_path": file_path}
