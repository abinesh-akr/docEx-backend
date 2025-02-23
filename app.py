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
import requests
# ✅ Ensure the uploads directory exists
os.makedirs("uploads", exist_ok=True)

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
if uploaded_file:
    file_path = os.path.join("uploads", uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ File saved: {file_path}")

    # Select Document Type
    option = st.radio("Select Document Type", ["Aadhar", "Income", "Gate"])

    # Process File
    extracted_text, output_images = process_uploaded_file(file_path, option)

    # ✅ Display Extracted Text
    st.subheader("📄 Extracted Text:")
    st.write(extracted_text)

    # ✅ Display Processed Images
    st.subheader("📸 Processed Images:")
    for img in output_images:
        img.seek(0)
        img_base64 = base64.b64encode(img.read()).decode("utf-8")
        st.image(f"data:image/png;base64,{img_base64}", caption="Processed Image", use_column_width=True)
    
    api_response = requests.post("https://docex-backend-api.onrender.com/api/return", json={
        "text": extracted_text,
        "image": img_base64
    })
    if api_response.status_code == 200:
        st.success("✅ Successfully processed!")
    else:
        st.error("❌ Failed to send results to FastAPI")


