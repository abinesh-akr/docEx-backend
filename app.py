import streamlit as st
import os
import cv2
import base64
import numpy as np
from pdf2image import convert_from_path
import pytesseract
from fastapi import FastAPI, File, UploadFile
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import threading
from aadhar import process_aadhar
from gate import process_gate
from income import process_income

# ✅ Ensure the uploads directory exists
os.makedirs("uploads", exist_ok=True)

# ✅ Initialize FastAPI
api = FastAPI()

# ✅ Enable CORS to allow React frontend to access the API
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Allow necessary HTTP methods
    allow_headers=["Content-Type", "Authorization"],  # Allow required headers
)

# ✅ Streamlit UI
st.title("📑 Document Extraction System")
st.write("Upload Aadhar, Income, or Gate documents to extract text and images.")

# ✅ Streamlit File Upload
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg"])

# ✅ Function to Process File
def process_uploaded_file(file_path, doc_type):
    """Process document based on type"""
    if doc_type == "Aadhar":
        return process_aadhar(file_path)
    elif doc_type == "Income":
        return process_income(file_path)
    elif doc_type == "Gate":
        return process_gate(file_path)

# ✅ FastAPI API for React Frontend
@api.post("/api/upload")
async def upload_file(file: UploadFile = File(...), doc_type: str = "Aadhar"):
    """API for React to send files and get extracted text"""
    file_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    extracted_text, output_images = process_uploaded_file(file_path, doc_type)

    # Convert images to base64 for API response
    images_base64 = []
    for img in output_images:
        img.seek(0)
        images_base64.append(base64.b64encode(img.read()).decode("utf-8"))

    return JSONResponse(content={"text": extracted_text, "images": images_base64, "filename": file.filename})

# ✅ Run FastAPI in a Separate Thread (Required for Streamlit Cloud)
def run_api():
    uvicorn.run(api, host="0.0.0.0", port=8502)

# ✅ Start FastAPI on a Separate Thread
threading.Thread(target=run_api, daemon=True).start()
